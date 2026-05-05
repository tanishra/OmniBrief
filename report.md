# OmniBrief Project Report

## 1. Overview
**OmniBrief** is an AI-powered technical newsletter platform designed to aggregate, curate, and summarize the latest advancements in AI and Machine Learning. Instead of just listing links, it acts as a smart filter. It fetches data from multiple sources (Hacker News, ArXiv, GitHub Trending, RSS feeds, Product Hunt, and Reddit), processes the content through a LangGraph-based AI pipeline to rank and summarize the items, and synthesizes a daily technical digest sent to subscribers via email.

The project features a decoupled architecture:
- A **Next.js** frontend for the landing page and subscription management.
- A **FastAPI** backend that provides the API for subscriptions, confirmations, unsubscriptions, and contact requests.
- A **PostgreSQL** database (via Neon) to manage state for subscribers, sent items, and delivery logs.
- A **Python Worker** (`main.py`) that acts as an orchestrator, running the entire data gathering and AI curation pipeline, before rendering an HTML email template and broadcasting it via the Resend API.

## 2. System Architecture & Working
The application's core functionality resides in its automated daily worker (`main.py`) and the LangGraph intelligence engine (`src/agent_graph.py`).

**Workflow Breakdown:**
1. **Data Fetching:** The orchestrator fetches data concurrently from various sources using specialized fetchers (`src/fetchers/`). It targets AI-related keywords, high scores on Reddit/HackerNews, and top repos on GitHub.
2. **Filtering & History:** The fetched data is cross-referenced with a PostgreSQL table (`sent_items`) to filter out URLs that have already been sent in previous digests.
3. **LangGraph Intelligence Engine:**
   - **Curate:** Deduplicates items across different sources using string similarity (e.g., matching a paper title on ArXiv with a GitHub repo name) and correlates papers to their implementations.
   - **Rank:** Uses an LLM (`gpt-4o-mini`) to assign a novelty and relevance score (1-10) to each item based on a user profile (`PROFILE.md`). It keeps only the top N items per category.
   - **Analyze (Summarize):** Scrapes the full content of the top-ranked articles/repos using HTTPX (with a Playwright fallback for JS-heavy sites). An LLM then generates a concise, 2-3 sentence technical summary.
   - **Critic:** Evaluates the generated summaries for quality (length, technical keywords). If a significant portion is of poor quality, it loops back to the analyze step for revision.
   - **Synthesize:** An advanced LLM (`gpt-4o`) reads all summaries and generates a 1-2 paragraph "Executive Synthesis" identifying the daily trends.
4. **Rendering & Delivery:** The summaries and synthesis are passed into a Jinja2 HTML template (`src/renderer.py`), and the email is broadcast to all confirmed subscribers using the Resend API (`src/mailer.py`). The delivery status is logged in the database.

## 3. Major Problems & Limitations
- **Worker Execution & Scheduling:** Currently, the daily pipeline (`main.py`) acts as a standalone script. There is no built-in cron job or task queue (like Celery/RabbitMQ). It relies on external automation (like GitHub Actions, though the workflow file is missing) or manual execution.
- **Scraping Reliability:** The web scraping fallback uses headless Chromium via Playwright. While robust against simple anti-bot protections, it is extremely resource-intensive and prone to hanging or timing out, which can slow down the daily pipeline significantly.
- **Cost Scaling:** The application uses LLM calls heavily. It ranks *all* fetched items, then summarizes the top ones, and finally synthesizes them. If the volume of raw data increases, API costs (both OpenAI and Resend) will scale linearly.
- **In-Memory Rate Limiting:** The FastAPI backend relies on an in-memory dictionary (`_rate_buckets` in `app.py`) for rate limiting. This means rate limits are reset if the server restarts, do not share state across multiple load-balanced workers, and can cause memory leaks over time because empty deques are never purged from the dictionary.
- **$O(N^2)$ Deduplication Logic:** The deduplication in `src/processor.py` uses `difflib.SequenceMatcher` to compare every new title against every previously seen title. As the number of daily fetched items grows, this will become computationally slow.

## 4. Security Issues
- **Server-Side Request Forgery (SSRF) bypass (TOCTOU):**
  The scraping engine (`src/scraper.py`) implements a custom `_is_safe_url` function that resolves hostnames and blocks private IP addresses to prevent SSRF. However, this is vulnerable to **Time-of-Check to Time-of-Use (TOCTOU)** via DNS Rebinding. The DNS lookup happens during validation, but HTTPX/Playwright performs its own DNS lookup when fetching. An attacker could host a domain that initially resolves to a safe IP but switches to an internal IP (like `169.254.169.254` or `127.0.0.1`) right after the check, exposing internal services or cloud metadata APIs.
- **Prompt Injection:**
  The summarizer (`src/summarizer.py`) directly feeds untrusted website content into the LLM prompt inside `<data>` tags. Although there is a system instruction to ignore commands inside these tags, LLMs are still highly susceptible to prompt injection. A malicious actor could write an article or GitHub description designed to override instructions, potentially forcing the LLM to output offensive text, hallucinate information, or craft phishing links in the newsletter.
- **IP Spoofing for Rate Limit Bypass:**
  In `app.py`, the function `_get_client_ip` reads the `x-forwarded-for` header to determine the client IP. If the FastAPI application is ever exposed directly to the internet (without a trusted reverse proxy like Nginx or Cloudflare overriding the header), an attacker can easily spoof the `x-forwarded-for` header to completely bypass the rate limits for subscribing, unsubscribing, and sending contact messages.
- **Lack of Dependency Pinning / Vulnerable Packages:**
  The `requirements.txt` only lists high-level package names without strict version pinning (e.g., `fastapi`, `langchain`, `playwright`). This can lead to non-deterministic builds and makes the project susceptible to supply chain attacks or accidental breaking changes from dependencies.
