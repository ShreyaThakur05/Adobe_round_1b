from typing import Literal, List
from pydantic import BaseModel,Field
from datetime import datetime
class Heading(BaseModel):
    level: Literal["H1", "H2", "H3"]
    text: str
    page: int

class Round1AOutput(BaseModel):
    title: str = "Untitled Document"
    outline: List[Heading] = Field(default_factory=list)
# --- Round 1B Schemas (Add These) ---

# Input Schemas
class DocumentInfo(BaseModel):
    filename: str
    title: str

class PersonaInfo(BaseModel):
    role: str

class JobInfo(BaseModel):
    task: str

class ChallengeInfo(BaseModel):
    challenge_id: str
    test_case_name: str
    description: str

class Round1BInput(BaseModel):
    challenge_info: ChallengeInfo
    documents: List[DocumentInfo]
    persona: PersonaInfo
    job_to_be_done: JobInfo

# Output Schemas
class Metadata(BaseModel):
    input_documents: List[str]
    persona: str
    job_to_be_done: str
    processing_timestamp: datetime

class ExtractedSection(BaseModel):
    document: str
    section_title: str
    importance_rank: int
    page_number: int

class SubsectionAnalysis(BaseModel):
    document: str
    refined_text: str
    page_number: int

class Round1BOutput(BaseModel):
    metadata: Metadata
    extracted_sections: List[ExtractedSection]
    subsection_analysis: List[SubsectionAnalysis]