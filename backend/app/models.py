from typing import List, Optional
from pydantic import BaseModel, Field


class JobDescriptionInput(BaseModel):
    title: str
    description: str


class CandidateRecord(BaseModel):
    candidate_id: str
    name: str
    profile_text: str


class ParsedJD(BaseModel):
    title: str
    summary: str
    required_skills: List[str] = Field(default_factory=list)
    optional_skills: List[str] = Field(default_factory=list)
    seniority: str = "unspecified"


class MatchExplanation(BaseModel):
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    keyword_hits: int = 0


class CandidateMatch(BaseModel):
    candidate_id: str
    name: str
    match_score: float
    explanation: MatchExplanation


class ConversationTurn(BaseModel):
    role: str
    message: str


class EngagementResult(BaseModel):
    candidate_id: str
    interest_score: float
    rationale: str
    conversation: List[ConversationTurn] = Field(default_factory=list)


class RankedCandidate(BaseModel):
    candidate_id: str
    name: str
    match_score: float
    interest_score: float
    final_score: float
    match_reason: MatchExplanation
    engagement_summary: str


class RankResponse(BaseModel):
    jd: ParsedJD
    shortlist: List[RankedCandidate]


class PipelineWeights(BaseModel):
    match_weight: float = 0.6
    interest_weight: float = 0.4


class PipelineRequest(BaseModel):
    jd: JobDescriptionInput
    candidates: Optional[List[CandidateRecord]] = None
    weights: PipelineWeights = Field(default_factory=PipelineWeights)
    top_k: int = 10
