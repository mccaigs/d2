from app.models.chat import SourceChip
from app.models.tender import TenderAnalysis
from app.services.tender_parser import parse_tender_text


FOLLOW_UPS = [
    "What evidence do we need to support this claim?",
    "Identify missing submission requirements",
    "What are the likely compliance risks?",
    "Summarise the buyer requirements",
]


def analyse_tender_text(text: str) -> TenderAnalysis:
    return parse_tender_text(text)


def build_tender_analysis_answer(analysis: TenderAnalysis) -> str:
    lines = [
        "**Opportunity summary**",
        analysis.opportunity_summary,
        "",
        "**Buyer requirements**",
    ]

    if analysis.buyer_requirements:
        lines.extend(f"- {item.text}" for item in analysis.buyer_requirements[:6])
    else:
        lines.append(
            "- No clear buyer requirements were extracted. Paste the full tender specification for a stronger read."
        )

    lines.extend(["", "**Submission requirements**"])
    if analysis.submission_requirements:
        lines.extend(f"- {item.text}" for item in analysis.submission_requirements[:6])
    else:
        lines.append("- No explicit submission requirements were extracted from the pasted text.")

    lines.extend(["", "**Compliance risks**"])
    for risk in analysis.compliance_risks[:6]:
        evidence = (
            f" Evidence needed: {', '.join(risk.evidence_needed)}."
            if risk.evidence_needed
            else ""
        )
        lines.append(f"- **{risk.area}:** {risk.note}{evidence}")

    lines.extend(["", "**Evidence needed**"])
    if analysis.evidence_needed:
        lines.extend(f"- **{need.label}:** {need.reason}" for need in analysis.evidence_needed[:6])
    else:
        lines.append(
            "- No explicit evidence asks were found. Treat this as low confidence until the full tender pack is available."
        )

    lines.extend([
        "",
        "**Bid readiness score**",
        f"- **{analysis.readiness.score}/100:** {analysis.readiness.label}",
    ])
    for label, score in analysis.readiness.dimensions.items():
        display = label.replace("_", " ").title()
        lines.append(f"- {display}: {score}/100")

    lines.extend(["", "**Recommended next step**", f"- {recommended_next_step(analysis)}"])

    return "\n".join(lines)


def recommended_next_step(analysis: TenderAnalysis) -> str:
    if analysis.readiness.label == "Bid-ready with checks":
        return "Build the compliance matrix and map each draft claim to an approved evidence item."
    if analysis.readiness.label == "Review before bid":
        return "Resolve blocker risks and missing evidence before committing bid effort."
    return "Treat this as a cautious no-bid unless the missing capability and compliance evidence can be supplied."


def tender_source_chips(analysis: TenderAnalysis) -> list[SourceChip]:
    chips = [
        SourceChip(label="Pasted Tender Text", category="procurement"),
        SourceChip(label="Compliance Rules", category="compliance"),
        SourceChip(label="Scoring Rules", category="scoring"),
    ]
    if analysis.evidence_needed:
        chips.append(SourceChip(label="Evidence Categories", category="proof"))
    if analysis.submission_requirements:
        chips.append(SourceChip(label="Submission Requirements", category="workflows"))
    return chips
