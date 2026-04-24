from typing import Dict, List

from ..models import CandidateMatch, EngagementResult, RankedCandidate


def combine_scores(
    matches: List[CandidateMatch],
    interest: List[EngagementResult],
    match_weight: float,
    interest_weight: float,
) -> List[RankedCandidate]:
    interest_map: Dict[str, EngagementResult] = {i.candidate_id: i for i in interest}

    ranked: List[RankedCandidate] = []
    for m in matches:
        ir = interest_map.get(m.candidate_id)
        interest_score = ir.interest_score if ir else 50.0
        final_score = (m.match_score * match_weight) + (interest_score * interest_weight)

        ranked.append(
            RankedCandidate(
                candidate_id=m.candidate_id,
                name=m.name,
                match_score=m.match_score,
                interest_score=round(float(interest_score), 2),
                final_score=round(float(final_score), 2),
                match_reason=m.explanation,
                engagement_summary=(ir.rationale if ir else "No engagement response available."),
            )
        )

    ranked.sort(key=lambda x: x.final_score, reverse=True)
    return ranked
