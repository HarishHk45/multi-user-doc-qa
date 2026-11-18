"""Static configuration: companies, sample documents, and dummy user access control."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
INDEX_DIR = BASE_DIR / "data" / "index"

# Fictional companies used for the demo dataset. Names are invented so the
# sample transcripts are clearly not real filings for a real company.
COMPANIES = {
    "novapeak": {
        "name": "NovaPeak Technologies",
        "file": "novapeak_q4_earnings_call.pdf",
    },
    "beacon": {
        "name": "Beacon Health Systems",
        "file": "beacon_q4_earnings_call.pdf",
    },
    "cascade": {
        "name": "Cascade Energy Partners",
        "file": "cascade_q4_earnings_call.pdf",
    },
    "dover": {
        "name": "Dover Robotics",
        "file": "dover_q4_earnings_call.pdf",
    },
    "everline": {
        "name": "Everline Logistics",
        "file": "everline_q4_earnings_call.pdf",
    },
}

# Dummy user directory: email -> list of company ids the user may query.
# This simulates auth/access-control without building real user management.
USERS = {
    "alice@email.com": ["novapeak"],
    "bob@email.com": ["beacon", "cascade"],
    "charlie@email.com": ["dover", "everline"],
}


def companies_for_user(email: str) -> list[str]:
    return USERS.get(email.strip().lower(), [])


def company_label(company_id: str) -> str:
    return COMPANIES.get(company_id, {}).get("name", company_id)
