"""LangGraph application for Poetry AI Assistant."""

import logging
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

from backend.core.state import app_state
from backend.services.classification import classification_service
from backend.services.recommendation import recommendation_service

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class GraphState(TypedDict):
    """State definition for the poetry graph."""
    query: str
    response: str
    poem_text: Optional[str]


class PoetryGraph:
    """Main LangGraph application for handling poetry-related queries."""
    
    def __init__(self):
        self.graph = self._build_graph()

    def determine_query_type(self, g_state: GraphState):
        """Route query to poet or poem handler based on intent."""
        logger.info(f"[STEP 1] Query Classification - Input: '{g_state['query']}'")
        prompt = (
            f"You are a routing assistant. Analyze the user query: '{g_state['query']}'.\n"
            "Determine if the query is about a 'poet' (author info, biography) or a 'poem' (specific poem info, classification, recommendation).\n"
            "Examples:\n"
            "- 'Who is Maya Angelou?' -> poet\n"
            "- 'Tell me about the life of Shakespeare' -> poet\n"
            "- 'Analyze The Waste Land' -> poem\n"
            "- 'I want a poem recommendation' -> poem\n"
            "- 'Classify this text' -> poem\n"
            "Respond ONLY with one word: 'poet', 'poem', or 'unknown'."
        )
        try:
            resp = app_state.llm.invoke(prompt).content.strip().lower()
            logger.debug(f"[STEP 1] LLM Response: {resp}")
            if "poet" in resp:
                logger.info("[STEP 1] Classification Result: POET -> Routing to Poet QA Chain")
                return {"response": "call_poet_qa_chain"}
            if "poem" in resp:
                logger.info("[STEP 1] Classification Result: POEM -> Routing to Poem Tool Classifier")
                return {"response": "determine_poem_tool_type"}
        except Exception as e:
            logger.error(f"[STEP 1] Error in query classification: {e}")
        logger.warning("[STEP 1] Classification inconclusive -> Routing to fallback search")
        return {"response": "handle_unknown"}

    def determine_poem_tool_type(self, g_state: GraphState):
        """Route poem queries to appropriate handler (QA, recommendation, or classification)."""
        logger.info(f"[STEP 2] Poem Tool Classification - Query: '{g_state['query']}'")
        prompt = (
            f"You are a routing assistant for poem-related queries. Analyze the query: '{g_state['query']}'.\n"
            "Determine the intent: 'qa' (questions about poems), 'recommendation' (finding similar poems), or 'classification' (identifying genre/label).\n"
            "Examples:\n"
            "- 'What is the theme of Ozymandias?' -> qa\n"
            "- 'Suggest a poem like this one' -> recommendation\n"
            "- 'Recommend me a sad poem' -> recommendation\n"
            "- 'What category does this poem belong to?' -> classification\n"
            "- 'Classify this poem' -> classification\n"
            "Respond ONLY with one word: 'qa', 'recommendation', or 'classification'."
        )
        try:
            resp = app_state.llm.invoke(prompt).content.strip().lower()
            logger.debug(f"[STEP 2] LLM Response: {resp}")
            if "qa" in resp:
                logger.info("[STEP 2] Classification Result: QA -> Routing to Poem QA Chain")
                return {"response": "call_poem_qa_chain"}
            if "recommendation" in resp:
                logger.info("[STEP 2] Classification Result: RECOMMENDATION -> Requesting poem input")
                return {"response": "request_poem_input_recommendation"}
            if "classification" in resp:
                logger.info("[STEP 2] Classification Result: CLASSIFICATION -> Requesting poem input")
                return {"response": "request_poem_input_classification"}
        except Exception as e:
            logger.error(f"[STEP 2] Error in poem tool classification: {e}")
        logger.warning("[STEP 2] Classification inconclusive -> Routing to fallback search")
        return {"response": "handle_unknown"}

    def request_poem_input_classification(self, g_state: GraphState):
        """Interrupt to request poem text for classification."""
        user_input = interrupt("✍️ Please provide the poem text for classification:")
        return {"poem_text": user_input.get("poem_text")}

    def request_poem_input_recommendation(self, g_state: GraphState):
        """Interrupt to request poem text for recommendation."""
        user_input = interrupt("✨ Please provide the poem text for recommendation:")
        return {"poem_text": user_input.get("poem_text")}

    def call_poet_qa_chain(self, g_state: GraphState):
        """Handle poet-related questions using RAG."""
        logger.info(f"[STEP 3] Poet RAG QA Chain - Question: '{g_state['query']}'")
        logger.info("[STEP 3.1] Starting document retrieval from Pinecone (poet namespace)...")
        try:
            if not app_state.poet_qa_chain:
                logger.warning("[STEP 3] Poet QA chain unavailable -> Fallback to search")
                return self.duckduck_search(g_state)

            res = app_state.poet_qa_chain.invoke({"question": g_state["query"]})
            answer = res.get('answer', "") if isinstance(res, dict) else ""

            _no_info_phrases = {
                "no info found.", "",
                "i do not have any information about this in the provided context.",
                "i don't have enough information",
                "i cannot find", "no relevant information",
                "not mentioned in the provided context",
            }
            if not answer or any(p in answer.lower() for p in _no_info_phrases) or len(answer.strip()) < 20:
                logger.warning("[STEP 3] Empty/insufficient RAG answer -> Fallback to search")
                return self.duckduck_search(g_state)

            logger.debug(f"[STEP 3.2] Retrieved and generated answer (length: {len(answer)} chars)")
            logger.info(f"[STEP 3] RAG QA Complete - Response: {answer[:100]}...")
            return {"response": answer}
        except Exception as e:
            logger.error(f"[STEP 3] Error in poet QA chain: {e}")
            return self.duckduck_search(g_state)

    def call_poem_qa_chain(self, g_state: GraphState):
        """Handle poem-related questions using RAG."""
        logger.info(f"[STEP 3] Poem RAG QA Chain - Question: '{g_state['query']}'")
        logger.info("[STEP 3.1] Starting document retrieval from Pinecone (poem namespace)...")
        try:
            if not app_state.poem_qa_chain:
                logger.warning("[STEP 3] Poem QA chain unavailable -> Fallback to search")
                return self.duckduck_search(g_state)

            res = app_state.poem_qa_chain.invoke({"question": g_state["query"]})
            answer = res.get('answer', "") if isinstance(res, dict) else ""

            _no_info_phrases = {
                "no info found.", "",
                "i do not have any information about this in the provided context.",
                "i don't have enough information",
                "i cannot find", "no relevant information",
                "not mentioned in the provided context",
            }
            if not answer or any(p in answer.lower() for p in _no_info_phrases) or len(answer.strip()) < 20:
                logger.warning("[STEP 3] Empty/insufficient RAG answer -> Fallback to search")
                return self.duckduck_search(g_state)

            logger.debug(f"[STEP 3.2] Retrieved and generated answer (length: {len(answer)} chars)")
            logger.info(f"[STEP 3] RAG QA Complete - Response: {answer[:100]}...")
            return {"response": answer}
        except Exception as e:
            logger.error(f"[STEP 3] Error in poem QA chain: {e}")
            return self.duckduck_search(g_state)

    def call_poem_classifing(self, g_state: GraphState):
        """Classify poem text using ML model."""
        poem_preview = g_state["poem_text"][:100] if g_state.get("poem_text") else "N/A"
        logger.info(f"[STEP 4] Classification - Poem: '{poem_preview}...'")
        try:
            res = classification_service.classify(g_state["poem_text"])
            logger.info(f"[STEP 4] Classification Complete - Result: {res}")
            return {"response": f"**Classification Result:**\n\n{res}"}
        except Exception as e:
            logger.error(f"[STEP 4] Error in classification: {e}")
            return {"response": f"**Classification error:** {str(e)}"}

    def call_poem_recommendation(self, g_state: GraphState):
        """Get poem recommendations using ML model."""
        poem_preview = g_state["poem_text"][:100] if g_state.get("poem_text") else "N/A"
        logger.info(f"[STEP 4] Recommendation - Poem: '{poem_preview}...'")
        try:
            recs = recommendation_service.get_recommendations(g_state["poem_text"])
            if recs and len(recs) > 0:
                logger.info(f"[STEP 4] Recommendation Complete - Found {len(recs)} recommendations")
                logger.debug(f"[STEP 4] Top recommendation: {recs[0]}")
                return {"response": f"**Recommendation:**\n\nI suggest reading: *{recs[0].get('poem', 'Unknown')}*"}
            logger.warning("[STEP 4] No recommendations found")
            return {"response": "No recommendations found."}
        except Exception as e:
            logger.error(f"[STEP 4] Error in recommendation: {e}")
            return {"response": f"**Recommendation error:** {str(e)}"}

    def duckduck_search(self, g_state: GraphState):
        """Fallback search using DuckDuckGo, synthesized by LLM into a coherent answer."""
        logger.warning(f"[FALLBACK] DuckDuckGo Search - Query: '{g_state['query']}'")
        try:
            raw_results = app_state.search_tool.invoke(g_state['query'])
            logger.info(f"[FALLBACK] Search Complete - Raw results ({len(raw_results)} chars). Synthesizing with LLM...")

            synthesis_prompt = (
                f"You are a knowledgeable poetry assistant. A user asked: \"{g_state['query']}\"\n\n"
                f"The following web search results were retrieved:\n\n{raw_results}\n\n"
                "Using these search results as context, provide a clear, concise, and well-structured answer to the user's question. "
                "Focus on poetry-related information. If the results are insufficient, say so honestly and share what you do know. "
                "Do not mention that you are using search results — just answer naturally as an assistant."
            )
            synthesized = app_state.llm.invoke(synthesis_prompt).content.strip()
            logger.info(f"[FALLBACK] Synthesis Complete - Response: {synthesized[:100]}...")
            return {"response": synthesized}
        except Exception as e:
            logger.error(f"[FALLBACK] Error in search/synthesis: {e}")
            return {"response": "_I apologize, but I couldn't find relevant information in my database or through a web search._"}

    def _build_graph(self):
        """Construct the LangGraph state machine."""
        builder = StateGraph(GraphState)
        
        # Add nodes
        builder.add_node("determine_query_type", self.determine_query_type)
        builder.add_node("determine_poem_tool_type", self.determine_poem_tool_type)
        builder.add_node("request_poem_input_classification", self.request_poem_input_classification)
        builder.add_node("request_poem_input_recommendation", self.request_poem_input_recommendation)
        builder.add_node("call_poet_qa_chain", self.call_poet_qa_chain)
        builder.add_node("call_poem_qa_chain", self.call_poem_qa_chain)
        builder.add_node("call_poem_classifing", self.call_poem_classifing)
        builder.add_node("call_poem_recommendation", self.call_poem_recommendation)
        builder.add_node("handle_unknown", self.duckduck_search)

        # Set entry point
        builder.set_entry_point("determine_query_type")

        # Add conditional edges
        builder.add_conditional_edges("determine_query_type", lambda s: s["response"], {
            "call_poet_qa_chain": "call_poet_qa_chain",
            "determine_poem_tool_type": "determine_poem_tool_type",
            "handle_unknown": "handle_unknown"
        })
        builder.add_conditional_edges("determine_poem_tool_type", lambda s: s["response"], {
            "call_poem_qa_chain": "call_poem_qa_chain",
            "request_poem_input_classification": "request_poem_input_classification",
            "request_poem_input_recommendation": "request_poem_input_recommendation",
            "handle_unknown": "handle_unknown"
        })

        # Add fixed edges
        builder.add_edge("request_poem_input_classification", "call_poem_classifing")
        builder.add_edge("request_poem_input_recommendation", "call_poem_recommendation")
        builder.add_edge("call_poet_qa_chain", END)
        builder.add_edge("call_poem_qa_chain", END)
        builder.add_edge("call_poem_classifing", END)
        builder.add_edge("call_poem_recommendation", END)
        builder.add_edge("handle_unknown", END)

        return builder.compile(checkpointer=MemorySaver())

    def save_graph_image(self, output_path="graph_workflow.png"):
        """Generate and save an image of the graph workflow."""
        try:
            graph_image = self.graph.get_graph().draw_mermaid_png()
            with open(output_path, "wb") as f:
                f.write(graph_image)
            print(f"Graph image saved to {output_path}")
        except Exception as e:
            print(f"Failed to generate graph image: {e}")


poetry_graph_app = PoetryGraph()
graph = poetry_graph_app.graph


if __name__ == "__main__":
    poetry_graph_app.save_graph_image()