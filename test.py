
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()
import os
groq_api_key=os.getenv("GROQ_API_KEY")

llm = ChatGroq(
     model_name="llama3-8b-8192",
    groq_api_key=groq_api_key,
    max_retries=1,
    temperature=0.0)
tools = load_tools(
    ["arxiv"],
)
template ="""Answer the following questions as best you can. You have access to the following tools
{tools}:
Action: the action to take, should be one of [{tool_names}]
Thought:{agent_scratchpad}
Question:{input}
 """
prompt = PromptTemplate.from_template(template)
def _handle_error(error) -> str:
    return str(error)[:50]
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, 
                               tools=tools,
                               verbose=True,
                               handle_parsing_errors=_handle_error
                               )

result=agent_executor.invoke(
    {
        "input": "What's the paper 1605.08386 about?",
    }
)

print(result)