# Demo script

This walks through everything the assignment's "Demonstration" section asks for:
logging in as different users, submitting queries and viewing answers, proving
query isolation, and highlighting the conversational follow-up behavior.

Start the app first: `streamlit run app/streamlit_app.py`.

## 0. Show the access-control setup (30 seconds)

Open `app/config.py` and point at `USERS`:

| Email | Can query |
|---|---|
| `alice@email.com` | NovaPeak Technologies |
| `bob@email.com` | Beacon Health Systems, Cascade Energy Partners |
| `charlie@email.com` | Dover Robotics, Everline Logistics |

Say: each user is restricted to one or two companies, simulated with dummy
emails instead of real auth, matching the assignment's own scope.

## 1. Log in as different users

- On the login screen, pick `alice@email.com` from the dropdown and log in.
- Point out the sidebar: it lists exactly the companies that user can access.
- Log out, log in as `bob@email.com`, show the sidebar now lists two different
  companies. Log out again, log in as `charlie@email.com`.

## 2. Submit queries and retrieve answers

As `alice@email.com`, ask:

> What was the Q4 revenue?

Expected: an answer citing **NovaPeak Technologies**, $482 million for Q4
(up 19% year over year). Open the "Sources" expander to show the retrieved
excerpt and page number backing the answer.

## 3. Demonstrate query isolation

This is the core thing to prove — a user cannot retrieve another user's
documents, even by asking about them directly.

- Still as `alice@email.com` (only has NovaPeak access), ask:

  > What was Beacon Health Systems' revenue in Q4?

  Expected: the system says it doesn't have that information in the
  documents available to this user — it will **not** answer with Beacon's
  real figures, because Beacon's index is never loaded for Alice's session.

- Log out, log in as `charlie@email.com` (Dover + Everline only), ask the
  original NovaPeak question again:

  > What was the Q4 revenue?

  Expected: an answer about **Dover Robotics and/or Everline Logistics**
  only — never NovaPeak's $482 million figure, since Charlie has no access
  to that index at all.

- While explaining, open `app/qa_engine.py` and point at `_retrieve()`: it
  only calls `_load_store()` for the company ids in that user's `allowed`
  list. There's no shared index with a filter to get wrong — an
  unauthorized company's vectors are never even loaded into memory for that
  request.

## 4. Highlight the conversational component

As `bob@email.com`, ask:

> What was Beacon's adjusted EBITDA margin in Q4?

Expected: cites Beacon Health Systems, 14.2% (up from 13.6% a year ago).

Then, without repeating "Beacon" or "EBITDA margin", ask the follow-up:

> How does that compare to the prior year?

Expected: the answer correctly reuses the prior turn's context (the 14.2%
vs. 13.6% comparison) because `qa_engine.py` rewrites follow-ups into a
standalone question using the stored conversation history before
retrieving anything. Click "New conversation" afterward and show that a
repeated "how does that compare" with no prior turn now gets a generic
"I don't have enough context" style answer, proving history was actually
being used, not guessed.

## 5. Simultaneous multi-user access

Open a second browser tab (or an incognito window), log in as a different
user there, and run a query in both tabs. Point out:

- Each browser tab has its own Streamlit session (`st.session_state`), so
  the displayed chat history never mixes between tabs.
- Server-side, `QAEngine` keeps one conversation history per email
  (`_sessions` dict in `qa_engine.py`), so even two tabs logged in as the
  *same* user would correctly share one running conversation, while two
  different users never do.

## Recap checklist (matches the assignment's demonstration bullets)

- [ ] Logged in as multiple different users
- [ ] Submitted a query and showed the retrieved answer + source excerpt
- [ ] Showed a user being correctly denied an answer about a company they
      don't have access to
- [ ] Showed a follow-up question resolve using prior conversation context
- [ ] Showed two users' sessions running without interfering with each other
