from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools import ArxivQueryRun
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the language model
llm = ChatGroq(
    model="llama3-8b-8192",  # Changed model_name to model
    groq_api_key=groq_api_key,
    max_retries=1,
    temperature=0.0
)

tools = [ArxivQueryRun()]


template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:
Thought: [Your thought process]
Action: [The action to take, should be one of [{tool_names}]]
Action Input: [The input to the action]
Observation: [The result of the action]

When you have a final answer, provide it in this format:
Final Answer: [Your final answer]

Question: {input}
Thought: {agent_scratchpad}
"""

prompt = PromptTemplate.from_template(template)
agent = create_react_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True 
)

# Execute the query
result = agent_executor.invoke({
    "input": "What's the paper 1605.08386 about?"
})

print(result['output']) 