from qanoony.backend.rag.employment.rag import ask_qanoony

question = "ما هي مدة إجازة الوضع؟"

response = ask_qanoony(question)

print("\nQuestion:")
print(question)

print("\nAnswer:")
print(response)
