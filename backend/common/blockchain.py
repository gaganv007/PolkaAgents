import json
import logging
from typing import Dict, Any, List, Optional
import os
import time
import requests
from .models import Agent, AgentMetadata, AgentType, InteractionResult, InteractionStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlockchainClient:
    """Client for interacting with the Polkadot blockchain and our smart contract."""
    
    def __init__(self, node_url: str, contract_address: str):
        self.node_url = node_url
        self.contract_address = contract_address
        logger.info(f"Initialized blockchain client with node URL: {node_url}")
        
    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """
        Get agent information from the blockchain.
        
        In a real implementation, this would call the smart contract.
        For this example, we'll simulate the response.
        """
        # In a real implementation, this would make an RPC call to the blockchain
        # For this example, we'll return simulated data
        
        # Simulate agent not found for certain IDs
        if agent_id <= 0 or agent_id > 5:
            return None
            
        agent_types = [
            AgentType.CHATBOT,
            AgentType.TRANSLATION,
            AgentType.SENTIMENT,
            AgentType.SUMMARIZATION,
            AgentType.JOB_APPLICATION
        ]
        
        names = [
            "ChatBot AI",
            "TranslateGPT",
            "SentimentAnalyzer",
            "TextSummarizer",
            "JobApplicationWriter"
        ]
        
        descriptions = [
            "General purpose chatbot for answering questions",
            "Translation service supporting multiple languages",
            "Analyze the sentiment of text as positive, negative, or neutral",
            "Create concise summaries of long texts",
            "Generate professional cover letters from resumes and job descriptions"
        ]
        
        model_info = [
            "Using GPT-2 Large for offline text generation",
            "Using MarianMT models for offline translation",
            "Using BERT-Large for sentiment classification",
            "Using T5-Base for text summarization",
            "Using fine-tuned GPT-2 for job application writing"
        ]
        
        # Adjust for 0-indexing when accessing arrays
        idx = agent_id - 1
        
        metadata = AgentMetadata(
            name=names[idx],
            description=descriptions[idx],
            agent_type=agent_types[idx],
            model_info=model_info[idx]
        )
        
        return Agent(
            id=agent_id,
            owner="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",  # Example Polkadot address
            metadata=metadata,
            price_per_query=1000000000,  # 1 DOT in smallest units
            stake_amount=10000000000,  # 10 DOT in smallest units
            active=True,
            created_at=int(time.time()) - 86400  # Created 1 day ago
        )
    
    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        agents = []
        # In a real implementation, this would call the contract to get all agents
        # For this example, we'll simulate by getting agents with ID 1-5
        for agent_id in range(1, 6):
            agent = self.get_agent(agent_id)
            if agent:
                agents.append(agent)
        return agents
    
    def query_agent(self, agent_id: int, query: str, wallet_address: str) -> int:
        """
        Submit a query to an agent and pay the fee.
        
        Returns the interaction ID.
        """
        # In a real implementation, this would make a transaction to the smart contract
        # For this example, we'll simulate a successful query
        
        # Simulate a new interaction ID
        interaction_id = int(time.time() * 1000) % 1000000
        
        logger.info(f"Query submitted to agent {agent_id} from {wallet_address}: {query}")
        logger.info(f"Generated interaction ID: {interaction_id}")
        
        return interaction_id
    
    def submit_response(self, interaction_id: int, response_data: str, agent_id: int) -> bool:
        """
        Submit a response for a query interaction.
        
        Returns True if successful, False otherwise.
        """
        # In a real implementation, this would make a transaction to the smart contract
        # For this example, we'll simulate a successful response submission
        
        logger.info(f"Response submitted for interaction {interaction_id}, agent {agent_id}")
        logger.info(f"Response data: {response_data[:100]}...")
        
        return True
    
    def get_interaction(self, interaction_id: int) -> Optional[InteractionResult]:
        """Get interaction details."""
        # In a real implementation, this would call the smart contract
        # For this example, we'll simulate a response
        
        # Simulate not found for certain IDs
        if interaction_id <= 0:
            return None
            
        return InteractionResult(
            interaction_id=interaction_id,
            agent_id=1 + (interaction_id % 5),  # Simulate an agent ID
            query="Sample query for testing",
            response="Sample response for the query" if interaction_id % 3 != 0 else None,
            status=(
                InteractionStatus.COMPLETED if interaction_id % 3 != 0 
                else InteractionStatus.PENDING
            ),
            timestamp=int(time.time()) - (interaction_id % 1000),
            fee_paid=1000000000  # 1 DOT in smallest units
        )


# Singleton instance
blockchain_client = BlockchainClient(
    node_url=os.environ.get("BLOCKCHAIN_NODE_URL", "http://localhost:9944"),
    contract_address=os.environ.get("CONTRACT_ADDRESS", "5CiPPseXPECbkjWCa6MnjNokrgYjMqmKndv2rSnekmSK2DjL")
)