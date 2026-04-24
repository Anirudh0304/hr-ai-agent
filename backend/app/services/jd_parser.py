import re
from typing import List

from ..models import JobDescriptionInput, ParsedJD


SKILL_CATALOG = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "postgresql",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "fastapi",
    "flask",
    "machine learning",
    "nlp",
    "llm",
    "data analysis",
    "scikit-learn",
    "pytorch",
    "tensorflow",
    "communication",
    "leadership",
}

OPTIONAL_MARKERS = ["nice to have", "good to have", "preferred", "plus"]
SENIORITY_MARKERS = ["intern", "junior", "mid", "senior", "staff", "principal", "lead"]


def _extract_skills(text: str) -> List[str]:
    lowered = text.lower()
    found = [skill for skill in SKILL_CATALOG if skill in lowered]
    return sorted(found)


def parse_jd(jd: JobDescriptionInput) -> ParsedJD:
    body = jd.description.strip()
    body_lower = body.lower()

    all_skills = _extract_skills(body)
    optional_skills = []

    for marker in OPTIONAL_MARKERS:
        if marker in body_lower:
            idx = body_lower.find(marker)
            segment = body[idx : idx + 350]
            optional_skills.extend(_extract_skills(segment))

    optional_skills = sorted(set(optional_skills))
    required_skills = sorted([skill for skill in all_skills if skill not in optional_skills])

    seniority = "unspecified"
    for marker in SENIORITY_MARKERS:
        if re.search(rf"\b{re.escape(marker)}\b", body_lower):
            seniority = marker
            break

    summary = body[:250] + ("..." if len(body) > 250 else "")

    return ParsedJD(
        title=jd.title,
        summary=summary,
        required_skills=required_skills,
        optional_skills=optional_skills,
        seniority=seniority,
    )
