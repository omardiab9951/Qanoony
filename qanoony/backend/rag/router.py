from qanoony.backend.rag.company_formation.rag import ask_company
from qanoony.backend.rag.employment.rag import ask_qanoony


EMPLOYMENT_KEYWORDS = {
    "employee",
    "worker",
    "contract",
    "salary",
    "leave",
    "termination",
}

COMPANY_KEYWORDS = {
    "company",
    "establish",
    "register",
    "llc",
    "shareholder",
    "capital",
    "incorporation",
}

OUT_OF_SCOPE_MESSAGE = (
    "I'm currently specialized in Employment Law and Company Formation. "
    "This topic is outside my available knowledge base."
)


def route_question(question: str, module: str | None = None):
    if module == "company":
        return ask_company(question)
    if module == "employment":
        return ask_qanoony(question)

    normalized = question.lower()
    if any(keyword in normalized for keyword in COMPANY_KEYWORDS):
        return ask_company(question)
    if any(keyword in normalized for keyword in EMPLOYMENT_KEYWORDS):
        return ask_qanoony(question)
    return OUT_OF_SCOPE_MESSAGE
