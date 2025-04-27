# PolkaAgents: Decentralized AI Agent Marketplace

PolkaAgents is a fully decentralized AI agent marketplace built on the Polkadot Asset Hub using smart contracts. It enables developers to deploy AI models as tokenized agents, allowing users to interact with these agents for a fee in a fully trustless and auditable environment.

## Features

- **Decentralized Marketplace**: Register AI agents and make them available to users in a permissionless way.
- **Tokenized Agents**: AI agents are represented as tokens on the Polkadot blockchain.
- **Trustless Transactions**: All interactions are recorded on-chain for full auditability.
- **Offline-First**: All AI models run locally for privacy and reliability.
- **Hybrid Intelligence**: Supports robust offline inference using local models.

## Architecture

- **Smart Contract (Ink!)**: Handles agent registration, payments, and interaction logging.
- **Backend (FastAPI Microservices)**: Each AI agent runs as a standalone service.
- **Frontend (Streamlit)**: Simple, intuitive UI for users to interact with agents.

## Available AI Agents

1. **Chatbot Agent**: General Q&A functionality using GPT-2 Large.
2. **Translation Agent**: Multi-language translation using MarianMT models.
3. **Sentiment Analysis Agent**: Text sentiment classification using BERT-Large.
4. **Summarization Agent**: Text summarization using T5-Base.
5. **Job Application Writer Agent**: Professional cover letter generation using GPT-2 Large.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Polkadot.js wallet (for interacting with agents)
- At least 8GB of RAM (for running the AI models)
- GPU support (optional, but recommended for better performance)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PolkaAgents.git
   cd PolkaAgents