import logging
import logging
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components
from langchain_core.messages import AIMessage, ToolMessage

from ai_researcher_2 import INITIAL_PROMPT, config, graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Researchify", page_icon=":mag:", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f4f6f8;
        --ink: #1f2933;
        --sub: #64748b;
        --card: #ffffff;
        --line: #e5eaf0;
        --accent: #7c97ef;
    }

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        color: var(--ink);
        background: var(--bg);
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(163, 190, 217, 0.18) 0, rgba(163, 190, 217, 0) 35%),
            radial-gradient(circle at 92% 18%, rgba(243, 206, 214, 0.22) 0, rgba(243, 206, 214, 0) 34%),
            radial-gradient(circle at 92% 82%, rgba(246, 222, 174, 0.18) 0, rgba(246, 222, 174, 0) 30%),
            #f4f6f8;
    }

    .block-container {
        max-width: 980px;
        padding-top: max(3rem, env(safe-area-inset-top));
        padding-bottom: 8rem;
    }

    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(8px);
    }

    .hero-wrap {
        text-align: center;
        margin-bottom: 0.9rem;
    }

    .hero-title {
        font-size: clamp(36px, 6vw, 64px);
        font-weight: 800;
        color: #2a3440;
        line-height: 1.08;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }

    .brand-line {
        display: block;
        font-size: clamp(50px, 8vw, 88px);
        font-weight: 800;
        background: linear-gradient(90deg, #111827 0%, #1f3a5f 45%, #5b6ee1 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
        margin-bottom: 0.15rem;
        text-shadow: 0 10px 26px rgba(91, 110, 225, 0.18);
    }

    .hero-sub {
        font-size: 20px;
        color: #6a7482;
        margin-bottom: 0.9rem;
    }

    .trust-pill {
        width: fit-content;
        margin: 1rem auto 1.6rem auto;
        padding: 10px 16px;
        border-radius: 999px;
        border: 1px solid #e1e7ee;
        background: rgba(255, 255, 255, 0.78);
        color: #5a6574;
        font-size: 14px;
    }

    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        border: 1px solid var(--line);
        margin-bottom: 0.75rem;
        padding: 10px 12px 16px 12px;
        background: #fbfcfd;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06);
        animation: fadein 260ms ease-in-out;
    }

    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #f0f6ff;
        border-color: #d8e5ff;
    }

    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #ffffff;
    }

    div[data-testid="stChatMessageContent"],
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stMarkdownContainer"] * {
        color: #2d2d2d !important;
        line-height: 1.6;
        font-size: 16px;
    }

    div[data-testid="stMarkdownContainer"] p:last-child,
    div[data-testid="stMarkdownContainer"] ul:last-child,
    div[data-testid="stMarkdownContainer"] ol:last-child,
    div[data-testid="stMarkdownContainer"] table:last-child {
        margin-bottom: 0.65rem !important;
    }

    div[data-testid="stMarkdownContainer"] th,
    div[data-testid="stMarkdownContainer"] td {
        background: rgba(255, 255, 255, 0.55);
        border-color: #dbe3ec;
    }

    .live-chip {
        display: inline-block;
        border: 1px solid #d8e0ea;
        border-radius: 999px;
        padding: 6px 10px;
        background: #f5f8fb;
        color: #4a6178;
        font-size: 12px;
        font-weight: 500;
        margin-top: 4px;
        animation: fadein 240ms ease-in-out;
    }

    .mini-log {
        font-size: 12px;
        color: #5a7188;
        border-left: 2px solid #d0dfef;
        padding-left: 10px;
        margin-top: 7px;
        animation: fadein 240ms ease-in-out;
    }

    div[data-testid="stChatInput"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
        padding: 8px;
        transition: all 240ms ease-in-out;
        max-width: 980px;
        margin: 0 auto;
    }

    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] form,
    div[data-testid="stChatInput"] section,
    div[data-testid="stChatInput"] [data-baseweb="textarea"],
    div[data-testid="stChatInput"] [data-baseweb="textarea"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 14px !important;
    }

    div[data-testid="stChatInput"] textarea {
        font-size: 18px;
        color: #2d2d2d !important;
        -webkit-text-fill-color: #2d2d2d !important;
        background: #ffffff !important;
        border-radius: 14px !important;
        caret-color: #2d2d2d !important;
        line-height: 1.4 !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
        padding-left: 2px !important;
        padding-right: 2px !important;
        text-shadow: none !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #697586 !important;
        opacity: 1 !important;
    }

    div[data-testid="stChatInput"] textarea:focus::placeholder {
        color: transparent !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: #cfd8e3;
        box-shadow: 0 0 0 3px rgba(156, 175, 201, 0.20), 0 8px 28px rgba(15, 23, 42, 0.10);
    }

    button[kind="secondaryFormSubmit"] {
        border-radius: 999px !important;
        background: var(--accent) !important;
        color: white !important;
        border: 1px solid #7e98ea !important;
        box-shadow: 0 3px 10px rgba(124, 151, 239, 0.35) !important;
        transition: transform 220ms ease-in-out;
    }

    button[kind="secondaryFormSubmit"]:active {
        transform: scale(0.95);
    }

    div[data-testid="stButton"] button {
        border-radius: 10px !important;
        background: #eef2ff !important;
        color: #1f2a44 !important;
        border: 1px solid #d8e1ff !important;
    }

    div[data-testid="stButton"] button:hover {
        background: #e4ebff !important;
        color: #18233d !important;
    }

    @keyframes fadein {
        from { opacity: 0; transform: translateY(4px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-wrap">
      <div class="hero-title">
        <span class="brand-line">Researchify</span>
        AI for Research, Grounded in Evidence
      </div>
      <div class="hero-sub">Ask about any topic you want to research about</div>
    </div>
    """,
    unsafe_allow_html=True,
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "latest_pdf_path" not in st.session_state:
    st.session_state.latest_pdf_path = None
if "latest_pdf_filename" not in st.session_state:
    st.session_state.latest_pdf_filename = None
if "latest_tex_path" not in st.session_state:
    st.session_state.latest_tex_path = None
if "latest_tex_filename" not in st.session_state:
    st.session_state.latest_tex_filename = None
if "research_mode" not in st.session_state:
    st.session_state.research_mode = False
if "show_pdf_download" not in st.session_state:
    st.session_state.show_pdf_download = False

NON_RESEARCH_REPLY = "I’m Researchify, a research assistant. Tell me what you want to research, and I’ll help you."
MAX_CONTEXT_MESSAGES = 8
MAX_CONTEXT_CHARS = 12000


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return str(content)


def _is_tool_trace_text(text: str) -> bool:
    t = text.strip()
    if not t:
        return False
    if t.startswith("OLCALL>") or t.endswith("ALL>"):
        return True
    if "TOOLCALL" in t.upper() or "TOOL_CALL" in t.upper():
        return True
    return False


def _infer_phase(label: str) -> str:
    low = label.lower()
    if "arxiv" in low or "search" in low:
        return "Searching"
    if "read" in low or "pdf" in low:
        return "Reading"
    if "render" in low or "latex" in low or "write" in low:
        return "Writing"
    if "prompt" in low:
        return "Planning"
    return "Researching"


def _log_line(label: str, kind: str = "step") -> str:
    ts = datetime.now().strftime("%H:%M:%S")
    phase = _infer_phase(label)
    return f"<div class='mini-log'>[{ts}] <b>{phase}</b> · {kind}: {label}</div>"


def isResearchQuery(text: str) -> bool:
    cleaned = re.sub(r"[^a-zA-Z\\s]", " ", text).strip().lower()
    if not cleaned:
        return False
    research_keywords = {
        "research",
        "paper",
        "study",
        "analysis",
        "algorithm",
        "model",
        "ai",
        "ml",
        "data",
        "report",
        "thesis",
        "summary",
        "compare",
        "method",
        "explain",
    }
    tokens = set(cleaned.split())
    if tokens.intersection(research_keywords):
        return True
    phrase_hits = [
        "state of the art",
        "literature review",
        "future work",
        "recent papers",
        "arxiv",
    ]
    return any(p in cleaned for p in phrase_hits)


def _is_smalltalk(text: str) -> bool:
    cleaned = re.sub(r"[^a-zA-Z\\s]", " ", text).strip().lower()
    if not cleaned:
        return False
    smalltalk_exact = {
        "hi",
        "hello",
        "hey",
        "yo",
        "hii",
        "heyy",
        "hola",
        "how are you",
        "how is it going",
        "hows it going",
        "what s up",
        "whats up",
        "sup",
        "good morning",
        "good afternoon",
        "good evening",
    }
    if cleaned in smalltalk_exact:
        return True
    return len(cleaned.split()) <= 6 and any(
        cleaned.startswith(p) for p in ("how are you", "how is it going", "good morning", "good afternoon", "good evening")
    )


def _is_topic_like_short_reply(text: str) -> bool:
    cleaned = re.sub(r"[^a-zA-Z0-9\\s\\-]", " ", text).strip().lower()
    if not cleaned:
        return False
    if len(cleaned.split()) > 6:
        return False
    if _is_smalltalk(cleaned):
        return False
    return True


def _should_call_research_agent(text: str) -> bool:
    if isResearchQuery(text):
        return True
    if st.session_state.research_mode and _is_topic_like_short_reply(text):
        return True
    return False


def _build_compact_context(history: list[dict[str, str]]) -> list[dict[str, str]]:
    filtered = [m for m in history if m["role"] in {"user", "assistant"}]
    recent = filtered[-MAX_CONTEXT_MESSAGES:]
    total_chars = sum(len(m["content"]) for m in recent)
    while total_chars > MAX_CONTEXT_CHARS and len(recent) > 2:
        removed = recent.pop(0)
        total_chars -= len(removed["content"])
    return [{"role": m["role"], "content": m["content"]} for m in recent]


def _maybe_capture_rendered_pdf(tool_content: Any) -> None:
    if tool_content is None:
        return
    text = tool_content if isinstance(tool_content, str) else str(tool_content)
    try:
        payload = json.loads(text)
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    pdf_path = payload.get("pdf_path")
    pdf_filename = payload.get("pdf_filename")
    tex_path = payload.get("tex_path")
    tex_filename = payload.get("tex_filename")
    if pdf_path and pdf_filename:
        st.session_state.latest_pdf_path = pdf_path
        st.session_state.latest_pdf_filename = pdf_filename
        st.session_state.show_pdf_download = True
    if tex_path and tex_filename:
        st.session_state.latest_tex_path = tex_path
        st.session_state.latest_tex_filename = tex_filename


def _render_copy_icon(text: str, key: str) -> None:
    payload = json.dumps(text)
    components.html(
        f"""
        <div style="display:flex;justify-content:flex-end;align-items:center;gap:8px;">
          <button id="copy-{key}" title="Copy response"
            style="border:1px solid #d8e1ff;background:#eef2ff;color:#1f2a44;border-radius:10px;padding:6px 10px;cursor:pointer;font-size:14px;">
            📋
          </button>
          <span id="ok-{key}" style="font-size:12px;color:#5a6574;"></span>
        </div>
        <script>
          const btn = document.getElementById("copy-{key}");
          const ok = document.getElementById("ok-{key}");
          btn.addEventListener("click", async () => {{
            try {{
              await navigator.clipboard.writeText({payload});
              ok.textContent = "Copied";
              setTimeout(() => ok.textContent = "", 1200);
            }} catch (e) {{
              ok.textContent = "Copy failed";
              setTimeout(() => ok.textContent = "", 1200);
            }}
          }});
        </script>
        """,
        height=40,
    )


for idx, item in enumerate(st.session_state.chat_history):
    with st.chat_message(item["role"]):
        st.markdown(item["content"], unsafe_allow_html=item.get("html", False))
        if item["role"] == "assistant":
            _render_copy_icon(item["content"], key=f"hist_{idx}")


user_input = st.chat_input("Ask a research question...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    if _is_smalltalk(user_input):
        with st.chat_message("assistant"):
            st.markdown(NON_RESEARCH_REPLY)
        st.session_state.chat_history.append({"role": "assistant", "content": NON_RESEARCH_REPLY})
        st.stop()

    if not _should_call_research_agent(user_input):
        with st.chat_message("assistant"):
            st.markdown(NON_RESEARCH_REPLY)
        st.session_state.chat_history.append({"role": "assistant", "content": NON_RESEARCH_REPLY})
        st.stop()

    st.session_state.research_mode = True

    chat_input = {"messages": [{"role": "system", "content": INITIAL_PROMPT}] + _build_compact_context(st.session_state.chat_history)}

    logger.info("Starting agent processing...")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        live_status = st.empty()
        log_placeholder = st.empty()

        typing_frames = [
            "<span class='live-chip'>Researching.</span>",
            "<span class='live-chip'>Researching..</span>",
            "<span class='live-chip'>Researching...</span>",
            "<span class='live-chip'>Scanning papers...</span>",
            "<span class='live-chip'>Synthesizing answer...</span>",
        ]

        frame_idx = 0
        full_response = ""
        seen_tools = set()
        inline_logs = []
        turn_pdf_path = None
        turn_pdf_filename = None

        for state in graph.stream(chat_input, config, stream_mode="values"):
            message = state["messages"][-1]

            live_status.markdown(typing_frames[frame_idx % len(typing_frames)], unsafe_allow_html=True)
            frame_idx += 1

            if getattr(message, "tool_calls", None):
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get("name", "tool")
                    call_id = tool_call.get("id", f"{tool_name}-{frame_idx}")
                    if call_id not in seen_tools:
                        seen_tools.add(call_id)
                        inline_logs.append(_log_line(f"Calling `{tool_name}`", "tool"))

            if isinstance(message, ToolMessage):
                inline_logs.append(_log_line("Tool response received", "result"))
                _maybe_capture_rendered_pdf(message.content)
                try:
                    payload = json.loads(message.content if isinstance(message.content, str) else str(message.content))
                    if isinstance(payload, dict) and payload.get("pdf_path") and payload.get("pdf_filename"):
                        turn_pdf_path = payload["pdf_path"]
                        turn_pdf_filename = payload["pdf_filename"]
                        st.session_state.latest_pdf_path = turn_pdf_path
                        st.session_state.latest_pdf_filename = turn_pdf_filename
                        st.session_state.show_pdf_download = True
                except Exception:
                    pass

            if isinstance(message, AIMessage) and message.content:
                text_content = _content_to_text(message.content).strip()
                if text_content and not _is_tool_trace_text(text_content):
                    full_response = text_content
                    response_placeholder.write(full_response)

            if inline_logs:
                log_placeholder.markdown("".join(inline_logs[-8:]), unsafe_allow_html=True)

        live_status.empty()
        if inline_logs:
            log_placeholder.markdown("".join(inline_logs[-8:]), unsafe_allow_html=True)

    if full_response:
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})
        pdf_path_str = turn_pdf_path or st.session_state.latest_pdf_path
        pdf_name = turn_pdf_filename or st.session_state.latest_pdf_filename
        if st.session_state.show_pdf_download and pdf_path_str and pdf_name:
            with st.chat_message("assistant"):
                st.markdown("Your paper is ready.")
                pdf_path = Path(pdf_path_str)
                if pdf_path.exists():
                    with pdf_path.open("rb") as f:
                        st.download_button(
                            label="Download your PDF",
                            data=f.read(),
                            file_name=pdf_name,
                            mime="application/pdf",
                            key=f"pdf_btn_{len(st.session_state.chat_history)}",
                        )
