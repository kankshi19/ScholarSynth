# Step1: Define state
from typing_extensions import TypedDict
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Step2: Define ToolNode & Tools
from arxiv_tool import *
from read_pdf import *
from write_pdf import * 
from langgraph.prebuilt import ToolNode

tools = [arxiv_search, read_pdf, render_latex_pdf]
tool_node = ToolNode(tools)


# Step3: Setup LLM
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Token-control knobs for lower latency/cost.
MAX_MODEL_CONTEXT_MESSAGES = int(os.getenv("MAX_MODEL_CONTEXT_MESSAGES", "10"))
MAX_TOOL_MESSAGE_CHARS = int(os.getenv("MAX_TOOL_MESSAGE_CHARS", "4000"))
MAX_TEXT_MESSAGE_CHARS = int(os.getenv("MAX_TEXT_MESSAGE_CHARS", "6000"))

def build_model():
    # Prefer OpenRouter when OPENROUTER_API_KEY is present.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_api_key:
        openrouter_model = os.getenv("OPENROUTER_MODEL", "openrouter/free")
        llm = ChatOpenAI(
            model=openrouter_model,
            api_key=openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
        )
        return llm.bind_tools(tools)

    # Fallback to Gemini if OpenRouter key is not set.
    google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if google_api_key:
        llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
            api_key=google_api_key,
            temperature=0.2,
        )
        return llm.bind_tools(tools)

    raise ValueError(
        "No API key found. Set OPENROUTER_API_KEY (preferred) or GOOGLE_API_KEY/GEMINI_API_KEY."
    )

model = build_model()

# Step4: Setup graph

#from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, StateGraph

def _trim_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated for token optimization]"


def _compact_messages(messages: list) -> list:
    if not messages:
        return messages

    # Keep system prompt if present, then only recent context.
    system_msg = messages[0] if getattr(messages[0], "type", "") == "system" else None
    rest = messages[1:] if system_msg else messages[:]
    rest = rest[-MAX_MODEL_CONTEXT_MESSAGES:]

    compacted = []
    if system_msg is not None:
        compacted.append(system_msg)

    for msg in rest:
        msg_type = getattr(msg, "type", "")
        content = getattr(msg, "content", "")
        if not isinstance(content, str):
            compacted.append(msg)
            continue
        if msg_type == "tool":
            msg.content = _trim_text(content, MAX_TOOL_MESSAGE_CHARS)
        else:
            msg.content = _trim_text(content, MAX_TEXT_MESSAGE_CHARS)
        compacted.append(msg)

    return compacted


def call_model(state: State):
    messages = _compact_messages(state["messages"])
    response = model.invoke(messages)
    return {"messages": [response]}


def should_continue(state: State) -> Literal["tools", END]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow = StateGraph(State)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
config = {"configurable": {"thread_id": 222222}}

graph = workflow.compile(checkpointer=checkpointer)

# Step5: TESTING
INITIAL_PROMPT = """
You are an expert research assistant for: physics, mathematics, computer science,
quantitative biology, quantitative finance, statistics, electrical engineering,
systems science, and economics.

Workflow:
1. Clarify the topic with the user.
2. Use arxiv.org (via available tools) for recent papers.
3. Summarize key papers and discuss future directions.
4. Propose new research ideas and refine with user feedback.
5. When asked, write a LaTeX paper with equations and render it to PDF.

Rules:
- Prefer concise, high-signal responses.
- Cite arXiv links when referencing papers.
- Use tools when needed; avoid unnecessary tool calls.
- Ensure LaTeX compiles cleanly before finalizing.
"""

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        print(f"Message received: {message.content[:200]}...")
        message.pretty_print()

"""while True:
    user_input = input("User: ")
    if user_input:
        messages = [
                    {"role": "system", "content": INITIAL_PROMPT},
                    {"role": "user", "content": user_input}
                ]
        input_data = {
            "messages" : messages
        }
        print_stream(graph.stream(input_data, config, stream_mode="values"))"""
