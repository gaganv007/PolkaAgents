import streamlit as st
import requests
import json

# API Gateway URL
API_URL = "http://api-gateway:8000"

# Configure the page
st.set_page_config(
    page_title="PolkaAgents",
    page_icon="🧠",
    layout="wide"
)

# Add title
st.title("PolkaAgents: Decentralized AI Marketplace")
st.write("A fully decentralized AI agent marketplace built on Polkadot")

# Sidebar for agent selection
st.sidebar.title("Select AI Agent")
agent_options = {
    "Chatbot": 1,
    "Translation": 2, 
    "Sentiment Analysis": 3,
    "Summarization": 4,
    "Job Application Writer": 5
}
selected_agent = st.sidebar.selectbox("Choose an Agent", list(agent_options.keys()))
agent_id = agent_options[selected_agent]

# Input section
st.header(f"{selected_agent} Agent")

if selected_agent == "Chatbot":
    user_input = st.text_area("Enter your question:", height=150)
    
elif selected_agent == "Translation":
    st.write("Example: Translate from English to Spanish: Hello, how are you?")
    user_input = st.text_area("Enter text to translate:", height=150)
    
elif selected_agent == "Sentiment Analysis":
    user_input = st.text_area("Enter text for sentiment analysis:", height=150)
    
elif selected_agent == "Summarization":
    user_input = st.text_area("Enter text to summarize:", height=250)
    
elif selected_agent == "Job Application Writer":
    col1, col2 = st.columns(2)
    with col1:
        resume = st.text_area("Your Resume:", height=200)
    with col2:
        job_description = st.text_area("Job Description:", height=200)
    user_input = f"Resume:\n{resume}\n\nJob Description:\n{job_description}"

# Process input
if st.button("Submit"):
    if not user_input or (selected_agent == "Job Application Writer" and (not resume or not job_description)):
        st.error("Please provide all the required information.")
    else:
        with st.spinner("Processing..."):
            try:
                # For now, we'll just simulate a response since API might not be ready
                # In real implementation, we would call the API
                # response = requests.post(f"{API_URL}/query", 
                #     json={"agent_id": agent_id, "query": user_input, "wallet_address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY"}
                # )
                
                # Simulate a response
                st.success("Query processed!")
                
                # Show result
                st.header("Result")
                
                if selected_agent == "Chatbot":
                    st.write("This is a simulated response from the chatbot agent. In a real implementation, this would be a response from the AI model.")
                
                elif selected_agent == "Translation":
                    st.write("This is a simulated translation. In a real implementation, this would be translated text from the AI model.")
                
                elif selected_agent == "Sentiment Analysis":
                    st.write("Sentiment: Positive (Confidence: 92%)")
                    st.write("This is a simulated sentiment analysis result. In a real implementation, this would be an analysis from the AI model.")
                
                elif selected_agent == "Summarization":
                    st.write("This is a simulated summary. In a real implementation, this would be a summary from the AI model.")
                
                elif selected_agent == "Job Application Writer":
                    st.write("This is a simulated cover letter. In a real implementation, this would be a cover letter from the AI model.")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add info section
with st.expander("About PolkaAgents"):
    st.write("""
    PolkaAgents is a fully decentralized AI agent marketplace built on the Polkadot Asset Hub using smart contracts. 
    It enables developers to deploy AI models as tokenized agents, allowing users to interact with these agents for 
    a fee in a fully trustless and auditable environment.
    
    The platform offers hybrid intelligence, leveraging heavy local AI models when offline and online APIs when available, 
    ensuring seamless, robust, and flexible performance.
    """)
