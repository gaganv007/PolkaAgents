from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import time


class AgentType(str, Enum):
    CHATBOT = "chatbot"
    TRANSLATION = "translation"
    SENTIMENT = "sentiment"
    SUMMARIZATION = "summarization"
    JOB_APPLICATION = "job_application"


class InteractionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMetadata(BaseModel):
    name: str
    description: str
    agent_type: AgentType
    model_info: str
    version: str = "1.0.0"


class Agent(BaseModel):
    id: int
    owner: str
    metadata: AgentMetadata
    price_per_query: int
    stake_amount: int
    active: bool
    created_at: int


class QueryRequest(BaseModel):
    agent_id: int
    query: str
    wallet_address: str


class QueryResponse(BaseModel):
    interaction_id: int
    status: str = "pending"
    estimated_time: int = 5  # seconds


class SubmitResponseRequest(BaseModel):
    interaction_id: int
    response_data: str
    agent_id: int


class InteractionResult(BaseModel):
    interaction_id: int
    agent_id: int
    query: str
    response: Optional[str] = None
    status: InteractionStatus
    timestamp: int
    fee_paid: int


class AgentListResponse(BaseModel):
    agents: List[Agent]