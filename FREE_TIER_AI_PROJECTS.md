# 5 Free-Tier AI Portfolio Projects

Production-grade AI systems using **open-source models** and **free APIs** - no OpenAI/Anthropic required.

---

## Project 1: Smart Code Search Engine with Local Embeddings

### Overview
A semantic code search tool that indexes your entire codebase using local embeddings, provides intelligent search with natural language queries, and suggests similar code patterns. Uses **sentence-transformers** (runs locally, completely free) and **tree-sitter** for AST parsing.

### Stack
- **Frontend**: Next.js 14 + TypeScript
- **Backend**: Python FastAPI
- **Embeddings**: sentence-transformers (local, free)
  - Model: `all-MiniLM-L6-v2` (384 dim, 80MB)
  - Speed: 14,000 sentences/sec on CPU
- **Vector DB**: ChromaDB (local, free) or pgvector
- **AST Parsing**: tree-sitter (free)
- **Deployment**: Docker + free VPS ($0-5/month)

### Key Features
- Index codebases up to 100k LOC in <5 minutes
- Natural language search: "authentication middleware with JWT"
- Find code duplicates and similar patterns
- Export search results as VS Code snippets
- Works 100% offline (no API calls)

### Why It's Free
- Embeddings run locally on CPU (no GPU needed)
- No API calls to external services
- All models open-source (MIT/Apache licenses)
- Can deploy on free tier (Render, Railway $5 credit)

### Architecture Highlights
- **Incremental Indexing**: Only re-embed changed files (git diff)
- **Multi-language**: Supports TS, Python, Go, Rust, Java
- **Fast Search**: HNSW index for <50ms p95 latency
- **Caching**: Store embeddings in SQLite, never recompute

### Engineering Challenges
- Efficient chunking strategy (function-level granularity)
- Handling large repos (batch processing, pagination)
- Incremental updates (only re-index changed files)
- Query optimization (vector search + keyword filter)

### Success Metrics
- Index 50k LOC in <2 min
- Search latency p95 <100ms
- Find relevant code with >80% precision
- Zero cost (runs on laptop or free tier)

---

## Project 2: Content Moderation System with Hugging Face Models

### Overview
A real-time content moderation pipeline that detects toxic content, hate speech, spam, and PII using **open-source classifiers from Hugging Face**. Includes webhook API, confidence scoring, and appeal workflow. Uses free Hugging Face Inference API (30k requests/month free).

### Stack
- **Frontend**: Next.js 14 with moderation dashboard
- **Backend**: Node.js + Fastify
- **Models** (all free via Hugging Face):
  - Toxicity: `unitary/toxic-bert` (94M params)
  - Hate Speech: `facebook/roberta-hate-speech-dynabench`
  - Spam: `mrm8488/bert-tiny-finetuned-sms-spam-detection`
  - PII Detection: `StanfordAIMI/stanford-deidentifier-base`
- **Queue**: BullMQ + Redis
- **Database**: Postgres (Supabase free tier)
- **Deployment**: Railway + Vercel (both free tier)

### Key Features
- Multi-model ensemble (combine 4 models for higher accuracy)
- Real-time API (<200ms p95)
- Confidence thresholds (auto-approve, auto-reject, manual review)
- Appeal workflow for false positives
- Analytics dashboard (moderation stats over time)

### Why It's Free
- Hugging Face Inference API: **30,000 requests/month free**
- Can self-host models on CPU (smaller models run fine)
- All infrastructure on free tiers
- No GPU required (BERT runs on CPU in <500ms)

### Architecture Highlights
- **Ensemble Scoring**: Weighted average of 4 models
- **Fallback Strategy**: If HF API down, use cached local model
- **Rate Limiting**: Queue system prevents API quota exhaustion
- **Human-in-the-Loop**: Manual review for 0.6-0.8 confidence range

### Engineering Challenges
- Handling API rate limits (queue with backpressure)
- Model disagreement resolution (ensemble voting)
- False positive handling (appeal system)
- Performance optimization (batch inference)

### Success Metrics
- Detect toxic content with F1 >0.85
- p95 latency <300ms (including API call)
- False positive rate <10%
- 100% free (within HF free tier limits)

---

## Project 3: Real-Time Translation API with Meta's NLLB

### Overview
A translation service supporting 200+ languages using **Meta's No Language Left Behind (NLLB)** model. Includes caching, batch translation, and quality scoring. Runs locally or on free GPU providers (Replicate free tier: 50 predictions/month).

### Stack
- **Frontend**: Next.js 14 with translation UI
- **Backend**: Python FastAPI
- **Model**: `facebook/nllb-200-distilled-600M`
  - 200 languages, 600M params
  - Runs on CPU (slow) or GPU (fast)
- **Caching**: Redis (cache translations, reduce compute)
- **Queue**: Celery for batch jobs
- **Deployment**:
  - API: Railway free tier
  - Model: Replicate free tier or self-hosted

### Key Features
- Translate between any of 200+ language pairs
- Batch translation (documents, subtitles)
- Quality scoring (confidence, fluency metrics)
- Translation memory (cache common phrases)
- REST API + WebSocket for streaming

### Why It's Free
- NLLB is fully open-source (CC-BY-NC 4.0)
- Can run distilled 600M model on CPU
- **Replicate free tier**: 50 predictions/month
- **Alternative**: Google Colab free GPU (12hr sessions)
- Cache aggressively (>70% cache hit rate)

### Architecture Highlights
- **Smart Caching**: Hash source text + lang pair, serve from cache
- **Batching**: Process 100 sentences at once (10x faster)
- **Streaming**: WebSocket for real-time translation
- **Fallback Chain**: Replicate → Colab → local CPU

### Engineering Challenges
- Managing GPU quota (free tier limits)
- Cache invalidation strategy
- Handling rare languages (lower quality)
- Latency optimization (caching, batching)

### Success Metrics
- Translate common pairs in <1s (with cache)
- BLEU score >30 for high-resource languages
- Cache hit rate >70%
- Stay within free tier limits

---

## Project 4: GitHub PR Summarizer with Local LLMs (Ollama)

### Overview
A GitHub App that analyzes PRs and generates summaries, changelogs, and release notes using **Ollama** (runs LLaMA 3.2 locally for free). No external API calls, 100% self-hosted.

### Stack
- **Frontend**: Next.js 14 with GitHub OAuth
- **Backend**: Node.js + Fastify
- **LLM**: Ollama + LLaMA 3.2 (3B params)
  - Runs on CPU (8GB RAM required)
  - 100% free, no API costs
- **GitHub Integration**: Octokit + webhooks
- **Database**: Postgres (Supabase free tier)
- **Deployment**: VPS with Ollama ($5/month or free if you have spare hardware)

### Key Features
- Auto-generate PR descriptions from diff
- Create changelog entries (semantic versioning)
- Suggest reviewers based on file changes
- Detect breaking changes
- Generate release notes from merged PRs

### Why It's Free
- **Ollama**: 100% free, open-source LLM runtime
- **LLaMA 3.2**: Free, runs on CPU (slow but works)
- No external API calls (everything local)
- Can run on old laptop or free cloud credits

### Architecture Highlights
- **Context Optimization**: Only send relevant diff chunks (not full PR)
- **Prompt Engineering**: Structured output for consistent formatting
- **Incremental Processing**: Process files one at a time
- **Caching**: Store summaries, don't regenerate

### Engineering Challenges
- Managing context limits (LLaMA 3.2 has 128k context)
- Optimizing prompts for smaller models
- Handling large PRs (>1000 LOC)
- Performance on CPU (5-10s per summary)

### Success Metrics
- Generate PR summary in <30s
- Summary captures key changes (human eval)
- Detect breaking changes with >90% recall
- Zero API costs (fully self-hosted)

### Alternative Models (all free)
- **Mistral 7B** (better quality, slower)
- **Phi-3 Mini** (3.8B, fast on CPU)
- **Gemma 2B** (smallest, fastest)

---

## Project 5: Sentiment Analysis Dashboard with Classical ML

### Overview
A real-time sentiment analysis system for social media, customer reviews, or support tickets using **classical ML** (no neural networks needed). Uses scikit-learn's Naive Bayes + TF-IDF, runs blazingly fast, 100% free, no dependencies on external APIs.

### Stack
- **Frontend**: Next.js 14 with real-time charts (Chart.js)
- **Backend**: Python FastAPI
- **ML**: scikit-learn (free, CPU-only)
  - Model: Multinomial Naive Bayes + TF-IDF
  - Training: <1 min on 100k samples
  - Inference: <1ms per prediction
- **Database**: Postgres + TimescaleDB (time-series)
- **Queue**: Celery for batch processing
- **Deployment**: Railway + Vercel (free tiers)

### Key Features
- Real-time sentiment scoring (positive, neutral, negative)
- Emotion detection (joy, anger, sadness, surprise)
- Trend analysis (sentiment over time)
- Entity-level sentiment (per product, person, topic)
- Keyword extraction (important phrases)

### Why It's Free
- **No neural networks**: Classical ML runs on any CPU
- **No API calls**: Everything computed locally
- **Fast training**: Retrain model in seconds
- **Tiny models**: <10MB serialized model

### Architecture Highlights
- **Streaming Pipeline**: Process data in real-time (Kafka/Redis Streams)
- **Incremental Learning**: Update model with new data
- **Explainability**: Show which words influenced score
- **Multi-language**: Train separate models per language

### Engineering Challenges
- Feature engineering (TF-IDF tuning)
- Handling slang, emojis, abbreviations
- Class imbalance (more neutral than positive/negative)
- Real-time retraining (online learning)

### Success Metrics
- Sentiment accuracy F1 >0.75 (competitive with BERT)
- Inference latency <5ms per sample
- Process 10k samples/sec on single CPU
- Zero cost (no APIs, runs anywhere)

### Advanced Features
- **Aspect-based sentiment**: Per-topic sentiment in reviews
- **Sarcasm detection**: Rule-based + context patterns
- **Custom training**: Upload your own labeled data
- **A/B testing**: Compare model versions

---

## Comparison Table

| Project | Primary Tech | Cost | Speed | Difficulty | Best For |
|---------|-------------|------|-------|------------|----------|
| 1. Code Search | sentence-transformers | $0 | Fast (50ms) | Medium | Portfolio, actual use |
| 2. Content Mod | Hugging Face API | $0 (30k/mo) | Medium (300ms) | Medium | Resume, interviews |
| 3. Translation | NLLB + Replicate | $0 (50 pred/mo) | Slow (5s) | Hard | Learning NLP |
| 4. PR Summarizer | Ollama + LLaMA | $0-5 | Slow (30s) | Medium | Impressing employers |
| 5. Sentiment Analysis | scikit-learn | $0 | Blazing (5ms) | Easy | Quick win |

---

## Why These Projects Stand Out

### 1. **Zero Recurring Costs**
- No API subscriptions
- Run on free tiers or cheap hardware
- Open-source models (no licensing fees)

### 2. **Production-Ready**
- Handle real-world data at scale
- Proper error handling, retries, monitoring
- Can deploy to production immediately

### 3. **Resume-Worthy**
- Show ML engineering skills (model deployment, optimization)
- Demonstrate cost consciousness (important for startups)
- Highlight system design (caching, queueing, APIs)

### 4. **Actually Useful**
- Code Search: Use daily for your own projects
- Content Mod: Startups need this for UGC platforms
- Translation: Useful for international products
- PR Summarizer: Open-source maintainers love this
- Sentiment Analysis: Every company analyzes customer feedback

### 5. **Interview Talking Points**
- "Reduced inference cost from $0.02 to $0 per request"
- "Achieved 80% of BERT accuracy with 100x faster classical ML"
- "Deployed LLaMA 3.2 on CPU, no GPU required"
- "Handled 10k requests/day within free tier limits"

---

## Free-Tier Infrastructure

### Hosting Options (All Free or <$5/month)

**Compute:**
- Railway: $5 credit/month (sufficient for API)
- Render: 750 hours/month free
- Fly.io: 3 VMs free (256MB RAM each)
- Vercel: Unlimited free (frontend)

**Database:**
- Supabase: 500MB free
- PlanetScale: 5GB free (MySQL)
- Neon: 3GB free (Postgres)
- MongoDB Atlas: 512MB free

**Models/ML:**
- Hugging Face Inference API: 30k requests/month free
- Replicate: 50 predictions/month free
- Ollama: Fully local (free)
- Google Colab: Free GPU (12hr sessions)

**Storage:**
- Supabase Storage: 1GB free
- Cloudflare R2: 10GB free
- Backblaze B2: 10GB free

---

## Recommended Build Order

### 1. **Start with Project 5** (Sentiment Analysis) - 6-8 hours
**Why**: Easiest, fastest, immediate results
- No complex model setup
- Classical ML is well-understood
- Runs anywhere (CPU, serverless)
- Great for learning ML basics

### 2. **Then Project 1** (Code Search) - 10-12 hours
**Why**: Practical, you'll actually use it
- sentence-transformers easy to use
- Solves real problem (searching your code)
- Good intro to vector databases
- Can show in interviews ("I built the tool I use daily")

### 3. **Then Project 2** (Content Moderation) - 10-12 hours
**Why**: High-value, resume-worthy
- Every startup needs content moderation
- Shows multi-model ensemble skills
- Hugging Face API is industry-standard
- Great for safety/trust & safety roles

### 4. **Advanced: Project 4** (PR Summarizer) - 14-16 hours
**Why**: Cutting-edge, uses real LLMs
- Runs LLaMA locally (impressive)
- GitHub integration (practical)
- Good for DevTools companies
- Shows you can deploy LLMs without APIs

### 5. **Advanced: Project 3** (Translation) - 14-16 hours
**Why**: Multi-lingual, challenging
- NLLB is state-of-the-art
- 200 languages (impressive scale)
- Good for international companies
- Teaches model optimization

---

## Next Steps

I can create full specs with:
- 8 Claude Code prompts (like the original projects)
- Build & validation guides
- Cost optimization strategies
- Deployment instructions

**Which project interests you most?** I'll create a detailed spec for it.

Or I can create mini-specs for all 5 projects right now (similar format to the original 3 projects).

Let me know! 🚀
