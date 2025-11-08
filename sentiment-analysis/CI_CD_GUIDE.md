# CI/CD Guide

Continuous Integration and Continuous Deployment setup for the Sentiment Analysis Dashboard.

## Overview

This project uses GitHub Actions for CI/CD with the following workflows:

1. **API Tests** - Test Python API and ML package
2. **Web Build** - Build and test Next.js frontend
3. **Docker Build** - Build and publish Docker images
4. **Deploy** - Deploy to staging and production
5. **Pre-commit Hooks** - Local code quality checks

## Workflows

### 1. API Tests (`.github/workflows/api-tests.yml`)

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Changes to `apps/api/**` or `packages/ml/**`

**Jobs:**

#### Test Job
Runs on Python 3.11 and 3.12 with PostgreSQL and Redis services.

**Steps:**
1. ✓ Checkout code
2. ✓ Setup Python with caching
3. ✓ Install Poetry
4. ✓ Cache virtual environment
5. ✓ Install dependencies
6. ✓ Run linting (ruff)
7. ✓ Run type checking (mypy)
8. ✓ Run unit tests
9. ✓ Run integration tests
10. ✓ Run worker tests
11. ✓ Generate coverage report
12. ✓ Upload to Codecov
13. ✓ Check code formatting (black)
14. ✓ Security scan (bandit)

#### ML Package Test Job
Tests ML package independently.

**Steps:**
1. ✓ Test imports
2. ✓ Test preprocessing
3. ✓ Test training
4. ✓ Test model save/load
5. ✓ Test prediction

**Status Badge:**
```markdown
![API Tests](https://github.com/YOUR_USERNAME/AI-Projects/workflows/API%20Tests/badge.svg)
```

### 2. Web Build (`.github/workflows/web-build.yml`)

**Triggers:**
- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`
- Changes to `apps/web/**`

**Jobs:**

#### Build Job
Runs on Node.js 20.x and 21.x.

**Steps:**
1. ✓ Checkout code
2. ✓ Setup Node.js
3. ✓ Setup pnpm
4. ✓ Cache pnpm store
5. ✓ Install dependencies
6. ✓ Run ESLint
7. ✓ Run TypeScript type checking
8. ✓ Run tests (if configured)
9. ✓ Build Next.js application
10. ✓ Verify build output

#### Security Job
Runs security scans.

**Steps:**
1. ✓ npm audit
2. ✓ dependency check

**Status Badge:**
```markdown
![Web Build](https://github.com/YOUR_USERNAME/AI-Projects/workflows/Web%20Build/badge.svg)
```

### 3. Docker Build (`.github/workflows/docker-build.yml`)

**Triggers:**
- Push to `main` or `develop`
- Tags matching `v*`
- Pull requests to `main`

**Jobs:**

#### Build API Image
Builds and pushes API Docker image to GitHub Container Registry.

**Features:**
- Multi-platform (amd64, arm64)
- Layer caching
- Semantic versioning tags
- SHA-based tags

#### Build Web Image
Builds and pushes Web Docker image.

#### Build Worker Image
Builds and pushes Celery worker image.

#### Scan Images
Runs Trivy security scanner on all images.

**Image Tags:**
```
ghcr.io/USERNAME/sentiment-analysis-api:main
ghcr.io/USERNAME/sentiment-analysis-api:v1.0.0
ghcr.io/USERNAME/sentiment-analysis-api:main-abc1234
```

### 4. Deploy (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` (staging)
- Tags `v*.*.*` (production)
- Manual workflow dispatch

**Jobs:**

#### Deploy to Staging
Deploys to staging environment on every merge to main.

**Placeholder Steps:**
- Copy files to server
- Deploy with docker-compose
- Run database migrations
- Smoke tests
- Notifications

#### Deploy to Production
Deploys to production on version tags.

**Steps:**
1. ✓ Verify tag format (v1.0.0)
2. ✓ Deploy to production
3. ✓ Create GitHub release
4. ✓ Run migrations
5. ✓ Smoke tests
6. ✓ Rollback on failure

#### Health Check
Post-deployment verification.

**Checks:**
- API health endpoint
- Web accessibility
- Database connectivity
- Worker status

## Pre-commit Hooks

Local code quality checks before commits.

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Hooks

#### Python
- **black**: Code formatting
- **ruff**: Linting and auto-fixes
- **mypy**: Type checking
- **bandit**: Security scanning

#### General
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML syntax checking
- Large file detection
- Merge conflict detection
- Private key detection

#### JavaScript/TypeScript
- **ESLint**: Linting with auto-fix

#### Markdown & YAML
- Markdown linting
- YAML linting

#### Security
- Secret detection with baseline

### Configuration Files

- `.pre-commit-config.yaml` - Pre-commit configuration
- `.yamllint.yml` - YAML linting rules

## Code Quality Standards

### Coverage Targets

| Component | Target | Current |
|-----------|--------|---------|
| API | 85% | TBD |
| ML Package | 80% | TBD |
| Overall | 80% | TBD |

### Linting

**Python (Ruff):**
- Line length: 120
- Import sorting: isort
- Quote style: double

**TypeScript (ESLint):**
- Follows Next.js recommended config
- React hooks rules
- TypeScript strict mode

### Type Checking

**Python (mypy):**
- Ignore missing imports
- Gradual typing (not strict)

**TypeScript:**
- Strict mode enabled
- No implicit any
- Strict null checks

## Setting Up CI/CD

### Required Secrets

Add these to GitHub repository secrets (Settings → Secrets and variables → Actions):

#### For Docker Registry
```
GITHUB_TOKEN  # Automatically provided
```

#### For Deployment
```
STAGING_HOST           # Staging server hostname
STAGING_USER           # SSH username
STAGING_SSH_KEY        # SSH private key
PRODUCTION_HOST        # Production server hostname
PRODUCTION_USER        # SSH username
PRODUCTION_SSH_KEY     # SSH private key
```

#### For External Services
```
CODECOV_TOKEN          # Codecov upload token (optional)
FLY_API_TOKEN          # Fly.io API token (if using Fly)
SLACK_WEBHOOK          # Slack notifications (optional)
```

### Environment Variables

Create `.env` files for each environment:

**Staging (`.env.staging`):**
```bash
DATABASE_URL=postgresql://user:pass@staging-db:5432/sentiment
REDIS_URL=redis://staging-redis:6379
NEXT_PUBLIC_API_URL=https://api-staging.example.com
```

**Production (`.env.production`):**
```bash
DATABASE_URL=postgresql://user:pass@prod-db:5432/sentiment
REDIS_URL=redis://prod-redis:6379
NEXT_PUBLIC_API_URL=https://api.example.com
```

## Deployment Methods

### Option 1: Docker Compose on VPS

**Server Setup:**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose

# Clone repository
git clone https://github.com/USERNAME/AI-Projects.git
cd AI-Projects/sentiment-analysis

# Create .env file
cp .env.example .env
nano .env

# Start services
docker-compose up -d

# Run migrations
docker-compose exec api poetry run alembic upgrade head
```

**Update Deployment:**
```bash
git pull
docker-compose pull
docker-compose up -d
docker-compose exec api poetry run alembic upgrade head
```

### Option 2: Kubernetes

Create Kubernetes manifests:

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sentiment-api
  template:
    metadata:
      labels:
        app: sentiment-api
    spec:
      containers:
      - name: api
        image: ghcr.io/USERNAME/sentiment-analysis-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: sentiment-secrets
              key: database-url
```

Apply with:
```bash
kubectl apply -f k8s/
```

### Option 3: Platform as a Service

#### Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up
```

#### Heroku
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create sentiment-analysis-app

# Deploy
git push heroku main
```

## Monitoring Deployments

### GitHub Actions Dashboard

View workflow runs:
```
https://github.com/USERNAME/AI-Projects/actions
```

### Logs

**View workflow logs:**
1. Go to Actions tab
2. Click on workflow run
3. Click on job
4. Expand steps to see logs

**Download logs:**
```bash
gh run view <run-id> --log
```

### Notifications

#### Slack Integration

Add to workflow:
```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Deployment completed'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

#### Email Notifications

GitHub sends email notifications by default. Configure in Settings → Notifications.

## Troubleshooting

### Tests Failing

**Check logs:**
```bash
# Locally
poetry run pytest -v --tb=long

# In CI
# View GitHub Actions logs
```

**Common issues:**
- Missing environment variables
- Database not ready (increase health check interval)
- Port conflicts
- Dependency version mismatch

### Build Failures

**Docker build:**
```bash
# Test locally
docker build -t test-image -f apps/api/Dockerfile .

# Check build logs
docker build --progress=plain -t test-image .
```

**Next.js build:**
```bash
cd apps/web
pnpm run build
```

### Deployment Issues

**SSH connection:**
```bash
# Test SSH
ssh -i ~/.ssh/key user@host

# Check key permissions
chmod 600 ~/.ssh/key
```

**Docker Compose:**
```bash
# Check logs
docker-compose logs -f api

# Restart services
docker-compose restart

# Check status
docker-compose ps
```

### Pre-commit Hook Failures

**Skip hooks (emergency only):**
```bash
git commit --no-verify -m "message"
```

**Fix issues:**
```bash
# Auto-fix formatting
black apps/api
ruff check --fix apps/api

# Run specific hook
pre-commit run black --all-files
```

**Clear cache:**
```bash
pre-commit clean
pre-commit install --install-hooks
```

## Best Practices

### Commits

✅ **Good:**
```
feat: Add sentiment explanation endpoint
fix: Handle empty text in predictor
docs: Update API documentation
test: Add integration tests for batch analysis
```

❌ **Bad:**
```
fixed stuff
wip
asdf
```

### Pull Requests

1. Create feature branch from `develop`
2. Make changes
3. Run tests locally
4. Create PR to `develop`
5. Wait for CI to pass
6. Request review
7. Merge after approval

### Versioning

Follow Semantic Versioning (semver.org):

```
v1.0.0 - Major.Minor.Patch
  │ │ │
  │ │ └─ Bug fixes
  │ └─── New features (backwards compatible)
  └───── Breaking changes
```

### Branching Strategy

```
main          # Production code (deploys to prod)
  └─ develop  # Integration branch (deploys to staging)
      └─ feature/xyz
      └─ bugfix/abc
      └─ hotfix/urgent
```

### Release Process

1. Merge features to `develop`
2. Test in staging
3. Create release branch
4. Tag version: `git tag -a v1.0.0 -m "Release 1.0.0"`
5. Push tag: `git push origin v1.0.0`
6. CI automatically deploys to production
7. Create GitHub release

## Performance Optimization

### Caching

**GitHub Actions:**
- Poetry dependencies cached
- pnpm store cached
- Docker layers cached

**Build Times:**
- First build: ~5-10 minutes
- Cached build: ~2-3 minutes

### Parallel Jobs

Tests run in parallel across Python versions:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

### Docker Optimization

**Multi-stage builds:**
```dockerfile
FROM python:3.11-slim as builder
# Build dependencies

FROM python:3.11-slim as runtime
# Copy only necessary files
```

## Security

### Scanning

- **Trivy**: Container vulnerability scanning
- **Bandit**: Python security issues
- **npm audit**: JavaScript dependency vulnerabilities
- **detect-secrets**: Prevent committing secrets

### Secrets Management

❌ **Never commit:**
- API keys
- Database passwords
- SSH keys
- Environment files with secrets

✅ **Use:**
- GitHub Secrets
- Environment variables
- Secret management services (Vault, AWS Secrets Manager)

### SAST (Static Application Security Testing)

Enable CodeQL:
```yaml
# .github/workflows/codeql.yml
name: CodeQL
on:
  push:
    branches: [main]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v2
      - uses: github/codeql-action/analyze@v2
```

## Next Steps

- [ ] Set up staging environment
- [ ] Configure deployment secrets
- [ ] Set up monitoring (Sentry, Datadog)
- [ ] Configure alerts
- [ ] Set up log aggregation
- [ ] Implement blue-green deployment
- [ ] Add smoke tests to deployment
- [ ] Set up automated rollbacks

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Semantic Versioning](https://semver.org/)
- [Pre-commit Hooks](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
