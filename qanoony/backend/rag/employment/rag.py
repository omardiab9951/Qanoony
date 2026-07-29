import os
import re
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

print("Loading Groq LLM...")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

print("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu", "local_files_only": True},
    encode_kwargs={"normalize_embeddings": True},
)

print("Loading ChromaDB...")
from qanoony.backend.config import EMPLOYMENT_CHROMA_DIR

db = Chroma(
    persist_directory=str(EMPLOYMENT_CHROMA_DIR),
    embedding_function=embeddings,
    collection_name="qanoony_law_db",
)
retriever = db.as_retriever(search_kwargs={"k": 3})

PROMPT = PromptTemplate.from_template(
    """
أنت مساعد قانوني خبير ومتخصص في قانون العمل المصري رقم 14 لسنة 2025.

اكتشف لغة السؤال تلقائياً.
- إذا كان السؤال بالعربية، أجب بالعربية.
- إذا كان السؤال بالإنجليزية، أجب بالإنجليزية باحترافية.
- لا تخلط العربية والإنجليزية إلا إذا طلب المستخدم صراحة استجابة ثنائية اللغة.

السياق:
{context}

السؤال:
{input}

التعليمات:
1. أجب فقط باستخدام المعلومات الموجودة في السياق.
2. إذا كان السؤال بالعربية، احتفظ بالإجابة بالعربية.
3. إذا كان السؤال بالإنجليزية، ترجم المعلومات القانونية العربية إلى إنجليزية مهنية مع الحفاظ على المعنى القانوني.
4. ابدأ بملخص من جملة واحدة يجيب مباشرة على السؤال.
5. اعرض الشروط أو الحقوق أو الالتزامات القانونية في نقاط مختصرة عند وجود أكثر من تفصيل.
6. اذكر المادة بهذه الصيغة: "Article X of the Egyptian Labor Law No. 14 of 2025" مع استبدال X برقم المادة.
7. اختم بجملة قصيرة عند الحاجة، بدون إضافة أي معلومة غير موجودة في السياق.
8. إذا لم تجد الإجابة في السياق فقل:
"هذا الموضوع غير مغطى في نطاق قانون العمل الحالي، ويفضل استشارة جهة مختصة."
9. لا تخترع أي معلومة.
10. لا تستخدم معرفتك السابقة.

الإجابة:
"""
)


def format_docs(docs):
    return "\n\n".join(
        f"المادة: {doc.metadata.get('article', 'غير معروف')}\n{doc.page_content}"
        for doc in docs
    )


def normalize_message(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(r"[^\w\u0600-\u06FF\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


LEGAL_KEYWORDS = {
    "article",
    "articles",
    "law",
    "legal",
    "labor",
    "labour",
    "work",
    "worker",
    "employee",
    "employer",
    "employment",
    "contract",
    "salary",
    "wage",
    "pay",
    "payment",
    "leave",
    "vacation",
    "sick",
    "maternity",
    "termination",
    "fire",
    "firing",
    "dismiss",
    "dismissal",
    "resign",
    "resignation",
    "notice",
    "overtime",
    "hours",
    "working",
    "obligation",
    "rights",
    "penalty",
    "penalties",
    "probation",
    "insurance",
    "dispute",
    "court",
    "policy",
    "قانون",
    "قانوني",
    "العمل",
    "عامل",
    "العامل",
    "موظف",
    "الموظف",
    "صاحب",
    "صاحب العمل",
    "شركة",
    "عقد",
    "العقد",
    "راتب",
    "أجر",
    "اجر",
    "مرتب",
    "إجازة",
    "اجازة",
    "مرضية",
    "وضع",
    "فصل",
    "إنهاء",
    "انهاء",
    "استقالة",
    "إخطار",
    "اخطار",
    "ساعات",
    "إضافي",
    "اضافي",
    "التزامات",
    "حقوق",
    "غرامة",
    "عقوبة",
    "جزاء",
    "تأمين",
    "تامين",
    "نزاع",
    "محكمة",
    "مادة",
    "المادة",
}

GENERAL_CHAT_PROMPT = PromptTemplate.from_template(
    """
You are Qanoony, the legal AI assistant.

Handle only greetings, thanks, capability questions, and casual conversation.
Stay in character as Qanoony at all times.

Language rules:
1. Detect the language of the user's message.
2. If the user writes in Arabic, respond entirely in Arabic. Use Modern Standard Arabic unless the user clearly uses another Arabic dialect.
3. If the user writes in English, respond entirely in English.
4. Never translate greetings into another language.
5. Never answer an Arabic greeting in English.
6. Never answer in Spanish, French, or any unrelated language.
7. Never mix languages in one response.

Style rules:
1. For greetings, thanks, and casual conversation, respond in 1-2 short sentences.
2. Be friendly and professional.
3. When the user greets you, introduce yourself naturally as Qanoony.
4. Use deterministic wording. For the same greeting, give the same response.
5. Do not provide legal advice unless the user asks a legal question.

Use these exact responses for these exact messages:
- "Hello": "Hello! I'm Qanoony, your legal assistant. How can I help you today?"
- "Hi": "Hello! I'm Qanoony, your legal assistant. How can I help you today?"
- "Good morning": "Good morning! I'm Qanoony, your legal assistant. How can I help you today?"
- "السلام عليكم": "وعليكم السلام! أنا قانوني، مساعدك القانوني. كيف يمكنني مساعدتك اليوم؟"
- "مرحبًا": "أهلاً بك! أنا قانوني، مساعدك القانوني. كيف يمكنني مساعدتك اليوم؟"
- "شكراً": "على الرحب والسعة."

Examples:
English greeting: "Hello! I'm Qanoony, your legal assistant. How can I help you today?"
Arabic greeting: "أهلاً بك! أنا قانوني، مساعدك القانوني. كيف يمكنني مساعدتك اليوم؟"

User message:
{input}

Response:
"""
)


def is_legal_query(text: str) -> bool:
    """Conservatively route anything employment-law-like through RAG."""
    normalized = normalize_message(text)
    return any(keyword in normalized for keyword in LEGAL_KEYWORDS)


def chat_without_rag(text: str) -> str:
    """Handle casual conversation without touching ChromaDB or the retriever."""
    return general_chat_chain.invoke(text)


rag_chain = (
    RunnableParallel({"context": retriever | format_docs, "input": RunnablePassthrough()})
    .assign(answer=PROMPT | llm | StrOutputParser())
)
general_chat_chain = GENERAL_CHAT_PROMPT | llm | StrOutputParser()

print("RAG is ready!")


def ask_qanoony(question: str):
    try:
        if not is_legal_query(question):
            return chat_without_rag(question)

        result = rag_chain.invoke(question)
        if isinstance(result, dict) and "answer" in result:
            return result["answer"]
        return "عذراً، لم يتم التوصل إلى إجابة واضحة من نموذج الاسترجاع."
    except Exception as e:
        return f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
