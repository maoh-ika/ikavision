from dataclasses import dataclass
from enum import Enum

class AnalysisJobState(Enum):
    CREATED = 0
    MOVIE_UPLOADED = 1
    PROCESSING = 2
    COMPLETED = 3
    FAILED = 4
    CANCELLED = 5 

@dataclass
class AnalysisJob:
    job_id: str
    user_id: str
    job_name: str
    state: AnalysisJobState
    movie_bucket_name: str
    movie_key: str
    movie_file_name: str
    created_at: int
    fail_reason: dict = None
