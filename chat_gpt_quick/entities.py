from pydantic import BaseModel
from typing import List, Optional

class ResearchPaper(BaseModel):
    title: str  # Title of the paper
    abstract: str  # Abstract of the paper
    url: Optional[str]  # URL for accessing the full paper
    
class IndustryInsight(BaseModel):
    key_insight: str  # Single impactful statement summarizing the paper’s value
    actionable_insights: List[str]  # Practical applications of the research in the industry
    target_industries: List[str]  # Challenges or limitations of applying the research
    potential_impact: str  # Description of the business impact (e.g., cost savings, efficiency)