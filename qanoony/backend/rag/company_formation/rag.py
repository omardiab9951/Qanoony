import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
os.environ.setdefault("HF_HUB_OFFLINE", "1")

print("Loading Company Formation Groq LLM...")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

print("Loading Company Formation Embedding Model...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu", "local_files_only": True},
    encode_kwargs={"normalize_embeddings": True},
)

print("Loading Company Formation ChromaDB...")
from qanoony.backend.config import COMPANY_FORMATION_CHROMA_DIR

db = Chroma(
    persist_directory=str(COMPANY_FORMATION_CHROMA_DIR),
    embedding_function=embeddings,
    collection_name="company_formation_db",
)
retriever = db.as_retriever(search_kwargs={"k": 4})

PROMPT = PromptTemplate.from_template(
    """
You are Qanoony, a legal assistant specialized in Egyptian company formation.

Supported topics:
- Company establishment
- Company registration
- Companies Law 159/1981
- Investment Law 72/2017
- Required documents
- Shareholders
- Capital
- Board of Directors
- Commercial Register
- Tax Card
- GAFI
- Company compliance

Context:
{context}

Question:
{input}

Instructions:
1. Answer only using information found in the context.
2. Do not use outside knowledge.
3. If the answer is not found in the context, say:
"This information is not available in the Company Formation knowledge base."
4. Keep the answer clear and practical.
5. Mention source document names and page numbers when available.

Answer:
"""
)


def format_docs(docs):
    return "\n\n".join(
        "\n".join(
            [
                f"Source: {doc.metadata.get('source', 'unknown')}",
                f"Page: {doc.metadata.get('page_label', doc.metadata.get('page', 'unknown'))}",
                doc.page_content,
            ]
        )
        for doc in docs
    )


company_chain = (
    RunnableParallel({"context": retriever | format_docs, "input": RunnablePassthrough()})
    .assign(answer=PROMPT | llm | StrOutputParser())
)

print("Company Formation RAG is ready!")

ENGLISH_GREETING = (
    "Hello! I'm Qanoony, your legal assistant. I can help you with Egyptian "
    "company formation, registration procedures, and corporate legal requirements."
)
ARABIC_GREETING = (
    "أهلاً بك! أنا قانوني، مساعدك القانوني. يمكنني مساعدتك في تأسيس الشركات "
    "وإجراءات التسجيل والمتطلبات القانونية للشركات في مصر."
)


def ask_company(question: str):
    normalized = question.strip().lower()
    if normalized in {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"}:
        return ENGLISH_GREETING
    if normalized in {"مرحبا", "مرحبًا", "أهلا", "أهلاً", "السلام عليكم"}:
        return ARABIC_GREETING

    try:
        result = company_chain.invoke(question)
        if isinstance(result, dict) and "answer" in result:
            return result["answer"]
        return "This information is not available in the Company Formation knowledge base."
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
