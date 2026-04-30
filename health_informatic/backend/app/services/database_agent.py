import sys
import os
import re
import json
import time
import pandas as pd
from typing import Literal, Dict, List
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from app.config import settings

class DatabaseAgent:
    def __init__(self, patient_id, gemini_key=settings.GOOGLE_API_KEY, question=None):
        # Use environment variables from settings
        # self.host = settings.DATABASE_HOST
        # self.port = settings.DATABASE_PORT
        # self.user = settings.DATABASE_USER
        # self.password = settings.DATABASE_PASSWORD
        self.database = settings.DATABASE_NAME
        self.gemini_model = settings.GOOGLE_MODEL_NAME
        self.patient_id = patient_id
        self.gemini_key = gemini_key
        self.question = question

    def connect_db(self):
        db_start = time.time()
        # mysql_uri = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        
        # Use absolute path relative to this file to locate the database
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up 3 levels: services -> app -> backend -> health_informatic
        project_root = os.path.abspath(os.path.join(current_dir, "../../../"))
        db_dir = os.path.join(project_root, "database")
        db_path = os.path.join(db_dir, self.database)
        
        # Ensure the database directory exists
        if not os.path.exists(db_dir):
            print(f"Database directory missing: {db_dir}. Creating it...")
            os.makedirs(db_dir, exist_ok=True)
            
        print(f"Connecting to database at: {db_path}")
        if not os.path.exists(db_path):
            print(f"Database file does not exist. SQLite will create a new empty file.")
            
        sqlite_url = f"sqlite:///{db_path}"
        db = SQLDatabase.from_uri(sqlite_url)
        db_duration = time.time() - db_start
        print(f"Database connection in {db_duration*1000:.0f}ms")
        return db

    def save_graph_diagram(self, app):
        """Save the agent graph as a PNG image."""
        try:
            graph_image = app.get_graph().draw_mermaid_png()
            output_path = "agent_graph.png"
            with open(output_path, "wb") as f:
                f.write(graph_image)
            print(f"Graph diagram saved to {output_path}")
        except Exception as e:
            print(f"Could not save graph diagram: {e}")

    def create_agent(self):
        agent_start = time.time()
        print(f"DatabaseAgent: Starting initialization...")

        # Step 1: LLM Setup
        llm_start = time.time()
        # call gemini model
        llm = ChatGoogleGenerativeAI(model=self.gemini_model,
                                    verbose=False,  # Disable verbose
                                    temperature=0.1,  # Lower = faster
                                    # max_tokens=1000,  # Limit output
                                    google_api_key=self.gemini_key)
        db = self.connect_db()
        print(f"LLM setup in {(time.time() - llm_start)*1000:.0f}ms")
    
        # Step 2: Toolkit Setup
        toolkit_start = time.time()
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        # Create the agent with the tools
        tools = toolkit.get_tools()
        get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
        get_schema_node = ToolNode([get_schema_tool], name="get_schema")
        run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
        run_query_node = ToolNode([run_query_tool], name="run_query")
        print(f"Toolkit setup in {(time.time() - toolkit_start)*1000:.0f}ms")
    

        # Enhanced MessagesState to include schema info
        class EnhancedMessagesState(MessagesState):
            selected_tables: List[str] = []
            table_schemas: Dict = {}
            relevant_columns: Dict = {}
            executed_query: str = ""

        # Route the query to the appropriate chain
        
        def determine_query_type(state: EnhancedMessagesState):
            """Skip classification - assume all queries are patient data queries"""
            return {"messages": [AIMessage("list_tables")]}

        def route_query(state: EnhancedMessagesState) -> Literal[END, "list_tables","handle_greeting"]:
            """Route the query to the appropriate tool based on the last message."""
            print("STEP 2: Routing query")
            
            messages = state["messages"]
            last_message = messages[-1].content
            
            if "list_tables" in last_message:
                print("Routing to: list_tables")
                return "list_tables"
            elif "greeting" in last_message:
                print("Routing to: handle_greeting")
                return "handle_greeting"
            else:
                print("Routing to: END (non-patient query)")
                return END
            
        def handle_greeting(state: EnhancedMessagesState):
            """Handle greetings and general questions using LLM."""
            print("STEP 3: Handling greeting/general question")
            
            messages = state["messages"]
            original_query = messages[0].content if messages else self.question
            print(f"Original query: '{original_query}'")
            
            greeting_system_prompt = f"""You are a Health Informatics AI assistant designed for healthcare professionals.

            The user has sent: "{original_query}"

            Your task is to respond appropriately and CONCISELY based on the type of message:

            For GREETINGS (hello, hi, good morning, etc.):
            - Greet warmly in 1-2 sentences
            - Briefly mention you help with patient data
            - Give 1 simple example
            - Keep total response under 150 characters

            For FAREWELLS (goodbye, bye, etc.):
            - Simple, friendly farewell in 1 sentence
            - Maximum 50 characters

            For HELP/CAPABILITY questions (what can you do, who are you, etc.):
            - Explain role in 2-3 short sentences
            - List 2-3 main capabilities briefly
            - Keep under 200 characters total

            For COURTESY (thanks, how are you, etc.):
            - Brief appropriate response
            - Mention availability
            - Maximum 100 characters

            Guidelines:
            - BE CONCISE - short responses only
            - Use simple, direct language
            - No bullet points or complex formatting
            - Keep responses conversational but brief
            - Current patient: {self.patient_id}

            Examples of good responses:
            - "Hello! I help with patient data analysis. Try asking about patient {self.patient_id}'s treatment history!"
            - "I'm your Health Informatics AI. I can analyze patient records, treatments, and lab results. What would you like to know?"
            - "Goodbye! Feel free to return for patient data help anytime."
            """
            
            system_message = {
                "role": "system",
                "content": greeting_system_prompt,
            }
            
            user_message = {
                "role": "user", 
                "content": original_query
            }
            
            response = llm.invoke([system_message, user_message])
            
            print(f"Generated greeting response: {response.content[:100]}...")
            
            # Format as JSON for consistency
            formatted_result = json.dumps({
                "type": "text",
                "content": response.content,
                "context": "greeting_response"
            })
            
            new_message = AIMessage(content=formatted_result)
            return {"messages": [new_message]}

        def list_tables(state: EnhancedMessagesState):
            """List the tables in the database."""
            print("STEP 3: Listing database tables")
            
            tool_call = {
                "name": "sql_db_list_tables",
                "args": {},
                "id": "abc123",
                "type": "tool_call",
            }
            tool_call_message = AIMessage(content="", tool_calls=[tool_call])

            list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
            tool_message = list_tables_tool.invoke(tool_call)
            response = AIMessage(f"Available tables: {tool_message.content}")

            print(f"Available tables: {tool_message.content}")
            
            return {"messages": [tool_call_message, tool_message, response]}

        def call_get_schema(state: EnhancedMessagesState):
            """Get schema and store in state"""
            print("STEP 4: Getting database schema")
            
            llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
            response = llm_with_tools.invoke(state["messages"])
            
            print(f"Schema response has tool_calls: {hasattr(response, 'tool_calls') and bool(response.tool_calls)}")
            
            return {"messages": state["messages"] + [response]}
        
        def process_schema_response(state: EnhancedMessagesState):
            """Process schema response - minimal processing, let LLM handle details"""
            print("STEP 4b: Processing schema response (minimal)")
            
            messages = state["messages"]
            
            # Find the tool message with schema info
            schema_content = ""
            for msg in reversed(messages):
                if hasattr(msg, 'content') and 'CREATE TABLE' in str(msg.content):
                    schema_content = msg.content
                    break
            
            print(f"Schema content length: {len(schema_content)}")
            print(f"Schema preview: {schema_content[:200]}...")
            
            # Simple table extraction - no complex column parsing
            create_matches = re.findall(r'CREATE TABLE\s+`?(\w+)`?', schema_content, re.IGNORECASE)
            all_tables = list(set(create_matches))
            
            print(f"Found tables: {all_tables}")
            
            # Select relevant tables based on user question
            original_question = state["messages"][0].content if state["messages"] else self.question
            question_lower = original_question.lower()
            
            selected_tables = []
            for table in all_tables:
                table_lower = table.lower()
                if any(keyword in table_lower for keyword in ['patient', 'registration', 'treatment', 'pathology']):
                    selected_tables.append(table)
                    print(f"Selected table: {table} (keyword match)")
                elif table_lower in question_lower:
                    selected_tables.append(table)
                    print(f"Selected table: {table} (mentioned in question)")
            
            # Fallback selection
            if not selected_tables:
                selected_tables = all_tables[:1] if all_tables else []
                if selected_tables:
                    print(f"Fallback selected: {selected_tables}")
            
            print(f"Final selected tables: {selected_tables}")
            print(f"LLM will handle detailed schema parsing in generate_query")
            
            return {
                "messages": messages,
                "selected_tables": selected_tables,
                "table_schemas": {},  # Empty - LLM will parse from raw content
                "relevant_columns": {}  # Empty - LLM will parse from raw content
            }

        def generate_query(state: EnhancedMessagesState):
            print("STEP 5: Generating SQL query")
            
            selected_tables = state.get("selected_tables", [])
            
            print(f"Using tables: {selected_tables}")
            print(f"LLM will extract column info from schema messages")
            
            # Simplified prompt - let LLM read schema from message history
            generate_query_system_prompt = f"""
                You are an agent designed to interact with a SQL database.
                Given an input question about patient patient_id={self.patient_id}, create a syntactically correct {db.dialect} query to run.
                
                Guidelines:
                - Focus on the most relevant tables: {', '.join(selected_tables) if selected_tables else 'patient-related tables'}
                - Look at the schema information in the previous messages to understand available columns
                - Only select columns that are needed to answer the question
                - Always include patient_id filter where applicable (use id column for patient_id)
                - Limit results to 100 unless user specifies otherwise
                - DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.)
                
                You must generate a SQL query using the sql_db_query tool. The query will be validated and executed in the next step.
                Return only the SQL query via the tool call - do not execute it yet.
            """
            
            system_message = {
                "role": "system",
                "content": generate_query_system_prompt,
            }
            
            llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
            response = llm_with_tools.invoke([system_message] + state["messages"])
            
            # Extract query from response for logging
            if hasattr(response, 'tool_calls') and response.tool_calls:
                query = response.tool_calls[0]["args"]["query"]
                print(f"Generated query: {query}")
            else:
                print("No tool calls generated!")
            
            return {"messages": [response]}

        def check_query(state: EnhancedMessagesState):
            """Check the query generated by the model."""
            print("STEP 6: Validating SQL query")
            
            check_query_system_prompt = f"""
                You are a SQL expert with a strong attention to detail.
                Double check the {db.dialect} query for common mistakes, including:
                - Using NOT IN with NULL values
                - Using UNION when UNION ALL should have been used
                - Using BETWEEN for exclusive ranges
                - Data type mismatch in predicates
                - Properly quoting identifiers
                - Using the correct number of arguments for functions
                - Casting to the correct data type
                - Using the proper columns for joins

                If there are any mistakes, rewrite the query. If there are no mistakes,
                just reproduce the original query.

                You will call the appropriate tool to execute the query after running this check.
            """
            system_message = {
                "role": "system",
                "content": check_query_system_prompt,
            }

            tool_call = state["messages"][-1].tool_calls[0]
            user_message = {"role": "user", "content": tool_call["args"]["query"]}
            
            print(f"Validating query: {tool_call['args']['query']}")
            
            llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
            response = llm_with_tools.invoke([system_message, user_message])
            response.id = state["messages"][-1].id
            
            return {"messages": [response]}

        def run_query_with_schema(state: EnhancedMessagesState):
            """Custom run_query that preserves schema info"""
            print("STEP 7: Executing SQL query")
            
            messages = state["messages"]
            last_message = messages[-1]
            
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                query = last_message.tool_calls[0]["args"]["query"]
                print(f"Executing: {query}")
                
                # Create a proper tool call dict for the run_query_tool
                tool_call = {
                    "name": "sql_db_query",
                    "args": {"query": query},
                    "id": last_message.tool_calls[0].get("id", "query_exec"),
                    "type": "tool_call",
                }
                
                try:
                    result = run_query_tool.invoke(tool_call)
                    print(f"Query result type: {type(result)}")
                    print(f"Query result length: {len(str(result))}")
                    print(f"Result preview: {str(result)[:200]}...")
                    
                    return {
                        "messages": messages + [result],
                        "selected_tables": state.get("selected_tables", []),
                        "table_schemas": state.get("table_schemas", {}),
                        "relevant_columns": state.get("relevant_columns", {}),
                        "executed_query": query
                    }
                except Exception as e:
                    print(f"Error executing query: {e}")
                    error_message = f"Error executing query: {str(e)}"
                    error_result = AIMessage(content=error_message)
                    return {
                        "messages": messages + [error_result],
                        "selected_tables": state.get("selected_tables", []),
                        "table_schemas": state.get("table_schemas", {}),
                        "relevant_columns": state.get("relevant_columns", {}),
                        "executed_query": query
                    }
            
            return {"messages": messages}

        def should_continue(state: EnhancedMessagesState) -> Literal["check_query", "run_query_with_schema"]:
            # Skip validation step entirely
            return "run_query_with_schema"

        def should_continue_after_query(state: EnhancedMessagesState) -> Literal[END, "format_query_results"]:
            """Decide what to do after running the query"""
            print("STEP 8: Checking if results need formatting")
            
            messages = state["messages"]
            last_message = messages[-1]
            
            content = last_message.content if hasattr(last_message, "content") else ""
            print(f"Checking content: {content[:100]}...")
            
            if "[(" in content and ")]" in content:
                print("Found tuple data - proceeding to format")
                return "format_query_results"
            else:
                print("No tuple data found - going to END")
                return END

        def format_query_results(state: EnhancedMessagesState):
            """Let LLM format query results with summary-first approach"""
            print("STEP 9: LLM formatting query results with summary")
            
            messages = state["messages"]
            last_message = messages[-1]
            selected_tables = state.get("selected_tables", [])
            executed_query = state.get("executed_query", "")
            original_question = state["messages"][0].content if state["messages"] else self.question
            
            print(f"Selected tables: {selected_tables}")
            print(f"Executed query: {executed_query}")
            print(f"Original question: {original_question}")
            
            try:
                content = last_message.content.strip()
                print(f"Raw query result: {content[:200]}...")
                
                # Let LLM create both summary and detailed data
                format_system_prompt = f"""
                You are a health informatics assistant helping doctors analyze patient data. You have received raw query results from a database.
                
                Patient ID: {self.patient_id}
                Original Question: {original_question}
                Raw query result: {content}
                Query executed: {executed_query}
                Tables queried: {', '.join(selected_tables)}
                
                Your task is to create a user-friendly response with two parts:
                1. A brief summary that doctors can quickly read
                2. Detailed table data that can be viewed on demand
                
                Return a JSON object with this structure:
                {{
                    "type": "table_data",
                    "summary": "Brief, conversational summary of findings (2-3 sentences)",
                    "data_source": "Which table(s) and what type of data was found",
                    "record_count": "Number of records found",
                    "key_insights": ["2-3 bullet points of key findings"],
                    "data": [array of objects with column names as keys],
                    "table_html": "HTML table representation",
                    "explanation": "Brief medical context or interpretation if relevant",
                    "schema_info": {{
                        "tables": {selected_tables},
                        "query": "{executed_query}"
                    }}
                }}
                
                Guidelines for summary:
                - Start with "I found [X] records in the [table name] showing..."
                - Mention date ranges, key treatments, or notable patterns
                - Keep it conversational and doctor-friendly
                - Highlight any important medical findings
                
                Guidelines for data processing:
                - Convert datetime objects to readable date strings (YYYY-MM-DD format)
                - Handle None/null values as "N/A" or appropriate empty values
                - Use clear, readable column names (Treatment, Date, Disease Type, etc.)
                - Each row should be an object with consistent keys
                - Sort by date if applicable
                
                Example summary: "I found 24 treatment records in the patients_treatment table spanning from June 2023 to April 2024. The patient has received various treatments including medications like Ibuprofen and Aspirin for chronic pain, as well as specialized treatments for cardiovascular conditions."
                
                IMPORTANT: Return ONLY the JSON object, no markdown formatting, no code blocks, no extra text.
                """
                
                system_message = {
                    "role": "system", 
                    "content": format_system_prompt
                }
                
                user_message = {
                    "role": "user",
                    "content": f"Please analyze and format this patient data: {content}"
                }
                
                response = llm.invoke([system_message, user_message])
                
                print(f"LLM formatting response: {response.content[:200]}...")
                
                # Clean the response - remove markdown code blocks if present
                cleaned_response = response.content.strip()
                
                # Remove markdown code blocks
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                elif cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]   # Remove ```
                
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove ending ```
                
                cleaned_response = cleaned_response.strip()
                
                print(f"Cleaned response: {cleaned_response[:200]}...")
                
                # Validate that it's valid JSON
                try:
                    parsed_json = json.loads(cleaned_response)
                    print("LLM returned valid JSON")
                    
                    # Ensure required fields exist
                    if "type" not in parsed_json:
                        parsed_json["type"] = "table_data"
                    if "data" not in parsed_json:
                        parsed_json["data"] = []
                    if "summary" not in parsed_json:
                        parsed_json["summary"] = f"Found data in {', '.join(selected_tables)} table(s)"
                    if "schema_info" not in parsed_json:
                        parsed_json["schema_info"] = {
                            "tables": selected_tables,
                            "query": executed_query
                        }
                    
                    # Create HTML table if not provided
                    if "table_html" not in parsed_json and parsed_json["data"]:
                        df = pd.DataFrame(parsed_json["data"])
                        parsed_json["table_html"] = df.to_html(classes="table table-striped", index=False)
                        parsed_json["html"] = parsed_json["table_html"]  # For frontend compatibility
                    
                    # Add record count if not provided
                    if "record_count" not in parsed_json and parsed_json["data"]:
                        parsed_json["record_count"] = len(parsed_json["data"])
                    
                    formatted_result = json.dumps(parsed_json)
                    print("Successfully formatted with LLM summary")
                    
                except json.JSONDecodeError as e:
                    print(f"LLM response was not valid JSON: {str(e)}")
                    print(f"Problematic content: {cleaned_response[:500]}...")
                    # Fallback structure with basic summary
                    formatted_result = json.dumps({
                        "type": "table_data",
                        "summary": f"Found data in {', '.join(selected_tables)} table(s) for patient {self.patient_id}",
                        "data_source": f"Tables: {', '.join(selected_tables)}",
                        "record_count": "Multiple records",
                        "content": cleaned_response,
                        "original_query": executed_query,
                        "tables": selected_tables,
                        "parse_error": str(e)
                    })
                
                new_message = AIMessage(content=formatted_result)
                return {"messages": messages[:-1] + [new_message]}
                
            except Exception as e:
                print(f"Error in LLM formatting: {str(e)}")
                # Simple fallback with summary
                formatted_result = json.dumps({
                    "type": "table_data", 
                    "summary": f"Found data for patient {self.patient_id} in {', '.join(selected_tables)} table(s)",
                    "data_source": f"Tables: {', '.join(selected_tables)}",
                    "content": f"Query result: {content}",
                    "error": f"Formatting error: {str(e)}"
                })
                new_message = AIMessage(content=formatted_result)
                return {"messages": messages[:-1] + [new_message]}
            
            return {"messages": messages}

        # Build the graph with enhanced state
        builder = StateGraph(EnhancedMessagesState)
        
        # Add all nodes
        builder.add_node("determine_query_type", determine_query_type)
        builder.add_node("handle_greeting", handle_greeting)  # New greeting node
        builder.add_node("list_tables", list_tables)
        builder.add_node("call_get_schema", call_get_schema)
        builder.add_node("get_schema", get_schema_node)
        builder.add_node("process_schema_response", process_schema_response)
        builder.add_node("generate_query", generate_query)
        builder.add_node("check_query", check_query)
        builder.add_node("run_query_with_schema", run_query_with_schema)
        builder.add_node("format_query_results", format_query_results)
        
        # Add edges - ENHANCED STRUCTURE
        builder.add_edge(START, "determine_query_type")
        builder.add_conditional_edges("determine_query_type", route_query)
        builder.add_edge("handle_greeting", END)  # Greeting goes straight to end
        builder.add_edge("list_tables", "call_get_schema")
        builder.add_edge("call_get_schema", "get_schema")
        builder.add_edge("get_schema", "process_schema_response")
        builder.add_edge("process_schema_response", "generate_query")
        builder.add_conditional_edges("generate_query", should_continue)
        builder.add_edge("check_query", "run_query_with_schema")
        builder.add_conditional_edges("run_query_with_schema", should_continue_after_query)
        builder.add_edge("format_query_results", END)

        print("Building agent graph...")
        graph_start = time.time()
        agent = builder.compile()
        print(f"Graph built in {(time.time() - graph_start)*1000:.0f}ms")
    
        # Save the graph diagram
        self.save_graph_diagram(agent)
        
        print("Starting agent execution...")
        execution_start = time.time()
        final_state = None
        step_count = 0

        for step in agent.stream(
            {"messages": [{"role": "user", "content": self.question}]},
            stream_mode="values",
        ):
            step_count += 1
            final_state = step
            print(f"Step {step_count}: {step['messages'][-1].__class__.__name__}")
            # Remove the pretty_print for speed
            # step["messages"][-1].pretty_print()

        execution_duration = time.time() - execution_start
        total_duration = time.time() - agent_start
        print(f"Agent execution in {execution_duration:.2f}s ({step_count} steps)")
        print(f"Total DatabaseAgent time: {total_duration:.2f}s")

        # Return formatted result based on type
        final_message = final_state["messages"][-1]
        if hasattr(final_message, 'content'):
            try:
                parsed_content = json.loads(final_message.content)
                if parsed_content.get("type") == "table_data":
                    print("Returning table data")
                    return final_message.content, parsed_content["table_html"]
                elif parsed_content.get("type") == "single_column":
                    print("Returning single column data")
                    return parsed_content["text"], parsed_content["html"]
                else:
                    print("Returning text content")
                    return parsed_content.get("content", final_message.content), None
            except (json.JSONDecodeError, KeyError):
                print("Returning raw content")
                return final_message.content, None
        
        return final_message.content if isinstance(final_message, AIMessage) else str(final_message), None