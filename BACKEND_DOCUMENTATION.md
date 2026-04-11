# InsightX AI – Backend Architecture Guide

Welcome to the InsightX core backend documentation. This backend is structured as a **Multi-Agent AI Pipeline** built in Python with **FastAPI**. It has been optimized entirely for maximum speed and zero local GPU/RAM consumption by simulating complex HuggingFace models using the highly advanced **Groq (`llama-3.3-70b-versatile`)** inference engine.

## 📁 Directory Structure Overview

The entire backend is contained inside the `insightx-ingestion/` directory:

```text
insightx-ingestion/
├── main.py                     # Entry point for the FastAPI server
├── config.py                   # Pydantic settings loading environment variables
├── requirements.txt            # Dependency tracker
├── models/
│   └── schemas.py              # Pydantic schemas enforcing input/output structure
├── agents/                     # The Core Multi-Agent Pipeline
│   ├── pipeline.py             # Orchestrator chaining all 5 agents sequentially
│   ├── event_agent.py          # Extracts pure facts & triggers fact-checking
│   ├── reasoning_agent.py      # Establishes cause-and-effect & sentiment
│   ├── personalization_agent.py# Adapts narrative based on User Profile
│   ├── action_agent.py         # Suggests practical next steps / generates quizzes
│   └── prediction_agent.py     # Generates foresight & checks live portfolio signals
└── tools/                      # The Action Modules ("Virtual Models")
    ├── llm.py                  # The central bridge firing requests to the Groq API
    ├── news.py                 # Fetches / scrapes raw article data using newspaper3k
    ├── fact_check.py           # Virtual NLI model
    ├── finance.py              # Virtual FinBERT + actual `yfinance` live scraping
    ├── quiz.py                 # Virtual Question Generator
    ├── sentiment.py            # Virtual RoBERTa model
    ├── simplify.py             # Virtual FLAN-T5 model
    ├── summariser.py           # Virtual BART-large-cnn model
    ├── translation.py          # Virtual MarianMT translator
    └── tts.py                  # Google TTS (saves audio locally)
```

---

## ⚙️ Core Architecture Concepts

### 1. The Pydantic Immutable Context Layer
To pass huge chunks of data cleanly between the 5 AI agents, we utilize a centralized `AgentContext` schema (`models/schemas.py`).
When a request comes in via `/api/analyze`, `agents/pipeline.py` initializes a blank `AgentContext`.
Then, it passes this exact object linearly through all 5 Agents using the `async def run(context) -> AgentContext:` method. 
Each agent reads what it needs from the context, queries its designated Tools, and writes new data variables back onto the context.

### 2. "Virtual" HuggingFace Models
To avoid local machine crashes and heavy deployment costs, we do not download native PyTorch models blindly. Rather, inside the `tools/` directory, every file (e.g. `summariser.py`, `sentiment.py`) contains a strictly engineered **Zero-Shot LLM Prompt**. 
We command the Groq API (via `tools/llm.py`) to act **identically** to those models, forcing it to return `JSON` arrays with strict keys mimicking those specific architectures.

### 3. Profile-Based Dynamic Actions
The API relies heavily on the `Profile` Enum (`general`, `student`, `investor`, `explorer`) supplied by the Frontend.
While the "Core 5 Agents" run for **every** request, they selectively fire different internal specialized tools. 
**Example (`action_agent.py`):** 
If the profile is `explorer`, the Action Agent runs the `tools/quiz.py` model. If not, the Quiz generator is ignored entirely to save tokens and time.

---

## 🚀 How to Run the Server

1. **Install Requirements** (Ensure you are in the `/insightx-ingestion` folder):
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Make sure you have an `.env` file generated with your API keys:
   ```env
   GROQ_API_KEY=YOUR_GROQ_KEY_HERE
   ```

3. **Start FastAPI**:
   ```bash
   python main.py
   # Alternatively: uvicorn main:app --reload --port 8001
   ```

4. **Test the Endpoint**:
   Open a browser to `http://localhost:8001/docs`. 
   Click on the `/api/analyze` POST route, select "Try it out", and pass a body like:
   ```json
   {
     "url": "https://finance.yahoo.com/news/nvidia-corp-nvda-announces-new-chips.html",
     "profile": "investor"
   }
   ```

---

## 🔮 Expected Pipeline Data Flow

When you execute that `POST` route, here is exactly what happens under the hood:

1. `pipeline.py` executes `tools/news.py` to scrape the Yahoo Finance URL.
2. `event_agent.py` pulls the *Who/What/When* into a JSON dictionary and runs a fact-check validation.
3. `reasoning_agent.py` detects positive/negative sentiment using the Virtual RoBERTa tool, simplifies the text, and traces a 3-step cause & effect sequence.
4. `personalization_agent.py` looks at the `investor` profile tag, aborts the 'student career mapping' script, and specifically triggers a Macro Economics detector.
5. `action_agent.py` generates 3 solid trading advice steps and uses `gTTS` to generate an audio mp3 in `/tmp/`.
6. `prediction_agent.py` makes future forecasts, extracts any company mentions, and compares them against your `finance.py` watchlist using live `yfinance` stock hooks.
7. The massive populated `AgentContext` object is gracefully dumped into an `InsightOutput` strict JSON payload and returned to the React Frontend!
