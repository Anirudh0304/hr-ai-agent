import math
import re
from collections import Counter
from typing import List

from ..models import CandidateMatch, CandidateRecord, MatchExplanation, ParsedJD


WORD_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9\-\+\.]{1,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "have",
    "you",
    "your",
    "will",
    "into",
    "our",
    "are",
    "not",
    "all",
    "job",
    "role",
}


def _tokenize(text: str) -> List[str]:
    tokens = [t.lower() for t in WORD_PATTERN.findall(text)]
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]


def _tf_vector(text: str) -> Counter:
    return Counter(_tokenize(text))


def _cosine_similarity(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    numerator = sum(a[k] * b[k] for k in common)
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return numerator / (norm_a * norm_b)


def match_candidates(jd: ParsedJD, candidates: List[CandidateRecord]) -> List[CandidateMatch]:
    jd_text = " ".join([jd.title, jd.summary, " ".join(jd.required_skills), " ".join(jd.optional_skills)])
    jd_vector = _tf_vector(jd_text)

    results: List[CandidateMatch] = []

    for candidate in candidates:
        c_text_lower = candidate.profile_text.lower()
        c_vector = _tf_vector(candidate.profile_text)
        semantic_sim = _cosine_similarity(jd_vector, c_vector)

        matched = [s for s in jd.required_skills if s in c_text_lower]
        missing = [s for s in jd.required_skills if s not in c_text_lower]
        keyword_hits = len(matched)

        skill_coverage = (len(matched) / len(jd.required_skills)) if jd.required_skills else 0.0
        match_score = (0.65 * semantic_sim) + (0.35 * skill_coverage)

        results.append(
            CandidateMatch(
                candidate_id=candidate.candidate_id,
                name=candidate.name,
                match_score=round(match_score * 100, 2),
                explanation=MatchExplanation(
                    matched_skills=matched,
                    missing_skills=missing,
                    keyword_hits=keyword_hits,
                ),
            )
        )

    results.sort(key=lambda x: x.match_score, reverse=True)
    return results
