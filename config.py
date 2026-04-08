"""
config.py — Centralized configuration for OmniBrief
All secrets are pulled from environment variables (set in GitHub Actions secrets or .env)
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Recipients ────────────────────────────────────────────────────────────────
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "tanishrajput9@gmail.com")   # ← your Gmail (Resend free tier: must match your account email)
SENDER_EMAIL    = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")
SENDER_NAME     = os.getenv("SENDER_NAME", "OmniBrief")

# ── API Keys ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY", "")
RESEND_API_KEY  = os.getenv("RESEND_API_KEY", "")
GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN", "")   # Optional but recommended

# ── OpenAI Settings ───────────────────────────────────────────────────────────
OPENAI_MODEL       = "gpt-4o-mini"
OPENAI_MAX_TOKENS  = 200
OPENAI_TEMPERATURE = 0.3

# ── Fetch Limits ──────────────────────────────────────────────────────────────
HN_MAX_ITEMS          = 10
ARXIV_MAX_ITEMS       = 10
GITHUB_TRENDING_MAX   = 20
RSS_MAX_PER_FEED      = 3
PRODUCTHUNT_MAX       = 10
REDDIT_MAX_ITEMS      = 10

# ── ArXiv Categories (Comprehensive AI coverage) ─────────────────────────────
ARXIV_CATEGORIES = [
    "cs.AI",    # Artificial Intelligence
    "cs.LG",    # Machine Learning
    "cs.CL",    # Computation and Language / NLP
    "cs.CV",    # Computer Vision
    "cs.RO",    # Robotics
    "cs.MA",    # Multi-Agent Systems
    "cs.NE",    # Neural and Evolutionary Computing
    "stat.ML",  # Stats / ML

    # Expanded / Innovative Categories
    "cs.GT",    # Game Theory (Agent reasoning & Multi-agent strategy)
    "cs.IR",    # Information Retrieval (RAG, Search, Embeddings)
    "cs.HC",    # Human-Computer Interaction (AI Assistants & UX)
    "cs.CY",    # Computers and Society (Ethics, Safety, Policy, Alignment)
    "cs.CR",    # Cryptography and Security (Adversarial ML & AI Privacy)
    "cs.DB",    # Databases (Vector DBs & Data Infra for AI)
    "cs.GR",    # Graphics (3D Gen-AI & Neural Rendering)
    "cs.ET",    # Emerging Technologies (Hardware AI & New Paradigms)
]

# ── RSS Feeds (Global coverage — US, Europe, China, Research) ─────────────────
RSS_FEEDS = [
    # ── US Tech Media ─────────────────────────────────────────────────────────
    {
        "name": "TechCrunch AI",
        "url":  "https://techcrunch.com/category/artificial-intelligence/feed/",
        "category": "news",
    },
    {
        "name": "VentureBeat AI",
        "url":  "https://venturebeat.com/category/ai/feed/",
        "category": "news",
    },
    {
        "name": "Wired AI",
        "url":  "https://www.wired.com/feed/tag/ai/latest/rss",
        "category": "news",
    },
    {
        "name": "The Verge AI",
        "url":  "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "category": "news",
    },
    {
        "name": "Ars Technica AI",
        "url":  "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "category": "news",
    },
    # ── Research & Deep Dives ──────────────────────────────────────────────────
    {
        "name": "MIT Technology Review AI",
        "url":  "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "category": "research",
    },
    {
        "name": "The Batch (DeepLearning.AI)",
        "url":  "https://www.deeplearning.ai/the-batch/feed/",
        "category": "newsletter",
    },
    {
        "name": "Import AI (Jack Clark)",
        "url":  "https://importai.substack.com/feed",
        "category": "newsletter",
    },
    {
        "name": "The Gradient",
        "url":  "https://thegradient.pub/rss/",
        "category": "research",
    },

    # ── Company Blogs ──────────────────────────────────────────────────────────
    {
        "name": "OpenAI Blog",
        "url":  "https://openai.com/blog/rss.xml",
        "category": "company",
    },
    {
        "name": "Anthropic News",
        "url":  "https://www.anthropic.com/news/rss",
        "category": "company",
    },
    {
        "name": "Google DeepMind Blog",
        "url":  "https://deepmind.google/blog/rss.xml",
        "category": "company",
    },
    {
        "name": "Hugging Face Blog",
        "url":  "https://huggingface.co/blog/feed.xml",
        "category": "company",
    },
    {
        "name": "Meta AI Blog",
        "url":  "https://ai.meta.com/blog/rss/",
        "category": "company",
    },

    # ── Developer & Independent Blogs (High Signal) ─────────────────────────────
    {
        "name": "Simon Willison's Weblog",
        "url":  "https://simonwillison.net/atom/entries/",
        "category": "developer",
    },
    {
        "name": "Sebastian Raschka (Ahead of AI)",
        "url":  "https://sebastianraschka.com/rss.xml",
        "category": "research",
    },
    {
        "name": "Eugene Yan",
        "url":  "https://eugeneyan.com/rss/",
        "category": "developer",
    },
    {
        "name": "LangChain Blog",
        "url":  "https://blog.langchain.dev/rss/",
        "category": "framework",
    },
    {
        "name": "LlamaIndex Blog",
        "url":  "https://www.llamaindex.ai/blog/rss.xml",
        "category": "framework",
    },
    {
        "name": "Weights & Biases Blog",
        "url":  "https://wandb.ai/fully-connected/feed.xml",
        "category": "developer",
    },

    # ── Academic AI Labs ────────────────────────────────────────────────────────
    {
        "name": "Berkeley BAIR Blog",
        "url":  "https://bair.berkeley.edu/blog/feed.xml",
        "category": "research",
    },
    {
        "name": "Stanford HAI News",
        "url":  "https://hai.stanford.edu/news/rss.xml",
        "category": "research",
    },
    {
        "name": "CMU Machine Learning Blog",
        "url":  "https://blog.ml.cmu.edu/feed/",
        "category": "research",
    },

    # ── Global / China ─────────────────────────────────────────────────────────
    {
        "name": "Synced (AI from China/Global)",
        "url":  "https://syncedreview.com/feed/",
        "category": "global",
    },
    {
        "name": "KDnuggets",
        "url":  "https://www.kdnuggets.com/feed",
        "category": "news",
    },
    {
        "name": "Towards Data Science",
        "url":  "https://towardsdatascience.com/feed",
        "category": "tutorial",
    },
]

# ── GitHub Search Queries (Comprehensive AI coverage) ──────────────────────────
GITHUB_QUERIES = [
    # Agents & Autonomy
    "AI agent autonomous",
    "multi-agent system",
    "agentic workflow",
    "AI agent framework",

    # Emerging Architectures (Python-heavy)
    "long-context LLM python",
    "reasoning model CoT python",
    "mixture of experts MoE python",
    "state space model SSM python",
    "mamba architecture python",
    "bitnet 1bit LLM",

    # Infrastructure & Tooling
    "MCP server python",
    "model context protocol tools",
    "vLLM optimization",
    "unsloth fine-tuning",
    "ollama python",
    "pydantic-ai",
]

# ── AI Authority Organizations (Global Elite Labs) ───────────────────────────
# corporate, academic, and open-source powerhouses.
AI_ORGANIZATIONS = [
    # The Giants
    "microsoft", "openai", "google", "anthropic", "meta-llama", "nvidia",
    
    # The Frontier Labs (US & Europe)
    "deepmind", "mistralai", "huggingface", "togethercomputer", "groq",
    "lightning-AI", "runwayml", "replicate", "adept-ai", "answerdotai",
    
    # The Asian Powerhouse (China/HK/Singapore)
    "deepseek-ai", "bytedance", "HKUST-NLP", "moonshot-ai", "01-ai", 
    "THUDM", "modelscope", "alibaba", "tencent", "internlm", "baichuan-inc", "HKDUS",
    
    # Academic & Research Collectives
    "stanford-hai", "stanford-nlp", "berkeley-bair", "mit-csail", "cmu-ml",
    "EleutherAI", "LAION-AI", "bigscience", "allenai",
    
    # Individual Innovators (High-Signal personal orgs)
    "karpathy", "simonw", "fastai", "hwchase17", # LangChain
    "jerryjliu", # LlamaIndex
]

# ── User Interests (For Personalized V7 Ranking) ──────────────────────────────
# The AI uses these keywords to give higher scores to things you care about.
USER_INTERESTS = [
    "AI Agents & Autonomous Workflows",
    "Python Frameworks & SDKs",
    "LLM Orchestration & Memory",
    "Claude & Anthropic Ecosystem",
    "Model Context Protocol (MCP)",
    "Efficient Inference (vLLM, Ollama)",
    "RAG & Vector Databases",
]

# ── Timezone ──────────────────────────────────────────────────────────────────
TIMEZONE = "Asia/Kolkata"