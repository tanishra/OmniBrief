# OmniBrief Project Report (Updated)

## 1. Overview
**OmniBrief** is an AI-powered technical newsletter platform designed to aggregate, curate, and summarize the latest advancements in AI and Machine Learning. It fetches data from multiple sources (Hacker News, ArXiv, GitHub Trending, RSS feeds, Product Hunt, and Reddit), processes the content through a LangGraph-based AI pipeline to rank and summarize the items, and synthesizes a daily technical digest sent to subscribers via email.

The project features a decoupled architecture:
- A **Next.js** frontend for the landing page and subscription management.
- A **FastAPI** backend that provides the API for subscriptions, confirmations, unsubscriptions, and contact requests.
- A **PostgreSQL** database (via Neon) to manage state for subscribers, sent items, delivery logs, rate limits, feedback, and newsletter archives.
- A **Python Worker** (`main.py`) that acts as an orchestrator, running the entire data gathering and AI curation pipeline, before rendering an HTML email template and broadcasting it via the Resend API.

## 2. System Architecture & Working
The application's core functionality resides in its automated daily worker (`main.py`) and the LangGraph intelligence engine (`src/agent_graph.py`).

**Workflow Breakdown:**
1. **Data Fetching:** The orchestrator fetches data concurrently from various sources using specialized fetchers (`src/fetchers/`). It utilizes `tenacity` for exponential backoff retries to ensure resilience against transient network failures.
2. **Filtering & History:** The fetched data is cross-referenced with a PostgreSQL table (`sent_items`) to filter out URLs that have already been sent.
3. **LangGraph Intelligence Engine:**
   - **Curate:** Deduplicates items across different sources using Token-Based Jaccard Similarity and correlates papers to their implementations.
   - **Rank:** Uses an LLM (`gpt-4o-mini`) to assign a novelty and relevance score (1-10) to each item based on a user profile. It caches the static prompt instructions to reduce API costs.
   - **Analyze (Summarize):** Scrapes the full content of the top-ranked articles/repos using HTTPX (with an SSRF-safe network backend) and a Playwright fallback (utilizing a globally reused browser context and anti-bot evasion scripts). The untrusted content is sanitized and wrapped in randomized XML tags to prevent prompt injection.
   - **Critic:** Evaluates the generated summaries for quality. If a significant portion is of poor quality, it loops back to the analyze step for revision.
   - **Synthesize:** An advanced LLM (`gpt-4o`) reads all summaries and generates a 1-2 paragraph "Executive Synthesis" identifying the daily trends.
4. **Rendering & Delivery:** The summaries and synthesis are passed into a Jinja2 HTML template (`src/renderer.py`). The rendered HTML is archived to PostgreSQL, and the email is broadcast to all confirmed subscribers using the Resend API. The delivery status and user feedback (via HMAC-signed links) are logged in the database.
5. **Pruning:** Old rate limits and sent history are automatically pruned from the database at the end of the run.

## 3. Addressed Security and Architectural Issues
The project has recently undergone significant hardening:
- **SSRF Prevention:** HTTPX connections now enforce pre-validated, safe IP addresses to prevent Time-of-Check to Time-of-Use (TOCTOU) DNS Rebinding attacks.
- **Prompt Injection Defense:** Web content is sanitized (stripping HTML/XML tags) and enclosed in dynamically generated boundary delimiters (`<data_{hex}>`) when sent to the LLM.
- **IP Spoofing:** FastAPI now validates whether inbound connections originate from trusted internal proxy IP ranges before respecting `X-Forwarded-For` headers for rate limiting.
- **Deterministic Builds:** All dependencies are strictly pinned in `requirements.txt`.
- **Performance & Reliability:** Rate limits were migrated from memory to PostgreSQL. The deduplication algorithm was upgraded from an expensive $O(N^2)$ string matcher to a fast Jaccard similarity model. Playwright was refactored to reuse browser contexts and limit concurrency.

## 4. Remaining Flaws & Production Readiness
While the application is highly robust, it is a **"Startup Grade"** rather than fully **"Enterprise Grade"** system. It can comfortably run in production for thousands of subscribers, but there are several architectural flaws remaining:

1. **Monolithic Broadcasting:** The `main.py` script gathers data, processes it, and sends emails sequentially using an internal `asyncio.Semaphore`. If the script crashes halfway through sending 50,000 emails, there is no built-in state mechanism to resume exactly where it left off without duplicate deliveries. An enterprise system would push rendered emails to an external message broker (like RabbitMQ or AWS SQS) and use worker nodes to consume the queue.
2. **Lack of Database Migrations (Alembic):** The database schema is currently managed via raw `CREATE TABLE IF NOT EXISTS` queries in `src/persistence.py`. This is brittle. Modifying existing tables (e.g., adding a new column) requires manual SQL scripts. A production environment requires a migration tool like Alembic to manage schema evolution.
3. **Zero Test Coverage:** The project currently lacks automated unit or integration tests (`pytest` collects 0 items). Any future refactoring carries a high risk of silently breaking functionality.
4. **Synchronous Database Driver:** The `psycopg` database driver is used synchronously inside the async FastAPI endpoints. This means that a slow database query will block the entire ASGI event loop, neutralizing FastAPI's concurrency benefits. The backend should be upgraded to use `psycopg[pool]` and its native async capabilities or an async ORM like SQLAlchemy/SQLModel.
5. **Production Web Server:** The `fastapi` backend is currently launched via a raw `uvicorn` command. In a true production environment, it should be run behind a process manager like Gunicorn with `uvicorn.workers.UvicornWorker` to utilize multiple CPU cores effectively.
