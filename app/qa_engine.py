"""Per-user conversational retrieval over access-controlled company indexes."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.language_models.chat_models import BaseChatModel

from config import INDEX_DIR, USERS, companies_for_user
from ingest import get_embeddings

load_dotenv()


def get_llm() -> BaseChatModel:
    """LLM_PROVIDER selects the backend; defaults to OpenAI.

    Set LLM_PROVIDER=anthropic to use Claude instead, which avoids needing a
    separate OpenAI account if you already have an Anthropic API key.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model="claude-haiku-5-5", temperature=0)
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model="gpt-4o-mini", temperature=0)

CONDENSE_PROMPT = """Given the conversation history and a follow-up question, \
rewrite the follow-up question as a standalone question that makes sense \
without the history. If the follow-up question is already standalone, return \
it unchanged. Do not answer the question, only rewrite it.

Conversation history:
{history}

Follow-up question: {question}

Standalone question:"""

ANSWER_PROMPT = """You are a financial-results assistant. Answer the user's \
question using ONLY the excerpts below, which come from earnings call \
transcripts the user is authorized to see. If the excerpts do not contain the \
answer, say you don't have that information in the available documents. Cite \
the company name for any figure you state.

Conversation so far:
{history}

Excerpts:
{context}

Question: {question}

Answer:"""


@dataclass
class ChatTurn:
    question: str
    answer: str


@dataclass
class UserSession:
    email: str
    history: list[ChatTurn] = field(default_factory=list)

    def history_text(self, max_turns: int = 4) -> str:
        if not self.history:
            return "(no previous turns)"
        recent = self.history[-max_turns:]
        return "\n".join(f"User: {t.question}\nAssistant: {t.answer}" for t in recent)


class QAEngine:
    """Owns the embedding model, per-company FAISS stores, the LLM, and all
    per-user chat sessions. One process-wide instance is shared by the
    Streamlit app; isolation between users is enforced by only ever touching
    the FAISS stores for companies that specific user is allowed to see.
    """

    def __init__(self) -> None:
        self._embeddings = get_embeddings()
        self._llm = get_llm()
        self._store_cache: dict[str, FAISS] = {}
        self._sessions: dict[str, UserSession] = {}

    def _load_store(self, company_id: str) -> FAISS:
        if company_id not in self._store_cache:
            path = INDEX_DIR / company_id
            if not path.exists():
                raise FileNotFoundError(
                    f"no index for {company_id}; run ingest.py first"
                )
            self._store_cache[company_id] = FAISS.load_local(
                str(path), self._embeddings, allow_dangerous_deserialization=True
            )
        return self._store_cache[company_id]

    def session_for(self, email: str) -> UserSession:
        key = email.strip().lower()
        if key not in self._sessions:
            self._sessions[key] = UserSession(email=key)
        return self._sessions[key]

    def reset_session(self, email: str) -> None:
        self._sessions[email.strip().lower()] = UserSession(email=email.strip().lower())

    def is_known_user(self, email: str) -> bool:
        return email.strip().lower() in USERS

    def _condense(self, session: UserSession, question: str) -> str:
        if not session.history:
            return question
        prompt = CONDENSE_PROMPT.format(
            history=session.history_text(), question=question
        )
        result = self._llm.invoke(prompt)
        return result.content.strip() or question

    def _retrieve(
        self, standalone_question: str, allowed_companies: list[str], k: int = 4
    ) -> list[tuple[Document, float]]:
        scored: list[tuple[Document, float]] = []
        for company_id in allowed_companies:
            store = self._load_store(company_id)
            scored.extend(store.similarity_search_with_score(standalone_question, k=k))
        # FAISS score is L2 distance here: lower means more similar.
        scored.sort(key=lambda pair: pair[1])
        return scored[:k]

    def ask(self, email: str, question: str) -> dict:
        allowed = companies_for_user(email)
        session = self.session_for(email)

        if not allowed:
            answer = (
                "Your account has no documents assigned, so there is nothing "
                "I'm authorized to search for you."
            )
            session.history.append(ChatTurn(question=question, answer=answer))
            return {"answer": answer, "sources": []}

        standalone_question = self._condense(session, question)
        results = self._retrieve(standalone_question, allowed)

        if not results:
            answer = "I couldn't find anything relevant in the documents you have access to."
            session.history.append(ChatTurn(question=question, answer=answer))
            return {"answer": answer, "sources": []}

        context = "\n\n".join(
            f"[{doc.metadata.get('company_name')} | page {doc.metadata.get('page', 0) + 1}]\n{doc.page_content}"
            for doc, _ in results
        )
        prompt = ANSWER_PROMPT.format(
            history=session.history_text(), context=context, question=question
        )
        result = self._llm.invoke(prompt)
        answer = result.content.strip()

        sources = [
            {
                "company": doc.metadata.get("company_name"),
                "page": doc.metadata.get("page", 0) + 1,
                "excerpt": doc.page_content[:280],
            }
            for doc, _ in results
        ]

        session.history.append(ChatTurn(question=question, answer=answer))
        return {"answer": answer, "sources": sources, "standalone_question": standalone_question}
