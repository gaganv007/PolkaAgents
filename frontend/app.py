import streamlit as st
import requests
import json
import time
from datetime import datetime
import os

# API Gateway URL (use environment variable or default)
API_URL = os.environ.get("API_URL", "http://api-gateway:8000")

# Configure page
st.set_page_config(
    page_title="PolkaAgents - Decentralized AI Marketplace",
    page_icon="🧠",
    layout="wide"
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        font-size: 42px;
        font-weight: bold;
        color: #4F8BF9;
        margin-bottom: 10px;
    }
    .main-subtitle {
        font-size: 24px;
        margin-bottom: 30px;
    }
    .agent-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .agent-card:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .agent-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #333;
    }
    .error-box {
        background-color: #ffdddd;
        border: 1px solid #ff0000;
        color: #ff0000;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'wallet_connected' not in st.session_state:
    st.session_state.wallet_connected = False
    st.session_state.wallet_address = ""

if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Main header
st.markdown('<div class="main-title">PolkaAgents</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Decentralized AI Agent Marketplace on Polkadot</div>', unsafe_allow_html=True)

# Sidebar - Wallet connection
st.sidebar.title("Wallet Connection")

if not st.session_state.wallet_connected:
    with st.sidebar.form("wallet_form"):
        wallet_address = st.text_input("Wallet Address", value="5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")
        connect_button = st.form_submit_button("Connect Wallet")
        
        if connect_button and wallet_address:
            st.session_state.wallet_connected = True
            st.session_state.wallet_address = wallet_address
            st.experimental_rerun()
else:
    st.sidebar.success(f"Connected: {st.session_state.wallet_address[:10]}...{st.session_state.wallet_address[-6:]}")
    if st.sidebar.button("Disconnect Wallet"):
        st.session_state.wallet_connected = False
        st.session_state.wallet_address = ""
        st.experimental_rerun()

# Sidebar - Transaction history
st.sidebar.title("Transaction History")
if st.session_state.transactions:
    for tx in reversed(st.session_state.transactions[-10:]):
        st.sidebar.markdown(f"""
        <div style="border-bottom: 1px solid #e0e0e0; padding: 10px 0;">
            <div><strong>{tx['agent_type']}</strong></div>
            <div style="font-size: 12px;">{tx['timestamp']}</div>
            <div style="font-size: 12px;">Fee: {tx['fee']} DOT</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.sidebar.info("No transactions yet")

# Function to get all agents
@st.cache_data(ttl=60)
def get_agents():
    try:
        response = requests.get(f"{API_URL}/agents", timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["agents"]
    except requests.RequestException as e:
        st.error(f"Network error fetching agents: {str(e)}")
        return []
    except ValueError as e:
        st.error(f"Error parsing agents response: {str(e)}")
        return []

# Function to submit a query
def submit_query(agent_id, query, wallet_address):
    try:
        payload = {
            "agent_id": agent_id,
            "query": query,
            "wallet_address": wallet_address
        }
        response = requests.post(
            f"{API_URL}/query", 
            json=payload, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error submitting query: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"Error parsing query response: {str(e)}")
        return None

# Function to get interaction results
def get_interaction(interaction_id):
    try:
        response = requests.get(f"{API_URL}/interactions/{interaction_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching interaction: {str(e)}")
        return None
    except ValueError as e:
        st.error(f"Error parsing interaction response: {str(e)}")
        return None

# Main application logic
def main():
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Browse Agents", "Use Agent", "About"])

    with tab1:
        display_agents_tab()

    with tab2:
        use_agent_tab()

    with tab3:
        about_polkaagents_tab()

def display_agents_tab():
    st.header("Available AI Agents")
    
    # Get agents
    agents = get_agents()
    
    if not agents:
        st.warning("No agents available. Please check your network connection.")
        return
    
    # Display agents
    for agent in agents:
        with st.container():
            st.markdown(f"<div class='agent-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='agent-title'>{agent['metadata']['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Type:** {agent['metadata']['agent_type'].title()}")
            st.markdown(f"**Price:** {agent['price_per_query'] / 10**10:.4f} DOT per query")
            st.markdown(f"**Description:** {agent['metadata']['description']}")
            st.markdown(f"**Model:** {agent['metadata']['model_info']}")
            st.markdown("</div>", unsafe_allow_html=True)

def use_agent_tab():
    st.header("Use an AI Agent")
    
    if not st.session_state.wallet_connected:
        st.warning("Please connect your wallet first to use AI agents.")
        return

    # Get agents
    agents = get_agents()
    
    if not agents:
        st.error("Unable to load agents. Please check your connection.")
        return

    # Select agent
    agent_options = {agent["metadata"]["name"]: agent["id"] for agent in agents}
    selected_agent_name = st.selectbox("Select an Agent", list(agent_options.keys()))
    selected_agent_id = agent_options[selected_agent_name]
    
    # Get selected agent
    selected_agent = next((a for a in agents if a["id"] == selected_agent_id), None)
    
    if not selected_agent:
        st.error("Selected agent not found.")
        return

    # Display agent details
    st.markdown(f"<div class='agent-card'>", unsafe_allow_html=True)
    st.markdown(f"**Description:** {selected_agent['metadata']['description']}")
    st.markdown(f"**Price:** {selected_agent['price_per_query'] / 10**10:.4f} DOT per query")
    st.markdown(f"**Model:** {selected_agent['metadata']['model_info']}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input form based on agent type
    agent_type = selected_agent["metadata"]["agent_type"]
    
    # Specialized input for different agent types
    if agent_type == "chatbot":
        query = st.text_area("Enter your question:", height=150)
        submit_text = "Ask Question"
    
    elif agent_type == "translation":
        st.markdown("**Example format:** Translate from English to Spanish: Hello, how are you?")
        query = st.text_area("Enter text to translate:", height=150)
        submit_text = "Translate"
    
    elif agent_type == "sentiment":
        query = st.text_area("Enter text for sentiment analysis:", height=150)
        submit_text = "Analyze Sentiment"
    
    elif agent_type == "summarization":
        query = st.text_area("Enter text to summarize:", height=250)
        submit_text = "Summarize"
    
    elif agent_type == "job_application":
        col1, col2 = st.columns(2)
        with col1:
            resume = st.text_area("Your Resume:", height=200)
        with col2:
            job_description = st.text_area("Job Description:", height=200)
        
        query = f"Resume:\n{resume}\n\nJob Description:\n{job_description}"
        submit_text = "Generate Cover Letter"
    
    # Submit button
    if st.button(submit_text):
        # Validate input
        if not query or (agent_type == "job_application" and (not resume or not job_description)):
            st.error("Please provide all required information.")
            return

        with st.spinner("Processing your request..."):
            # Submit query
            response = submit_query(
                selected_agent_id,
                query,
                st.session_state.wallet_address
            )
            
            if not response:
                st.error("Failed to submit query. Please try again.")
                return

            interaction_id = response.get("interaction_id")
            if not interaction_id:
                st.error("No interaction ID received.")
                return

            # Poll for result
            progress_bar = st.progress(0)
            max_retries = 60
            retries = 0
            result = None
            
            while retries < max_retries:
                retries += 1
                progress_bar.progress(retries / max_retries)
                
                result = get_interaction(interaction_id)
                if result and result.get("status") == "COMPLETED" and result.get("response"):
                    progress_bar.progress(1.0)
                    break
                
                time.sleep(0.5)
            
            # Display result
            if result and result.get("status") == "COMPLETED" and result.get("response"):
                st.success("Query processed successfully!")
                
                # Add to transaction history
                st.session_state.transactions.append({
                    "agent_type": selected_agent["metadata"]["name"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fee": selected_agent["price_per_query"] / 10**10
                })
                
                # Display result
                st.subheader("Result")
                st.markdown(result["response"])
            else:
                st.warning("Query processing timed out or failed. Please try again.")

def about_polkaagents_tab():
    st.header("About PolkaAgents")
    
    st.markdown("""
    **PolkaAgents** is a fully decentralized AI agent marketplace built on the Polkadot Asset Hub using smart contracts. 
    It enables developers to deploy AI models as tokenized agents, allowing users to interact with these agents for 
    a fee in a fully trustless and auditable environment.
    
    ### Key Features
    
    - **Decentralized Marketplace**: Register AI agents and make them available to users in a permissionless way
    - **Tokenized Agents**: AI agents are represented as tokens on the Polkadot blockchain
    - **Trustless Transactions**: All interactions are recorded on-chain for full auditability
    - **Offline-First**: All AI models run locally for privacy and reliability
    
    ### Architecture
    
    - **Smart Contract (Ink!)**: Handles agent registration, payments, and interaction logging
    - **Backend Services**: Each AI agent runs as a standalone FastAPI microservice
    - **Frontend**: Streamlit interface for users to interact with agents
    
    ### Available AI Agents
    
    - **Chatbot**: General Q&A functionality using GPT-2 Large
    - **Translation**: Multi-language translation using MarianMT models
    - **Sentiment Analysis**: Text sentiment classification using BERT-Large
    - **Summarization**: Text summarization using T5-Base
    - **Job Application Writer**: Professional cover letter generation using GPT-2 Large
    """)

# Footer
def display_footer():
    st.markdown("""
    ---
    ### PolkaAgents - Redefining AI ownership, trust, and accessibility in the decentralized web
    """)

# Run the main application
if __name__ == "__main__":
    main()
    display_footer()
