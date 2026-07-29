# Qanoony (قانوني) — Egyptian Labor Law RAG Assistant for Employers & Startups
## Complete Project Plan

> **Note on scope:** This is a **full working prototype**, not a production deployment. The goal is a complete, functioning end-to-end system (data -> retrieval -> LLM -> UI) that can be demoed live.

---

## The Problem

Employers, startup founders, and small business owners in Egypt regularly need to know what they're legally required to do as an employer — contract requirements, notice periods, leave entitlements, termination rules, working hours — but have no reliable, fast way to find out. Lawyers are expensive for simple questions, forums are unreliable, and generic AI answers confidently even when wrong, with no grounding in actual Egyptian law text.

## The Solution

A RAG-powered assistant for **employers and people starting a business** that only answers using the real text of Egyptian Labor Law, always cites the specific article it's using, and says "not covered" instead of guessing when something is outside its scope.

## Who It's For

- Startup founders hiring their first employee, with no institutional HR knowledge
- Small business owners who want a compliance sanity-check
- Anyone thinking about starting a business who wants to understand employer obligations before committing

---

## What We Have Built So Far

### Day 1: Data + RAG Core — Complete and Fully Verified

- Fetched and cleaned the full text of Egyptian Labor Law No. 14 of 2025 from Arabic Wikisource
- Chunked by article using a line-anchored regex, avoiding mid-sentence splits and boilerplate contamination
- Result: 301 verified chunks, zero duplicates, spot-checked at edges and midpoints
- Embedded with `BAAI/bge-m3` (from Hugging Face) and stored in ChromaDB
- Full data integrity verification completed

### Day 2: LangChain Chain + LLM — Complete and Running Locally

- Integrated Groq (Llama 3.3 70B) through LangChain; resolved LangChain/Pydantic compatibility issues
- Secured the Groq API key using environment variables
- Built an LCEL retrieval chain with a strict prompt preventing hallucination and enforcing source-grounded answers
- Iterated on the prompt to resolve a refusal-bypass failure mode (model explaining around refusals instead of declining cleanly)
- Validated the pipeline with multiple in-scope and out-of-scope test cases
- **Migrated the complete RAG pipeline from Kaggle to a local VS Code development environment** — no longer dependent on Kaggle notebooks
- Downloaded and integrated the persisted ChromaDB knowledge base into the local backend
- Created a reusable `rag.py` module initializing the embedding model, ChromaDB, and Groq LLM, exposing an `ask_qanoony(question)` function
- Verified the local pipeline with `test_rag.py`, confirming retrieval and generation work correctly outside Kaggle
- Refactored `ask_qanoony()` to return only the generated answer (not the full LangChain response object), making it directly usable by the frontend
- **Added automatic multilingual support**: detects the language of the user's query, responds in Arabic for Arabic questions and English for English questions, and translates retrieved Arabic legal content into professional English while preserving legal meaning — all existing safety rules and citation requirements preserved
- **Replaced hardcoded greeting logic with intelligent conversational routing**: casual conversation (greetings, thanks, capability questions) is answered directly by the LLM, while employment-law questions continue to use the full RAG pipeline — removing brittle rule-based greeting detection

**Result:** a fully local, working RAG pipeline with multilingual support and smart conversational routing, verified to consistently retrieve correct articles and avoid hallucination on unsupported topics.

**Still remaining for Day 2:**
- Add conversational memory
- Expand testing with additional edge cases
- Further validate multilingual behavior with broader Arabic/English test scenarios
- Improve the system prompt so the assistant clearly communicates its current scope (Employment Law only) without implying support for unrelated legal domains

### Day 3: Platform + UI — Core Complete

1. **UI designed in Stitch** — header with logo and EN/AR toggle, sidebar with Quick Consultation categories, chat interface with AI response bubbles, input area with disclaimer, expandable citation section (planned), "Upgrade to Pro" placeholder.
2. **Caught a mock-data accuracy risk before shipping** — the Stitch prototype referenced the obsolete Labor Law No. 12 of 2003 as placeholder text; confirmed harmless (no backend connected yet) and recorded that citations must be generated dynamically from retrieved article metadata, never hardcoded.
3. **Built the backend API** — created a FastAPI backend exposing the RAG system via REST, with a `POST /chat` endpoint, FastAPI serving the frontend directly from `/`, CORS configured for frontend communication, and functionality verified through FastAPI's Swagger docs (`/docs`).
4. **Connected the local AI backend end-to-end** — integrated ChromaDB, Groq LLM, and LangChain with FastAPI; resolved all local dependency/environment issues; verified that frontend, backend, Swagger docs, `/chat`, and `/` all operate correctly together as a single FastAPI server (simplified deployment — one server runs the whole app).
5. **Frontend integration (core complete)** — kept the existing HTML/CSS/JS interface from Stitch for the MVP rather than migrating to React (reduces complexity); connected the chat interface to the `/chat` endpoint via JavaScript `fetch()`; implemented dynamic rendering of user and AI messages; added a temporary "جاري التفكير..." loading state; added error handling for failed requests; enabled submission via both the Send button and Enter key; prevented empty submissions; switched to relative API endpoints (`/chat`) since frontend and backend now run under the same server; added request-state management to prevent overlapping simultaneous requests; fixed sidebar navigation so switching consultation categories no longer clears chat history or shows artificial transition screens — conversation is now preserved across category switches.
6. **Functional validation completed** — tested the full browser-to-backend workflow end-to-end; confirmed employment-law questions retrieve correct articles and generate accurate, grounded responses; confirmed multilingual behavior for both Arabic and English; confirmed casual conversation is handled directly by the LLM while legal questions use RAG; confirmed unsupported legal domains are not answered with fabricated information.
7. **Scoping decision (reaffirmed)** — Employment Contracts remains the only fully functional module, powered by the verified Labor Law corpus. Company Formation, Tax Compliance, and Social Insurance remain planned future modules representing product vision without overstating current capability. Social Insurance Law No. 148 of 2019 remains the strongest candidate for the next functional module if time allows.

**Still remaining for Day 3:**
- Dynamically generate and display legal citations from retrieved document metadata (replacing the placeholder citation UI)
- Connect the EN/AR language toggle to actual bilingual UI behavior (currently the backend is multilingual, but the toggle's UI-chrome switching needs to be wired up)
- Disable or mark unsupported sidebar modules as "Coming Soon" while keeping Employment Contracts active
- Improve formatting of legal answers (summaries, bullet points, clearer article references) without changing the underlying RAG pipeline
- Prepare the ChatGPT-vs-Qanoony comparison demo
- Write the project README
- Prepare deployment instructions

---

## How to Explain It When Asked

- **What problem does this solve?** People get confidently wrong legal answers from generic AI; this grounds every answer in real, current law with citations.
- **Why only one law (fully functional)?** Retrieval quality over coverage breadth — the UI shows the broader vision while the working demo stays narrow and accurate.
- **How do you know it's accurate?** Every answer is traceable to a specific article; if the law doesn't cover it, the system refuses instead of guessing — tested and iterated on directly, including catching and fixing a refusal-bypass bug.
- **Is the data current?** Yes — Labor Law 14/2025, in force since Sept 2025, not the outdated 2003 law many tools reference.
- **Is this deployed/live?** It runs as a single local FastAPI server serving both frontend and backend — a full working prototype, not yet deployed to a public host.
- **Why Groq/Llama 3.3?** Fast inference for a smooth live demo, strong multilingual generation, avoids GPU/quantization instability seen in earlier self-hosted attempts.
- **Does it support English and Arabic?** Yes — the backend automatically detects query language and responds accordingly, translating retrieved Arabic legal content into professional English when needed while preserving legal meaning and citation accuracy.
- **Why FastAPI instead of Streamlit?** Chose to keep the polished Stitch-designed frontend as the real UI rather than rebuilding it in Streamlit — FastAPI serves both the API and the static frontend from a single server, keeping deployment simple while preserving full design control.

---

## What the System Should Answer (Employer/Founder-Facing)

### Core question types it should handle well

**Hiring & Contracts**
- What must I legally include in an employment contract?
- Can I hire someone without a written contract?
- Fixed-term vs. unlimited contracts — which should I use?

**Obligations & Costs**
- What am I required to pay an employee if I terminate them?
- How much annual leave am I legally required to give?
- Overtime pay obligations; maximum working hours *(tested — working correctly)*

**Risk & Compliance**
- What happens if I don't register an employment contract properly?
- Mandatory workplace policies (harassment, discrimination)
- Dispute process if an employee files a complaint
- Probation-period termination limits

**Employee Entitlements an Employer Must Know**
- Sick leave rules and compensation
- Maternity leave duration under the new law *(confirmed correct — Article 54)*
- Leave for religious occasions (e.g., Hajj)

### What it should correctly refuse to answer

- GAFI business registration, licensing, company formation
- Tax filing or tax obligations *(tested — working correctly)*
- Minimum wage figures or specific tax brackets — refuses even if a related article discusses the general mechanism *(tested — working correctly after prompt iteration)*
- Government employees/civil servants — new law applies only to private-sector workers
- Other legal domains (real estate, criminal law, unrelated civil disputes)
- Vague/trick questions where the honest answer is "not specified"

### Demo structure

1. Ask a clear in-scope question -> accurate answer + article citation
2. Ask the same question to plain ChatGPT -> shows hedging/guessing/outdated info
3. Ask an out-of-scope question -> system correctly declines instead of guessing
