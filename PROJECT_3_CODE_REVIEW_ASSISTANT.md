# Project 3: AI-Powered Code Review Assistant

## Overview
A GitHub App that analyzes pull requests, provides contextual code review comments (bugs, performance, security, style), suggests fixes with diffs, estimates blast radius of changes, and tracks fix adoption rate. Processes repos up to 100k LOC, handles incremental reviews on subsequent commits, respects `.reviewignore`, and maintains review history for learning. Designed for teams shipping 50+ PRs/week.

## Architecture
- **Frontend**: Next.js 14 App Router with GitHub OAuth, displays review dashboard + metrics
- **API**: Node.js + Fastify, Webhooks from GitHub, REST endpoints for manual triggers
- **Database**: Postgres (Supabase) with Prisma, stores reviews, findings, code embeddings
- **Storage**: Supabase Storage for cached AST snapshots, S3-compatible
- **Queue**: BullMQ + Redis for async PR analysis (5-15 min per large PR)
- **AI**: Claude Sonnet 3.5 for code analysis (200k context), OpenAI o1-preview for security-critical deep dives, Voyage Code embeddings for semantic code search
- **AST Parsing**: tree-sitter for multi-language support (TS, Python, Go, Rust)
- **Observability**: OpenTelemetry with custom spans for each analysis stage

## Key Engineering Concerns
- **Incremental Analysis**: Store file hashes, only re-analyze changed files on force-push, skip vendored/generated code
- **Idempotency**: Dedupe on `(pr_number, commit_sha)` composite key, skip duplicate webhooks
- **Backpressure**: Queue with concurrency limit (3 PRs in parallel), priority for small PRs (<500 LOC)
- **Partial Failures**: If AST parsing fails for one file, log error but continue reviewing other files
- **Schema Migrations**: Prisma migrations with constraint checks (foreign keys, enums)
- **Pagination**: Cursor-based on `(repo_id, created_at desc, id)` for review history
- **Rate Limiting**: GitHub API (5000/hr), cache repo metadata in Redis (1hr TTL), AI providers (tier limits)
- **Security**: Validate GitHub webhook signatures (HMAC-SHA256), sandbox code execution for test generation

## AI System Details
- **Analysis Pipeline**:
  1. Fetch diff from GitHub API
  2. Parse changed files with tree-sitter, extract functions/classes
  3. Retrieve similar code patterns from vector DB (embedding cache)
  4. Send to Claude with prompt: "Review for bugs, security (OWASP), performance (O(n²) loops, unnecessary allocations), style (idiomatic patterns)"
  5. Parse structured output (JSON schema: `{findings: [{type, severity, line, message, suggested_fix}]}`)
  6. Estimate blast radius: count usages of modified functions in codebase (semantic search)
- **Fix Suggestions**: Generate unified diff for each finding, post as GitHub suggestion (reviewable in UI)
- **Learning Loop**: Track which suggestions get accepted (via commit SHA matching), fine-tune prompts based on acceptance rate
- **Evals**: Golden dataset of 100 PRs with human-labeled issues, measure detection precision/recall (target F1 > 0.75), false-positive rate (<20%), fix acceptance rate (>50%)
- **Latency Target**: p95 < 10s for <200 LOC PRs, < 5 min for <1000 LOC
- **Cost Target**: <$0.50 per PR review (Sonnet 3.5), <$2.00 for deep security review (o1-preview, optional)

## Prompts for Claude Code Pairing

### a) Scaffold
```
Create Turborepo monorepo:
- apps/web: Next.js 14 App Router, TypeScript, NextAuth.js (GitHub provider), Tailwind, shadcn/ui
- apps/api: Node.js + Fastify + TypeScript, @octokit/webhooks for GitHub events
- packages/db: Prisma with Postgres, pgvector extension for code embeddings
- packages/analyzer: tree-sitter bindings (tree-sitter, tree-sitter-typescript, tree-sitter-python)
- packages/shared: Zod schemas for Review, Finding, BlastRadius
- Root .eslintrc (extends next, prettier), turbo.json with pipeline caching
- Dockerfiles: multi-stage for api (node:20-slim) and web
- docker-compose.yml: postgres, redis, ngrok for local webhook testing
```

### b) Contracts
```
Write OpenAPI 3.1 spec (openapi.yaml):
- POST /webhooks/github (handle pull_request events: opened, synchronize)
- POST /repos/{owner}/{repo}/prs/{number}/review (manual trigger)
- GET /repos/{owner}/{repo}/reviews (cursor pagination)
- GET /reviews/{id} (findings, blast radius, status)
- POST /reviews/{id}/findings/{finding_id}/feedback (accept/reject)
Use openapi-typescript to generate types in packages/shared.
Create GraphQL schema (schema.graphql) for subscriptions:
- reviewStatusChanged(prNumber: Int!): Review (WebSocket updates)
Generate Apollo Client hooks for web app.
```

### c) Data
```
Design Prisma schema:
- Repository: id, full_name, github_id, installation_id, default_branch
- PullRequest: id, repo_id, number, title, head_sha, base_sha, author, loc_added, loc_removed
- Review: id, pr_id, status enum (pending, analyzing, completed, failed), started_at, completed_at
- Finding: id, review_id, type enum (bug, security, performance, style), severity enum (low, medium, high, critical), file_path, line_start, line_end, message, suggested_fix text, accepted boolean
- CodeEmbedding: id, repo_id, file_path, function_name, embedding vector(512), last_updated
Enable pgvector, create indexes: (repo_id, pr_number) unique, embedding ivfflat, (review_id, severity) for filtering.
Write migrations in prisma/migrations/.
Seed script: use Faker + mock GitHub API responses to create 50 repos, 200 PRs, 1000 findings (vary types/severities).
```

### d) Workers
```
Add BullMQ in packages/queue:
- Job: AnalyzePRJob(repo_id, pr_number, commit_sha)
  1. Fetch PR diff from GitHub API (@octokit/rest)
  2. Filter changed files (skip node_modules, .reviewignore patterns)
  3. For each file:
     a. Parse with tree-sitter, extract function ASTs
     b. Embed with Voyage Code, find similar patterns in DB
     c. Send to Claude with context (file content, diff, similar code)
     d. Parse findings (JSON schema validation)
  4. Compute blast radius: for each modified function, semantic search for usages
  5. Store findings in DB, update review status
Make idempotent: check if review exists for (pr_id, commit_sha), skip if completed.
Retry: 3 attempts, exponential backoff (1/2/4 min), capture errors in Review.error_message.
Dead-letter queue: after max retries, mark review as 'failed', alert via webhook.
Rate limit: 10 GitHub API calls/sec, batch embed requests (50 functions at a time).
```

### e) Tests
```
Set up Jest in apps/api with ts-jest, @faker-js/faker.
Unit tests:
- test_tree_sitter_parsing (parse TS/Python files, assert correct AST structure)
- test_finding_deduplication (same issue on multiple lines, dedupe by type+file+message)
- test_blast_radius_calculation (mock vector search, assert correct usage count)
Integration tests:
- test_pr_review_flow (mock GitHub webhook, trigger job, assert findings stored)
- test_incremental_review (same PR, new commit, assert only new files analyzed)
- Mock Anthropic/OpenAI with nock or msw
Create k6 load test (load-test.js):
- Simulate 50 concurrent PR reviews
- Assert p95 latency < 10s for small PRs (<200 LOC)
- Assert no job failures (check BullMQ failed queue)
```

### f) AI
```
Implement analysis pipeline in packages/analyzer:
- CodeAnalyzer class:
  - parseFile(content, language): tree-sitter AST
  - embedFunctions(functions[]): Voyage Code batch embed
  - findSimilar(embedding): pgvector query top 5
  - reviewCode(file, diff, context): call Claude with structured output (Zod schema)
- BlastRadiusCalculator:
  - findUsages(function_name, repo_id): semantic search for function calls
  - estimateImpact(usages): count files, classify risk (low <5, medium <20, high >=20)
Create eval harness in eval/:
- Load golden-prs.jsonl (100 PRs, human-labeled issues with line numbers)
- For each PR:
  1. Run CodeAnalyzer
  2. Match findings to labels (IoU on line ranges, type match)
  3. Compute precision/recall/F1, false-positive rate
  4. Track fix acceptance: match suggested_fix to actual commits (diff similarity)
- Save eval-results.json with scores per category (bug, security, performance, style)
- Assert overall F1 >= 0.75, false-positive rate <= 0.2, acceptance rate >= 0.5
```

### g) CI/CD
```
Create .github/workflows/ci.yml:
- On PR: turbo lint, test, build (cache node_modules, .turbo)
- Run Jest with coverage, fail if < 80%
- Run eval harness, fail if F1 < 0.75 or FP rate > 0.2
- Check Prisma migration conflicts (prisma migrate diff)
Create .github/workflows/release.yml (on main merge):
- Build Docker images (api, web, worker)
- Tag with git SHA, 'latest', semver (if tagged)
- Push to GHCR
- Run smoke test: trigger review on test repo, assert completion
Create .github/workflows/deploy.yml (manual):
- Deploy to Vercel (web) and Railway (api, worker)
- Run post-deploy health check
```

### h) Instrumentation
```
Integrate OpenTelemetry in apps/api/main.ts:
- @opentelemetry/sdk-node with FastifyInstrumentation
- Custom spans:
  - 'analyze_pr' (tag: repo, pr_number, loc, duration)
  - 'parse_file' (tag: file_path, language, ast_size)
  - 'ai_review' (tag: model, tokens_in, tokens_out, cost)
  - 'blast_radius' (tag: function_name, usages_found)
- Export traces to Tempo
Add custom metrics (Prometheus client):
- review_duration_seconds (histogram, label: repo, loc_bucket)
- findings_total (counter, label: type, severity)
- ai_cost_dollars (counter, label: model)
- acceptance_rate (gauge, computed from findings.accepted)
Create grafana/dashboard.json:
- Panel 1: Review latency p50/p95/p99 by LOC bucket (heatmap)
- Panel 2: Findings by type/severity (stacked bar chart)
- Panel 3: AI cost per day (graph with cost breakdown by model)
- Panel 4: Fix acceptance rate over time (line chart)
- Panel 5: Queue depth (gauge)
Add Tempo, Prometheus, Grafana services to docker-compose.yml with persistent volumes.
```

## Success Metrics
- Review 200 LOC PR in <10s p95, 1000 LOC PR in <5 min p95
- Finding detection F1 >= 0.75 across all categories
- False-positive rate <= 20% (validated via eval)
- Fix acceptance rate >= 50% (team adopts suggestions)
- Cost < $0.50 per review (Sonnet 3.5 batch processing)
- Zero missed PRs (webhook delivery confirmed, retries on failure)
- 80%+ test coverage
