"""Generate synthetic Q4 earnings-call transcript PDFs for the demo dataset.

These are invented transcripts for fictional companies, built so the retrieval
and access-control demo has realistic, distinct numbers to query per company.
They are not real filings and should not be treated as real company data.
"""

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from config import COMPANIES, PDF_DIR

TRANSCRIPTS: dict[str, dict] = {
    "novapeak": {
        "title": "NovaPeak Technologies (NPTX) Q4 FY2025 Earnings Call Transcript",
        "paragraphs": [
            "Operator: Good morning, and welcome to the NovaPeak Technologies "
            "fourth quarter fiscal year 2025 earnings conference call.",
            "Priya Anand, Chief Executive Officer: Thank you all for joining. "
            "Q4 was a strong finish to the year for NovaPeak. We reported revenue "
            "of $482 million for the fourth quarter, up 19% year over year, driven "
            "by continued demand for our cloud security platform. Full fiscal year "
            "2025 revenue came in at $1.74 billion, up 17% from fiscal 2024.",
            "Diluted earnings per share for the quarter were $1.12, compared to "
            "$0.89 in the fourth quarter of fiscal 2024. Our subscription "
            "renewal rate held steady at 96%, and we closed the quarter with "
            "over 3,100 enterprise customers, an increase of 240 from the prior "
            "quarter.",
            "Marcus Lee, Chief Financial Officer: Gross margin for the quarter "
            "was 78.4%, roughly flat sequentially. Operating cash flow for the "
            "quarter was $146 million. We ended the quarter with $890 million in "
            "cash and short-term investments and no outstanding debt.",
            "Looking ahead, we are guiding first quarter fiscal 2026 revenue to a "
            "range of $470 million to $485 million, and we expect full fiscal "
            "2026 revenue in the range of $1.95 billion to $2.0 billion, "
            "implying growth of roughly 12% to 15%.",
            "Analyst Q&A: An analyst asked about pricing pressure from new "
            "entrants in the cloud security market. Priya Anand responded that "
            "NovaPeak's platform breadth and existing customer integrations "
            "continue to support premium pricing, and that churn remains at "
            "historically low levels.",
            "A second analyst asked about headcount plans for fiscal 2026. "
            "Marcus Lee said the company expects to grow headcount by "
            "approximately 8%, concentrated in research and development and "
            "international sales.",
            "Operator: This concludes the NovaPeak Technologies fourth quarter "
            "fiscal year 2025 earnings call. Thank you for joining.",
        ],
    },
    "beacon": {
        "title": "Beacon Health Systems (BHSY) Q4 FY2025 Earnings Call Transcript",
        "paragraphs": [
            "Operator: Welcome to the Beacon Health Systems fourth quarter "
            "fiscal 2025 earnings call.",
            "Daniel Ortiz, Chief Executive Officer: Beacon delivered fourth "
            "quarter revenue of $612 million, up 8% year over year, led by "
            "growth in our outpatient services division. Full year revenue was "
            "$2.31 billion, up 6% from fiscal 2024.",
            "Adjusted EBITDA margin for the quarter was 14.2%, compared to 13.6% "
            "a year ago, reflecting continued cost discipline across our "
            "facilities network. Same-facility patient volumes grew 3.4% in the "
            "quarter.",
            "Grace Whitfield, Chief Financial Officer: Diluted earnings per "
            "share for the quarter were $0.74, up from $0.61 in the prior-year "
            "quarter. We generated $98 million in free cash flow during the "
            "quarter and reduced net debt by $40 million.",
            "For fiscal 2026, we expect revenue growth of 5% to 7%, with "
            "adjusted EBITDA margin expansion of 30 to 50 basis points, as labor "
            "cost inflation continues to moderate.",
            "Analyst Q&A: An analyst asked about staffing costs. Grace Whitfield "
            "noted that contract labor expense fell to 6.1% of total labor cost "
            "in the quarter, down from 9.8% a year earlier, as more roles were "
            "filled with permanent staff.",
            "A second analyst asked about acquisition plans. Daniel Ortiz said "
            "Beacon continues to evaluate tuck-in acquisitions of outpatient "
            "clinics in its existing markets but has no material transactions "
            "pending disclosure.",
            "Operator: This concludes the Beacon Health Systems fourth quarter "
            "earnings call.",
        ],
    },
    "cascade": {
        "title": "Cascade Energy Partners (CEPX) Q4 FY2025 Earnings Call Transcript",
        "paragraphs": [
            "Operator: Good afternoon, and welcome to the Cascade Energy "
            "Partners fourth quarter fiscal 2025 earnings call.",
            "Robert Hale, Chief Executive Officer: Fourth quarter revenue was "
            "$1.08 billion, down 4% year over year, primarily due to lower "
            "average realized natural gas prices, partially offset by higher "
            "production volumes. Full year revenue was $4.42 billion.",
            "Average daily production in the quarter was 1.42 billion cubic "
            "feet equivalent per day, up 6% year over year. Realized natural "
            "gas price averaged $2.65 per thousand cubic feet, compared to "
            "$3.05 in the prior-year quarter.",
            "Elena Kowalski, Chief Financial Officer: Adjusted EBITDA for the "
            "quarter was $540 million, and diluted earnings per share were "
            "$0.58, compared to $0.71 a year ago. We returned $120 million to "
            "shareholders through dividends and buybacks during the quarter.",
            "For fiscal 2026, Cascade is guiding capital expenditures to a "
            "range of $1.1 billion to $1.2 billion, with production growth of "
            "4% to 6%, assuming current commodity price levels.",
            "Analyst Q&A: An analyst asked about hedging coverage for fiscal "
            "2026. Elena Kowalski said approximately 55% of expected 2026 gas "
            "production is hedged at an average floor price of $3.10 per "
            "thousand cubic feet.",
            "A second analyst asked about pipeline takeaway capacity. Robert "
            "Hale said Cascade has secured firm transportation for "
            "substantially all expected 2026 production and does not "
            "anticipate bottlenecks.",
            "Operator: This concludes the Cascade Energy Partners earnings "
            "call.",
        ],
    },
    "dover": {
        "title": "Dover Robotics (DVRB) Q4 FY2025 Earnings Call Transcript",
        "paragraphs": [
            "Operator: Welcome to the Dover Robotics fourth quarter fiscal "
            "2025 earnings conference call.",
            "Aisha Rahman, Chief Executive Officer: Fourth quarter revenue was "
            "$296 million, up 27% year over year, driven by strong demand for "
            "our warehouse automation systems. Full year revenue reached $1.02 "
            "billion, our first year above $1 billion.",
            "We shipped 1,840 robotic units in the quarter, compared to 1,260 "
            "in the prior-year quarter. Backlog at quarter end stood at $410 "
            "million, up from $340 million last quarter.",
            "Nathan Pierce, Chief Financial Officer: Gross margin was 41.8%, "
            "up from 38.5% a year ago, reflecting manufacturing scale and "
            "component cost reductions. Diluted earnings per share were $0.47, "
            "compared to $0.21 in the prior-year quarter.",
            "For fiscal 2026, we expect revenue of $1.25 billion to $1.32 "
            "billion, representing growth of 22% to 29%, and we expect gross "
            "margin to approach 43% by year end.",
            "Analyst Q&A: An analyst asked about supply chain constraints on "
            "key components. Nathan Pierce said lead times for servo motors "
            "have normalized to 8 weeks from a peak of 22 weeks last year.",
            "A second analyst asked about competition from new entrants in "
            "warehouse robotics. Aisha Rahman said Dover's installed base and "
            "software integration advantage continue to support win rates "
            "above 60% in competitive deals.",
            "Operator: This concludes the Dover Robotics fourth quarter "
            "earnings call.",
        ],
    },
    "everline": {
        "title": "Everline Logistics (EVLN) Q4 FY2025 Earnings Call Transcript",
        "paragraphs": [
            "Operator: Good morning, and welcome to the Everline Logistics "
            "fourth quarter fiscal 2025 earnings call.",
            "Carlos Mendoza, Chief Executive Officer: Fourth quarter revenue "
            "was $1.86 billion, up 3% year over year, as freight volume growth "
            "offset continued softness in spot market rates. Full year revenue "
            "was $7.21 billion.",
            "Our ground parcel segment grew volume 9% year over year, while "
            "freight brokerage revenue declined 5% due to lower rate per "
            "shipment. Operating ratio for the quarter was 88.6%, compared to "
            "90.1% a year ago.",
            "Helen Dubois, Chief Financial Officer: Diluted earnings per share "
            "were $1.34, up from $1.05 in the prior-year quarter. We generated "
            "$310 million in free cash flow and repurchased $150 million of "
            "shares during the quarter.",
            "For fiscal 2026, we expect low single digit revenue growth and "
            "continued operating ratio improvement of roughly 100 basis points, "
            "as network efficiency initiatives continue to roll out.",
            "Analyst Q&A: An analyst asked about fuel surcharge trends. Helen "
            "Dubois said fuel surcharge revenue declined 11% year over year in "
            "line with lower average diesel prices, with no material margin "
            "impact since surcharges are a pass-through.",
            "A second analyst asked about e-commerce demand trends. Carlos "
            "Mendoza said residential delivery volume grew 14% year over year "
            "and remains the fastest growing part of the network.",
            "Operator: This concludes the Everline Logistics fourth quarter "
            "earnings call.",
        ],
    },
}


def build_pdf(company_id: str) -> Path:
    meta = COMPANIES[company_id]
    transcript = TRANSCRIPTS[company_id]
    out_path = PDF_DIR / meta["file"]

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TranscriptTitle", parent=styles["Title"], fontSize=14, spaceAfter=18
    )
    body_style = ParagraphStyle(
        "TranscriptBody", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=10
    )

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=LETTER,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title=transcript["title"],
    )

    story = [Paragraph(transcript["title"], title_style), Spacer(1, 6)]
    for para in transcript["paragraphs"]:
        story.append(Paragraph(para, body_style))

    doc.build(story)
    return out_path


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for company_id in COMPANIES:
        path = build_pdf(company_id)
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
