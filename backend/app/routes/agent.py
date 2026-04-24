import csv
import io
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..models import (
    CandidateRecord,
    JobDescriptionInput,
    PipelineRequest,
    RankResponse,
)
from ..services.conversation_engine import batch_assess_interest
from ..services.jd_parser import parse_jd
from ..services.matching_engine import match_candidates
from ..services.scoring_service import combine_scores


router = APIRouter(prefix="/api", tags=["agent"])


@router.post("/parse-jd")
async def parse_jd_endpoint(jd: JobDescriptionInput):
    return parse_jd(jd)


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = await file.read()
    decoded = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(decoded))

    required_columns = {"candidate_id", "name", "profile_text"}
    if not required_columns.issubset(set(reader.fieldnames or [])):
        raise HTTPException(
            status_code=400,
            detail="CSV must contain columns: candidate_id, name, profile_text",
        )

    candidates: List[CandidateRecord] = []
    for row in reader:
        candidates.append(
            CandidateRecord(
                candidate_id=(row.get("candidate_id") or "").strip(),
                name=(row.get("name") or "").strip(),
                profile_text=(row.get("profile_text") or "").strip(),
            )
        )

    return {"count": len(candidates), "candidates": candidates}


@router.post("/run-pipeline", response_model=RankResponse)
async def run_pipeline(payload: PipelineRequest):
    if not payload.candidates:
        raise HTTPException(status_code=400, detail="At least one candidate is required.")

    parsed_jd = parse_jd(payload.jd)
    matches = match_candidates(parsed_jd, payload.candidates)
    interest = await batch_assess_interest(payload.candidates, parsed_jd)

    ranked = combine_scores(
        matches=matches,
        interest=interest,
        match_weight=payload.weights.match_weight,
        interest_weight=payload.weights.interest_weight,
    )

    shortlist = ranked[: max(1, payload.top_k)]
    return RankResponse(jd=parsed_jd, shortlist=shortlist)
