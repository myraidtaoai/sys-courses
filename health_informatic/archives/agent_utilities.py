from typing import Literal  
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

class DatabaseAgent:
    def __init__(self, patient_id, gemini_key, question):
        # Initial the database credentials
        self.host = 'db_host'
        self.port = 3306
        self.user = 'user_name'
        self.password = 'password'
        self.database = 'db_name'
        self.patient_id = patient_id
        self.gemini_key = gemini_key
        self.question = question

    def connect_db(self):
        mysql_uri = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        return SQLDatabase.from_uri(mysql_uri)

    def create_agent(self):
        # call gemini model
        llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash',
                                    verbose=True,
                                    temperature=0,
                                    google_api_key=self.gemini_key)
        db = self.connect_db()
        
        # Create the SQLDatabaseToolkit with the database and LLM
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        # Create the agent with the tools
        tools = toolkit.get_tools()
        get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
        get_schema_node = ToolNode([get_schema_tool], name="get_schema")
        run_query_tool = next(tool for tool in tools if tool.name == "sql_db_query")
        run_query_node = ToolNode([run_query_tool], name="run_query")
       
        # Route the query to the appropriate chain
        def determine_query_type(state: MessagesState):
            """Determine if the query is about patients or not."""
            messages = state["messages"]
            last_message = messages[-1]
            query = last_message.content
            # Use LLM to determine which tool to use
            system_route_prompt = f"""You are a Health Informatice AI. You will be given a user query and you must decide whether it is about patient's information, such as treament, pathology, phone number, address and so on.
            If the query is about patient's information, return "list_tables". If not, answer the question as briefly as you can.
            """
            system_message = {
                "role": "system",
                "content": system_route_prompt,
            }

            response = llm.invoke([system_message, {"role": "user", "content": query}])
            if "list_tables" in response.content :
                return {"messages": [AIMessage("list_tables")]}
            else:
                return {"messages": [response]}

        def route_query(state: MessagesState) -> Literal[END, "list_tables"]:
            """Route the query to the appropriate tool based on the last message."""
            messages = state["messages"]
            last_message = messages[-1].content
            if "list_tables" in last_message:
                return "list_tables"
            else:
                return END  


        def list_tables(state: MessagesState):
            """List the tables in the database."""
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

            return {"messages": [tool_call_message, tool_message, response]}


        def call_get_schema(state: MessagesState):
            """
            Call the get_schema tool to get the schema of the database.
            Note that LangChain enforces that all models accept `tool_choice="any"`
            as well as `tool_choice=<string name of tool>`.
            """
            llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice="any")
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}

        def generate_query(state: MessagesState):
            # Define the system prompt for generating queries
            # This prompt will be used to instruct the model on how to generate queries
            generate_query_system_prompt = """
                You are an agent designed to interact with a SQL database.
                Given an input question about patient patient_id={patient_id}, create a syntactically correct {dialect} query to run,
                then look at the results of the query and return the answer. Unless the user
                specifies a specific number of examples they wish to obtain, always limit your
                query to at most {top_k} results.

                You can order the results by a relevant column to return the most interesting
                examples in the database. Never query for all the columns from a specific table,
                only ask for the relevant columns given the question.
                DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
            """.format(
                dialect=db.dialect,
                top_k=100,
                patient_id=self.patient_id
            )
            system_message = {
                "role": "system",
                "content": generate_query_system_prompt,
            }
            # We do not force a tool call here, to allow the model to
            # respond naturally when it obtains the solution.
            llm_with_tools = llm.bind_tools([run_query_tool])
            response = llm_with_tools.invoke([system_message] + state["messages"])

            return {"messages": [response]}

        def check_query(state: MessagesState):
            """Check the query generated by the model."""
            check_query_system_prompt = """
                You are a SQL expert with a strong attention to detail.
                Double check the {dialect} query for common mistakes, including:
                - Using NOT IN with NULL values
                - Using UNION when UNION ALL should have been used
                - Using BETWEEN for exclusive ranges
                - Data type mismatch in predicates
                - Properly quoting identifiers
                - Using the correct number of arguments for functions
                - Casting to the correct data type
                - Using the proper columns for joins

                If there are any of the above mistakes, rewrite the query. If there are no mistakes,
                just reproduce the original query.

                You will call the appropriate tool to execute the query after running this check.
                """.format(dialect=db.dialect)
            system_message = {
                "role": "system",
                "content": check_query_system_prompt,
            }

            # Generate an artificial user message to check
            tool_call = state["messages"][-1].tool_calls[0]
            user_message = {"role": "user", "content": tool_call["args"]["query"]}
            llm_with_tools = llm.bind_tools([run_query_tool], tool_choice="any")
            response = llm_with_tools.invoke([system_message, user_message])
            response.id = state["messages"][-1].id
            return {"messages": [response]}
        def should_continue(state: MessagesState) -> Literal[END, "check_query"]:
            messages = state["messages"]
            last_message = messages[-1]
            if not last_message.tool_calls:
                return END
            else:
                return "check_query"


        builder = StateGraph(MessagesState)
        builder.add_node(determine_query_type)
        builder.add_node(list_tables)
        builder.add_node(call_get_schema)
        builder.add_node(get_schema_node, "get_schema")
        builder.add_node(generate_query)
        builder.add_node(check_query)
        builder.add_node(run_query_node, "run_query")
        
        builder.add_edge(START, "determine_query_type")
        builder.add_conditional_edges("determine_query_type", route_query)
        builder.add_edge("list_tables", "call_get_schema")
        builder.add_edge("call_get_schema", "get_schema")
        builder.add_edge("get_schema", "generate_query")
        builder.add_conditional_edges(
            "generate_query",
            should_continue,
        )
        builder.add_edge("check_query", "run_query")
        builder.add_edge("run_query", "generate_query")

        agent = builder.compile()
        for step in agent.stream(
            {"messages": [{"role": "user", "content": self.question}]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()
            
        final_anwser = step["messages"][-1]
        return final_anwser.content if isinstance(final_anwser, AIMessage) else final_anwser

def main():
    patient_id = 143
    gemini_key = "your_gemini_api_key_here"
    question = "What treaments the patient has recently?"
    agent = DatabaseAgent(patient_id, gemini_key, question)
    final_answer = agent.create_agent()
    print(final_answer)

if __name__ == "__main__":
    main()