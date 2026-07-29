# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Challenge (June–July) 2026
 
> 🏆 This repository is my official submission for the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.
 
## 👤 Participant
 
| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        | Omar                                 |
| Project Name     | Qanoony (قانوني)                     |
| GitHub Username  | omardiab9951                         |
| Challenge Batch  | June–July 2026                       |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |
 
---
 
# 📖 Project Overview
 
**Qanoony (قانوني)** is a bilingual (English/Arabic) AI legal assistant platform built for Egyptian employers, startup founders, and small business owners. It answers real questions about employer obligations under Egyptian law — grounded strictly in verified, current legal text rather than a model's general training knowledge.
 
The core problem it solves: generic AI chatbots answer legal questions *confidently even when wrong*, since they have no grounding in actual Egyptian law and can cite the wrong article, use outdated law, or blend in rules from other countries. Qanoony uses Retrieval-Augmented Generation (RAG) to ensure every answer is retrieved from real legal source text, cited to the specific article, and refuses to answer rather than guess when a question falls outside its current knowledge base.
 
The platform is built with a modular, multi-domain architecture — each legal domain (Employment Law, Company Formation, and future domains) is powered by its own isolated knowledge base and retrieval pipeline, connected through an intelligent router.
 
This is a **full working prototype**, demonstrating a complete end-to-end pipeline — from raw legal text to a deployed, interactive chat interface — rather than a hosted production system.
 
---
 
# ✨ Features
 
* **Grounded, cited legal answers** — every response is generated only from retrieved legal text and cites the specific source article, preventing hallucinated or fabricated legal information
* **Reliable refusal behavior** — the system explicitly declines to answer questions outside its verified knowledge base (e.g., tax figures, minimum wage amounts, unsupported legal domains) instead of guessing
* **Bilingual support (English/Arabic)** — automatic language detection responds in the user's language, translating retrieved Arabic legal content into professional English while preserving legal accuracy
* **Modular multi-domain architecture** — Employment Law and Company Formation are powered by fully isolated knowledge bases and retrieval modules, routed intelligently based on user-selected module or keyword classification
* **Intelligent conversational routing** — casual conversation (greetings, capability questions) is handled directly by the LLM, while legal questions are routed through the full RAG pipeline
* **Interactive chat interface** — a custom-designed web UI with module switching, preserved conversation history, expandable source citations, and a responsive, accessible design
---
 
# 🛠️ Technologies Used
 
* **LLM:** Groq (Llama 3.3 70B) — fast inference via Groq's API
* **Embeddings:** BAAI/bge-m3 (multilingual embedding model, via Hugging Face)
* **Vector Database:** ChromaDB — isolated collections per legal domain
* **Orchestration:** LangChain (LCEL — LangChain Expression Language)
* **Backend:** FastAPI (REST API + static frontend serving)
* **Frontend:** HTML, CSS (Tailwind), JavaScript — designed with Google Stitch, refined for accessibility and responsiveness
* **Data Sources:** Egyptian Labor Law No. 14 of 2025 (Arabic Wikisource), Companies Law No. 159 of 1981, Investment Law No. 72 of 2017, GAFI Investor Services Guide
---
 
# ⚙️ Installation
 
1. Clone the repository:
```bash
   git clone https://github.com/omardiab9951/Qanoony.git
   cd Qanoony
```
 
2. Install backend dependencies:
```bash
   pip install -r requirements.txt
```
 
3. Set your Groq API key as an environment variable:
```bash
   # Mac/Linux
   export GROQ_API_KEY="your_api_key_here"
 
   # Windows
   set GROQ_API_KEY=your_api_key_here
```
 
4. Ensure the pre-built ChromaDB knowledge bases are present in their expected data directories (Employment Law and Company Formation).
5. Run the FastAPI server:
```bash
   uvicorn backend.main:app --reload
```
 
6. Open your browser to `http://localhost:8000` to access the application.
---
 
# 🚀 Usage
 
1. Open the app in your browser — the interface loads in English by default, with an Arabic toggle available in the header.
2. Select a legal module from the sidebar (**Employment Law** or **Company Formation**). Other modules (Tax Compliance, Social Insurance) are marked "Coming Soon."
3. Type a question in the chat input — e.g., *"What are the requirements for a fixed-term employment contract in Egypt?"*
4. The assistant retrieves the relevant legal article(s), generates a grounded answer, and displays a citation you can expand to see the original legal text.
5. Ask an out-of-scope question (e.g., a tax question) to see the assistant correctly decline rather than guess.
6. Switch modules at any point — conversation history is preserved.
---
 
# 📸 Demo
 
<img width="947" height="437" alt="image" src="https://github.com/user-attachments/assets/a192c7b1-5dc4-4d23-bf1d-4ada59e20d43" />
 
---
 
# 📈 Results
 
* Built and verified a 301-article Egyptian Labor Law knowledge base with a custom article-boundary chunking pipeline, achieving zero duplicate or malformed chunks after full integrity verification
* Engineered and iteratively tested a strict grounding prompt, identifying and fixing a real refusal-bypass failure mode (the model explaining around a refusal instead of declining cleanly) through direct testing
* Validated correct system behavior across in-scope questions (accurate, cited answers), out-of-scope questions (clean refusals), and edge cases (topics mentioned in context but missing the specific requested fact)
* Migrated the full RAG pipeline from a Kaggle notebook environment to a locally running, production-shaped FastAPI application
* Extended the platform from a single-domain assistant to a modular, multi-domain architecture with an intelligent routing layer distinguishing Employment Law and Company Formation queries
---
 
# 🔮 Future Improvements
 
* Complete indexing and validation of the Company Formation knowledge base
* Add conversational memory for natural multi-turn follow-up questions
* Expand to additional legal domains (Tax Compliance, Social Insurance)
* Broaden automated test coverage across both legal domains and languages
* Deploy to a public hosting environment with authentication and usage monitoring
* Improve citation UI with richer source previews and article cross-referencing
---
 
# 📚 About the Challenge
 
This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Challenge (June–July) 2026**.
 
[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the challenge encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.
 
For more information about the challenge, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.
 
---
 
# 📄 License
 
This project is shared for educational and portfolio purposes.
