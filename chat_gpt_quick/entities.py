from pydantic import BaseModel
from typing import List, Optional

class ResearchPaper(BaseModel):
    title: str  # Title of the paper
    abstract: str  # Abstract of the paper
    url: Optional[str]  # URL for accessing the full paper
    
class IndustryInsight(BaseModel):
    key_insight: str  # Single impactful statement summarizing the paper’s value
    use_cases: List[str]  # Practical applications of the research in the industry
    risks_or_challenges: Optional[List[str]] = None  # Challenges or limitations of applying the research
    potential_impact: str  # Description of the business impact (e.g., cost savings, efficiency)
    target_industries: List[str]  # Industries or sectors most likely to benefit
    feasibility_score: float  # Scale from 1 to 5 (1: not feasible, 5: highly feasible)