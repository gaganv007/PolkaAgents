from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import sys
import time
from pydantic import BaseModel
import traceback

# Add the parent directory to sys.path to import from common
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.utils import time_execution

# Import the model
from model import SentimentModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PolkaAgents Sentiment Analysis Agent",
    description="API for the Sentiment Analysis AI Agent in the PolkaAgents marketplace",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model
model = SentimentModel()

# Define request and response models
class PredictRequest(BaseModel):
    interaction_id: int
    agent_id: int
    query: str

class PredictResponse(BaseModel):
    interaction_id: int
    agent_id: int
    result: str
    processing_time: float

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "PolkaAgents Sentiment Analysis Agent"}

@app.post("/predict", response_model=PredictResponse)
@time_execution
async def predict(request: PredictRequest):
    """Analyze sentiment of text using the sentiment model."""
    try:
        start_time = time.time()
        
        # Log the incoming request
        logger.info(f"Received sentiment analysis request: {request.interaction_id} - {request.query[:100]}...")
        
        # Analyze sentiment using the model
        result = model.analyze_sentiment(request.query)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log the result
        logger.info(f"Generated sentiment analysis in {processing_time:.4f} seconds: {result[:100]}...")
        
        # Return the result
        return PredictResponse(
            interaction_id=request.interaction_id,
            agent_id=request.agent_id,
            result=result,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Get port from environment or default to 8003
    port = int(os.environ.get("PORT", 8003))
    # Run the FastAPI application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)