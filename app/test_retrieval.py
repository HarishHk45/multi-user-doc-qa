"""Smoke-test retrieval and access isolation without calling the OpenAI API."""

from config import USERS, companies_for_user
from ingest import get_embeddings
from langchain_community.vectorstores import FAISS
from config import INDEX_DIR


def load(company_id):
    return FAISS.load_local(
        str(INDEX_DIR / company_id), embeddings, allow_dangerous_deserialization=True
    )


embeddings = get_embeddings()

print("--- Per-user allowed companies ---")
for email in USERS:
    print(email, "->", companies_for_user(email))

print("\n--- Relevance check: NovaPeak revenue question against novapeak index ---")
store = load("novapeak")
hits = store.similarity_search_with_score("What was the Q4 revenue?", k=2)
for doc, score in hits:
    print(f"score={score:.3f} company={doc.metadata['company_name']} :: {doc.page_content[:120]!r}")

print("\n--- Isolation check: Bob (beacon, cascade) must never touch novapeak/dover/everline ---")
allowed = companies_for_user("bob@email.com")
assert "novapeak" not in allowed and "dover" not in allowed and "everline" not in allowed
print("OK: bob's allowed set is", allowed)

print("\n--- Cross-company relevance: Dover robotics question against dover index ---")
store = load("dover")
hits = store.similarity_search_with_score("How many robotic units did they ship?", k=2)
for doc, score in hits:
    print(f"score={score:.3f} company={doc.metadata['company_name']} :: {doc.page_content[:120]!r}")

print("\nAll smoke checks passed.")
