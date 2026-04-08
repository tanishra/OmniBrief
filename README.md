<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,50:1d4ed8,100:312e81&height=220&section=header&text=OmniBrief&fontSize=72&fontColor=FFFFFF&fontAlignY=40&desc=Autonomous%20Technical%20Research%20Briefing%20for%20Python%20Engineers&descAlignY=63&descColor=ffffff&descSize=18" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-2D333B?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

<br/>

> **OmniBrief is an autonomous discovery engine that scans the global AI frontier, using a multi-agent LangGraph pipeline to deliver a high-signal technical briefing directly to your inbox.**

<br/>

</div>

---

## Overview
OmniBrief is a **high-signal discovery platform** that autonomously scans the global AI landscape (ArXiv, GitHub, RSS, Technical Blogs) to deliver a personalized, technical research briefing. Unlike simple aggregators, it uses a **stateful agentic graph** to "think," "rank," and "correlate" information based on your personal interest profile.

## The "Why"
In the hyper-accelerated world of Artificial Intelligence, the "half-life" of knowledge is measured in days. Manually scouring ArXiv, GitHub, Reddit, and technical blogs every morning to find the signal in the noise has become a full-time job. 

I built **OmniBrief** to automate the research lifecycle. It acts as an autonomous technical analyst that:
- **Keeps up with the global pace:** Scans 30+ sources, from elite labs to underdog innovators.
- **Understands the signal:** Uses AI to read full-text articles and code, not just headlines.
- **Tailored to you:** Prioritizes specific frameworks and architectures defined in your personal profile.
- **Delivers value daily:** Sends a high-density report every morning at a specified time, ensuring you never miss a breakthrough while you sleep.

---

## System Architecture
The engine operates as a cyclical intelligence pipeline orchestrated by **LangGraph**.

```mermaid
graph TD
    %% Input Layer
    subgraph "1. Data Acquisition (Wide Net)"
        Fetch[Parallel Fetchers] -->|httpx| RSS[30+ Tech Blogs]
        Fetch -->|Atom API| ArXiv[Elite Research]
        Fetch -->|Search API| GH[GitHub Trending & Innovation]
        Fetch -->|Scraper| PH[ProductHunt & Signals]
    end

    %% Intelligence Layer
    subgraph "2. Agentic Intelligence Graph (The Brain)"
        RSS & ArXiv & GH & PH --> Filter[Persistent Memory Filter]
        Filter -->|SQLite| Dedup[Fuzzy Deduplicator]
        Dedup -->|Cross-Source| Corel[Contextual Correlator]
        Corel -->|Link Paper to Code| Rank[AI Ranking Node]
        Rank -->|PROFILE.md| Scoring[Personalized Scoring]
    end

    %% Deep Dive Layer
    subgraph "3. Cognitive Processing"
        Scoring --> Scrape[Hybrid Smart Scraper]
        Scrape -->|Playwright Fallback| Extract[Full-Text Extraction]
        Extract --> Summary[Analyst-Critic Loop]
        Summary -->|Self-Correction| Synthesis[Daily Strategic Synthesis]
    end

    %% Output Layer
    subgraph "4. Delivery & Persistence"
        Synthesis --> Render[Jinja2 Editorial Template]
        Render -->|Resend API| Email[Premium Substack Inbox]
        Email -->|Commit| History[SQLite & GitHub Cache]
    end

    %% Styling
    style Synthesis fill:#f96,stroke:#333,stroke-width:2px
    style Scoring fill:#6366f1,stroke:#fff,color:#fff
    style Corel fill:#10b981,stroke:#fff,color:#fff
```

## Key Features
- **Agentic Workflow:** Built with LangGraph for stateful, recoverable, and iterative processing.
- **Authority-Based Scouting:** Explicitly monitors elite labs (DeepSeek, HKUST, Microsoft, OpenAI) for underdog releases.
- **Full-Text Analysis:** Bypasses "headline-only" summaries by using **Playwright** to scrape and read the actual technical articles.
- **Cross-Source Correlation:** Automatically identifies when a new ArXiv paper has an official GitHub implementation and links them.
- **Personalized Ranking:** Uses your `PROFILE.md` to score and prioritize content matching your specific tech stack and interests.
- **Cost Auditing:** Built-in private token tracking to monitor OpenAI API budget.

## Setup
1. **Clone & Install:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
2. **Configure Profile:**
   Edit `PROFILE.md` to describe your technical interests in natural language.
3. **Set Environment:**
   Copy `.env.example` to `.env` and add your `OPENAI_API_KEY`, `RESEND_API_KEY`, and `GITHUB_TOKEN`.
4. **Run:**
   ```bash
   python main.py
   ```