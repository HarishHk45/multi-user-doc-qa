"""Streamlit UI: log in as a dummy user, ask questions, see isolated, conversational answers."""

import streamlit as st

from config import USERS, companies_for_user, company_label
from qa_engine import QAEngine

st.set_page_config(page_title="Multi-User Document Q&A", page_icon="📄", layout="centered")


@st.cache_resource
def get_engine() -> QAEngine:
    return QAEngine()


def render_login() -> None:
    st.title("📄 Multi-User Document Q&A")
    st.caption("Conversational search over earnings-call transcripts, scoped per user.")

    st.subheader("Log in")
    known_emails = list(USERS.keys())
    choice = st.selectbox(
        "Pick a demo user, or choose Other to type any email",
        known_emails + ["Other"],
    )
    email = (
        st.text_input("Email", placeholder="name@email.com")
        if choice == "Other"
        else choice
    )

    if st.button("Log in", type="primary", disabled=not email):
        st.session_state["email"] = email.strip().lower()
        st.rerun()

    with st.expander("Who can see what in this demo"):
        for user_email, companies in USERS.items():
            labels = ", ".join(company_label(c) for c in companies)
            st.write(f"- **{user_email}** → {labels}")


def render_chat() -> None:
    engine = get_engine()
    email = st.session_state["email"]
    allowed = companies_for_user(email)

    with st.sidebar:
        st.markdown(f"**Logged in as**\n\n{email}")
        if allowed:
            st.markdown("**Document access**")
            for company_id in allowed:
                st.write(f"- {company_label(company_id)}")
        else:
            st.warning("This email has no document access configured.")
        st.divider()
        if st.button("New conversation"):
            engine.reset_session(email)
            st.session_state.pop("display_history", None)
            st.rerun()
        if st.button("Log out"):
            del st.session_state["email"]
            st.rerun()

    st.title("📄 Multi-User Document Q&A")

    display_history = st.session_state.setdefault("display_history", [])
    for turn in display_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn.get("sources"):
                with st.expander("Sources"):
                    for src in turn["sources"]:
                        st.markdown(f"**{src['company']}**, page {src['page']}")
                        st.caption(src["excerpt"])

    question = st.chat_input("Ask about the earnings calls you have access to...")
    if question:
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Searching your authorized documents..."):
                result = engine.ask(email, question)
            st.write(result["answer"])
            if result.get("sources"):
                with st.expander("Sources"):
                    for src in result["sources"]:
                        st.markdown(f"**{src['company']}**, page {src['page']}")
                        st.caption(src["excerpt"])
        display_history.append(
            {
                "question": question,
                "answer": result["answer"],
                "sources": result.get("sources", []),
            }
        )


def main() -> None:
    if "email" not in st.session_state:
        render_login()
    else:
        render_chat()


if __name__ == "__main__":
    main()
