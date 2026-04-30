# --- START OF FILE streamlit_app.py ---

import streamlit as st
import google.generativeai as genai
import os
# Remove duplicate imports
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain # Removed RetrievalQA as it wasn't used directly
from langchain.memory import ConversationBufferMemory
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.checkpoint.memory import MemorySaver # In-memory checkpoint saver for simplicity
from langgraph.graph import StateGraph, END
from langgraph.pregel import Pregel # Import Pregel for running the graph
from langgraph.errors import GraphInterrupt # Import GraphInterrupt exception
from langgraph.types import interrupt, Command
import pickle
from sentence_transformers import SentenceTransformer
import pandas as pd # Keep pandas if needed elsewhere, otherwise remove
from typing import TypedDict, Optional,Sequence, Annotated, Dict # Use Annotated for state updates
import uuid # For unique thread IDs
import torch
from sklearn.metrics.pairwise import cosine_similarity

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

# --- Configuration & Constants ---
# Using environment variables is generally better, but sticking to sidebar input for now
PINECONE_INDEX_NAME = "poetryqa"
POET_NAMESPACE = "poet" # Corrected typo from 'peot'
POEM_NAMESPACE = "poem"
EMBEDDING_MODEL_PATH = 'You local path/Final Project/embeddingModel' # Make paths configurable or relative if possible
CLASSIFICATION_MODEL_PATH = 'You local path/Final Project/classificationModel/svm_model.pkl'

# --- Streamlit UI Setup ---
st.set_page_config(layout="wide") # Use wide layout for better chat display
st.title("📚 Poetry AI Assistant")


with st.sidebar:
    st.header("API Configuration")
    genai_api_key = st.text_input("Enter Gemini API Key", key="gemini_api_key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
    pinecone_api_key = st.text_input("Enter Pinecone API Key", key="pinecone_api_key", type="password", value=os.environ.get("PINECONE_API_KEY", ""))
    st.markdown("---")
    st.header("Debug Info")
    show_debug = st.checkbox("Show Debug Info", value=False)

# --- API Key Validation ---
if not genai_api_key:
    st.info("🔑 Please add your Gemini API key in the sidebar to continue.")
    st.stop()

if not pinecone_api_key:
    st.info("🔑 Please add your Pinecone API key in the sidebar to continue.")
    st.stop()

# --- Load Models and Initialize Services ---
pinecone_index = "poetry-ai"
pinecone_namespace = "poetry-ai"

# Initialize Pinecone
# Pinecone index name and namespaces
PINECONE_INDEX_NAME = "poetryqa"
POET_NAMESPACE = "peot"
POEM_NAMESPACE = "poem"

pc = Pinecone(api_key=pinecone_api_key)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# Initialize Google Gemini Embedding Model
embed_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=genai_api_key)
# Initialize Google Gemini Chat Model
# 
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-001", google_api_key=genai_api_key, temperature=0.1)

# Load the pre-trained SentenceTransformer model
embeddingPath = 'You local path/Final Project/embeddingModel'
embedding_model = SentenceTransformer(embeddingPath)
# Load the classification model
with open('You local path/Final Project/classificationModel/svm_model.pkl', 'rb') as f:
    svm_classifier = pickle.load(f)

with open('You local path/Final Project/clusterModel/kmeans.pkl', 'rb') as f:
    kmeans = pickle.load(f)

# Load the dataset
poem_df = pd.read_csv('You local path/Final Project/data/poem_embedding_and_label.csv')

# Initialize DuckDuckGo search tool
search_tool = DuckDuckGoSearchResults(max_results=3)
# --- Helper Functions ---
@st.cache_data # Cache classification function
def classify_text(text: str):
    """Classifies text using loaded models."""
    if not text or not isinstance(text, str) or not text.strip():
        return "Invalid Input"
    try:
        embedding = embedding_model.encode([text])
        prediction = svm_classifier.predict(embedding)[0]
        return f"Class {prediction}" # Adjust label as needed
    except Exception as e:
        st.error(f"Classification failed: {e}")
        return "Classification Error"
@st.cache_data # Cache recommendations function
def content_based_recommendations_by_text(text:str):
    # get embedding of text
    top_n=1
    poem_vector = embedding_model.encode([text])
    # find the cluster of the text
    prediction = kmeans.predict(poem_vector)[0]
    chosen_df = poem_df[poem_df['labels'] == prediction]
    columns = [str(i) for i in range(768)]
    chosen_df_embedding = chosen_df[columns].values
    # Calculate cosine similarity
    similarity_scores = cosine_similarity(poem_vector, chosen_df_embedding).flatten()
    # Get the indices of the most similar poems
    similar_poem_indices = similarity_scores.argsort()[-top_n:][::-1]
    recommendations = []
    for index in similar_poem_indices:
        recommendations.append({'poem': poem_df.iloc[index]['poem'], 'score': similarity_scores[index]})
    return recommendations
# --- Retrieval Chains ---
@st.cache_resource # Cache retrieval chains
def create_retrieval_chain(_llm, _embed_model, _index, namespace):
    """Creates a Langchain retrieval chain for a given namespace."""
    try:
        vectorstore = PineconeVectorStore(index=_index, embedding=_embed_model, namespace=namespace)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Reduced k for faster response
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True) # Specify output key
        qa = ConversationalRetrievalChain.from_llm(
            _llm,
            retriever=retriever,
            memory=memory
        )
        return qa
    except Exception as e:
        st.error(f"Error creating retrieval chain for namespace '{namespace}': {e}")
        return None

# Create Retrieval Chains (only if services loaded correctly)
poet_qa_chain = create_retrieval_chain(llm, embed_model, pinecone_index, POET_NAMESPACE)
poem_qa_chain = create_retrieval_chain(llm, embed_model, pinecone_index, POEM_NAMESPACE)

# --- LangGraph State and Nodes ---
# --- LangGraph State Definition ---

class GraphState(TypedDict):
    query: str                  # Original user query
    response: str               # Holds intermediate routing decisions OR final answer
    poem_text: Optional[str] # Stores poem text during interruption
    interrupted_for_classification: bool        # Flag for Streamlit UI
    interrupted_for_recommendation: bool        # Flag for Streamlit UI

# --- LangGraph Nodes ---
def determine_query_type(state: GraphState) -> GraphState:
    """Routes between Poet, Poem (further routing), or Unknown."""
    prompt = f"Route the query: '{state['query']}'. Is it about poets or poems? Respond ONLY poet or poem. If unsure, respond unknown."
    try:
        response_content = llm.invoke(prompt).content.strip().lower()
        route = "handle_unknown" # Default
        if "poet" in response_content: route = "call_poet_qa_chain"
        elif "poem" in response_content: route = "determine_poem_tool_type" # Needs further routing
    except Exception as e:
        st.warning(f"Router 1 LLM failed: {e}. Defaulting to search.")
        route = "handle_unknown"
    # Return full state, setting the route decision in 'response'
    return GraphState(
        query=state['query'],
        response=route,
        poem_text=None, # Ensure clear
        interrupted_for_classification=False, # Ensure clear
        interrupted_for_recommendation=False # Ensure clear
    )

def determine_poem_tool_type(state: GraphState) -> GraphState:
    """Routes Poem queries between QA, Classification (interrupt), or Unknown."""
    prompt = f"For the poem-related query: '{state['query']}'. Is it asking a question (qa) ,recommendation asking for classification/genre/category? Respond ONLY qa,recommendation or classification. If unsure, respond unknown."
    try:
        response_content = llm.invoke(prompt).content.strip().lower()
        route = "handle_unknown" # Default
        if "qa" in response_content: route = "call_poem_qa_chain"
        if "recommendation" in response_content: route = "request_poem_input_recommendation" # Route to interruption node
        elif "classification" in response_content: route = "request_poem_input_classification" # Route to interruption node
    except Exception as e:
        st.warning(f"Router 2 LLM failed: {e}. Defaulting to search.")
        route = "handle_unknown"
    # Preserve original query, set new route in 'response'
    return GraphState(
        query=state['query'],
        response=route,
        poem_text=None,
        interrupted_for_classification=False,
        interrupted_for_recommendation=False
    )

def request_poem_input_classification(state: GraphState) -> GraphState:
    """Sets the flag to signal Streamlit to pause and ask for input."""
    return GraphState(
        query=state['query'],
        response="Waiting for poem text...", # Placeholder response in state
        poem_text=state.get('poem_text'),
        interrupted_for_classification=True, # Set the flag
        interrupted_for_recommendation=False # Set the flag
    )
def request_poem_input_recommendation(state: GraphState) -> GraphState:
    """Sets the flag to signal Streamlit to pause and ask for input."""
    return GraphState(
        query=state['query'],
        response="Waiting for poem text...", # Placeholder response in state
        poem_text=state.get('poem_text'),
        interrupted_for_classification=False, # Set the flag
        interrupted_for_recommendation=True # Set the flag
    )
def call_poet_qa_chain(state: GraphState) -> GraphState:
    """Calls the Poet RAG chain."""
    response_text = "Error: Poet QA chain unavailable."
    try:
        if poem_qa_chain:
            # Use invoke for ConversationalRetrievalChain
            result = poet_qa_chain.invoke({"question": state["query"]})
            response_text = result.get('answer', "Could not find poet info.")
        else:
             st.error("Poet QA Chain could not be created.")
    except Exception as e:
        response_text = f"Poet chain error: {e}"
        st.error(response_text)
    return GraphState(
        query=state['query'],
        response=response_text,
        poem_text=state.get('poem_text'), # Preserve just in case
        interrupted_for_classification= False,
        interrupted_for_recommendation=False
    )

def call_poem_qa_chain(state: GraphState) -> GraphState:
    """Calls the Poem RAG chain."""
    response_text = "Error: Poem QA chain unavailable."
    try:
        if poem_qa_chain:
            result = poem_qa_chain.invoke({"question": state["query"]})
            response_text = result.get('answer', "Could not find poem info.")
        else:
             st.error("Poem QA Chain could not be created.")
    except Exception as e:
        response_text = f"Poem chain error: {e}"
        st.error(response_text)
    return GraphState(
        query=state['query'],
        response=response_text,
        poem_text=state.get('poem_text'),
        interrupted_for_classification= False,
        interrupted_for_recommendation=False
    )

def call_poem_recommendation(state: GraphState) -> GraphState:
    """Classifies the poem text received after interruption."""
    poem_text = state.get('poem_text')
    if poem_text:
        recommendations = content_based_recommendations_by_text(poem_text) # Use helper function
        recommendated_poem = recommendations[0]['poem']
        response_text = f"Recommendation: {recommendated_poem}"
    else:
        response_text = "Error: Poem text was not provided for recommendation."
        st.warning(response_text) # Log warning

    # Return final state, clearing temporary fields
    return GraphState(
        query=state['query'], # Keep original query for context
        response=response_text,
        poem_text=state.get('poem_text'), # Clear the text
        interrupted_for_classification=False, # Clear the flag,
        interrupted_for_recommendation=False
    )

def call_poem_classifing(state: GraphState) -> GraphState:
    """recommendate the poem text received after interruption."""
    poem_text = state.get('poem_text')
    if poem_text:
        classification_result = classify_text(poem_text) # Use helper function
        response_text = f"Classification Result: {classification_result}"
    else:
        response_text = "Error: Poem text was not provided for classification."
        st.warning(response_text) # Log warning

    # Return final state, clearing temporary fields
    return GraphState(
        query=state['query'], # Keep original query for context
        response=response_text,
        poem_text=state.get('poem_text'), # Clear the text
        interrupted_for_classification=False, # Clear the flag,
        interrupted_for_recommendation=False
    )
    
def duckduck_search(state: GraphState) -> GraphState:
    """Handles unknown queries using DuckDuckGo."""
    try:
        response_text = search_tool.invoke(state['query'])
    except Exception as e:
        response_text = f"Search error: {e}"
        st.error(response_text)
    return GraphState(
        query=state['query'],
        response=response_text,
        poem_text=state.get('poem_text'),
        interrupted_for_classification=False,
        interrupted_for_recommendation=False
    )

# --- Graph Definition ---
@st.cache_resource
def build_graph():
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("determine_query_type", determine_query_type)
    builder.add_node("determine_poem_tool_type", determine_poem_tool_type)
    builder.add_node("request_poem_input_classification", request_poem_input_classification) # Node that sets the flag
    builder.add_node("request_poem_input_recommendation", request_poem_input_recommendation) # Node that sets the flag
    builder.add_node("call_poet_qa_chain", call_poet_qa_chain)
    builder.add_node("call_poem_qa_chain", call_poem_qa_chain)
    builder.add_node("call_poem_recommendation", call_poem_recommendation) # Node that does classification
    builder.add_node("call_poem_classifing", call_poem_classifing) # Node that does classification
    builder.add_node("handle_unknown", duckduck_search)

    # Entry point
    builder.set_entry_point("determine_query_type")

    # Conditional Edges from Router 1
    builder.add_conditional_edges(
        "determine_query_type",
        lambda state: state["response"], # Route based on the node name stored in response
        {
            "call_poet_qa_chain": "call_poet_qa_chain",
            "determine_poem_tool_type": "determine_poem_tool_type", # Go to next router
            "handle_unknown": "handle_unknown",
        }
    )

    # Conditional Edges from Router 2
    builder.add_conditional_edges(
        "determine_poem_tool_type",
        lambda state: state["response"], # Route based on the node name stored in response
        {
            "call_poem_qa_chain": "call_poem_qa_chain",
            "request_poem_input_classification": "request_poem_input_classification",
            "request_poem_input_recommendation": "request_poem_input_recommendation",
            "handle_unknown": "handle_unknown",
        }
    )

    # Edge from requesting input node to the actual classification node.
    # This edge is followed *after* Streamlit resumes the graph.
    builder.add_edge("request_poem_input_classification", "call_poem_classifin")
    builder.add_edge("request_poem_input_recommendation", "call_poem_recommendationg")
    # Edges to END
    builder.add_edge("call_poet_qa_chain", END)
    builder.add_edge("call_poem_qa_chain", END)
    builder.add_edge("call_poem_classifing", END) # Classification node is now terminal
    builder.add_edge("call_poem_recommendation", END) # Classification node is now terminal
    builder.add_edge("handle_unknown", END)

    # Compile the graph with MemorySaver for checkpoints
    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory)
    print("DEBUG: Graph compiled successfully.") # Add a print statement for confirmation
    return graph

graph = build_graph()
graph.save_graph_image()
# --- Streamlit Chat Logic ---
# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "graph_interrupted_for_classification" not in st.session_state:
    st.session_state.graph_interrupted_for_classification = False
if "graph_interrupted_for_recommendation" not in st.session_state:
    st.session_state.graph_interrupted_for_recommendation = False
    
# Display existing messages
for message in st.session_state.messages:
    avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
    # with st.chat_message(message["role"], avatar=avatar):
    #     st.markdown(message["content"])       
    col1, col2 = st.columns([1, 1])  # Create two equal-width columns
    if message["role"] == "user":
        with col1:  # User message on the left
            st.chat_message("user",avatar=avatar)
            st.markdown(f"**You:** {message['content']}")
    else:
        with col2:  # Chatbot response on the right
            st.chat_message("assistant",avatar=avatar)
            st.markdown(f"**Bot:** {message['content']}")

# Handle Human Input if Interrupted
if st.session_state.graph_interrupted_for_classification or st.session_state.graph_interrupted_for_recommendation:
    # Display interruption message
    st.info("Please provide the poem text you want to classify or receive a recommendation for a similar poem below.")
    poem_text = st.text_area("Poem Text:", key="human_poem_input", height=150)
    if st.button("Submit Poem for Classification or Recommendation", key="submit_human_input"):
        if poem_text and poem_text.strip():
            # Prepare input for resuming the graph
            resume_input = {"poem_text": poem_text}
            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            # Display submission message
            submitted_text_display = f"(Poem submitted):\n```\n{poem_text[:400]}{'...' if len(poem_text) >400 else ''}\n```"
            st.session_state.messages.append({"role": "user", "content": submitted_text_display})
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(submitted_text_display)
            if st.session_state.graph_interrupted_for_classification:
                # Resume graph execution using invoke
                with st.spinner("Classifying..."):
                    try:
                        # Invoke the graph - it will resume from the checkpoint and use the input
                        # final_state = graph.invoke(Command(resume=resume_input), config=config)
                        # response = final_state.get('response', "Error retrieving classification result.")
                        response = classify_text(submitted_text_display)
                    except Exception as e:
                        st.error(f"Error resuming clssification: {e}")
                        response = "An error occurred during classification processing."
            if  st.session_state.graph_interrupted_for_recommendation:
                # Resume graph execution using invoke
                with st.spinner("Recommending..."):
                    try:
                        # Invoke the graph - it will resume from the checkpoint and use the input
                        # final_state = graph.invoke(Command(resume=resume_input), config=config)
                        # response = final_state.get('response', "Error retrieving recommendation result.")
                        recommendations = content_based_recommendations_by_text(submitted_text_display)
                        response = recommendations[0]['poem']
                    except Exception as e:
                        st.error(f"Error resuming recommendation: {e}")
                        response = "An error occurred during recommendation processing."
                        
            # Display final response
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(response)

            # Reset interruption state and rerun
            st.session_state.graph_interrupted_for_classification = False
            st.session_state.graph_interrupted_for_recommendation = False
            st.rerun()
        else:
            st.warning("Please enter the poem text.")

# Handle New User Query
else:
    if prompt := st.chat_input("Ask about poetry or request classification..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Prepare initial state and config
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        initial_input = GraphState(query=prompt, response="", poem_text=None, interrupted_for_classification=False,interrupted_for_recommendation=False)

        # Stream graph execution to check for interruption
        with st.spinner("Thinking..."):
            final_response = "Sorry, something went wrong."
            interrupted = False
            final_state_after_stream = None
            try:
                # Stream state updates
                for state_update in graph.stream(initial_input, config=config, stream_mode="values"):
                    final_state_after_stream = state_update # Keep track of the last state
                    # Check if the interruption flag was set by 'request_human_input' node
                    if state_update.get('interrupted_for_classification'):
                        st.session_state.graph_interrupted_for_classification = True
                        interrupted = True
                        break # Stop streaming, wait for user input
                    elif state_update.get('interrupted_for_recommendation'):
                        st.session_state.graph_interrupted_for_recommendation = True
                        interrupted = True
                        break
                if interrupted:
                    st.rerun() # Rerun to show the text area
                else:
                    # Graph finished normally, get response from the final state
                    if final_state_after_stream:
                        final_response = final_state_after_stream.get('response', "Processing complete, no response found.")
                    else:
                         final_response = "Error: Graph execution yielded no final state."

            except Exception as e:
                st.error(f"Error during graph execution: {e}")
                final_response = f"An error occurred: {e}"
                st.session_state.graph_interrupted = False # Reset flag on error

            # Display assistant response only if not interrupted
            if not interrupted:
                st.session_state.messages.append({"role": "assistant", "content": final_response})
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(final_response)
st.markdown("---")
st.caption("Enter your query in the box above. If requesting classification, you'll be prompted for the poem text.")