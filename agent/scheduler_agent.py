"""
PawPal+ Scheduler Agent — OpenAI function-calling loop.

Flow:
  1. User message → OpenAI (with tool schemas)
  2. OpenAI emits tool_calls → we execute matching tool closures
  3. Tool results sent back → OpenAI emits next response
  4. Repeat until OpenAI returns a plain-text message (no more tool calls)

The tool closures each close over a single SchedulerTools instance so the
agent and the Streamlit UI can share the same Schedule state.
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

from agent.tools import SchedulerTools

load_dotenv()

SYSTEM_PROMPT = """You are PawPal+, a friendly AI assistant that helps pet owners
plan and optimise their daily pet care schedules.

Guidelines:
- Be concise and warm in tone.
- After adding tasks, always call check_conflicts to surface budget or duplicate issues.
- When asked to build or show a schedule, call get_schedule then summarise it clearly.
- Flag immediately if the time budget would be exceeded.
- Durations are always in minutes.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a pet care task. priority is 1 (lowest) to 10 (highest).",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_type":        {"type": "string", "description": "Name of the care task"},
                    "duration_minutes": {"type": "integer", "description": "Duration in minutes"},
                    "priority":         {"type": "integer", "description": "Priority 1–10"},
                    "notes":            {"type": "string", "description": "Optional notes"},
                },
                "required": ["task_type", "duration_minutes", "priority"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remove_task",
            "description": "Remove all tasks with the given name from the schedule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_type": {"type": "string"},
                },
                "required": ["task_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Return all tasks currently in the schedule as JSON.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_schedule",
            "description": "Return the prioritised schedule (highest priority first).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_conflicts",
            "description": "Check for budget overruns, duplicate tasks, or all-completed state.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark all tasks with the given name as completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_type": {"type": "string"},
                },
                "required": ["task_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Return a high-level summary: owner, pet, task count, and budget status.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reset_schedule",
            "description": "Clear every task from the schedule.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


class SchedulerAgent:
    """
    Wraps an OpenAI chat session with a manual tool loop.

    Pass an existing SchedulerTools instance via `tools_instance` to share
    state with the Streamlit UI; omit it to create a fresh one.
    """

    def __init__(
        self,
        owner_name: str = "Owner",
        pet_name: str = "Pet",
        available_minutes: int = 120,
        tools_instance: Optional[SchedulerTools] = None,
    ):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. "
                "Add GROQ_API_KEY=<your_key> to your .env file."
            )
        self._client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

        self._inst = tools_instance or SchedulerTools(
            owner_name, pet_name, available_minutes
        )
        inst = self._inst

        self._tool_map = {
            "add_task":       lambda **kw: inst.add_task(**kw),
            "remove_task":    lambda **kw: inst.remove_task(**kw),
            "list_tasks":     lambda **kw: inst.list_tasks(),
            "get_schedule":   lambda **kw: inst.get_schedule(),
            "check_conflicts":lambda **kw: inst.check_conflicts(),
            "complete_task":  lambda **kw: inst.complete_task(**kw),
            "get_summary":    lambda **kw: inst.get_summary(),
            "reset_schedule": lambda **kw: inst.reset_schedule(),
        }

        self._messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # ----------------------------------------------------------------- public

    def run(self, user_message: str) -> str:
        """Send *user_message* and run the tool loop until a text reply arrives."""
        self._messages.append({"role": "user", "content": user_message})

        while True:
            response = self._client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                tools=TOOLS,
                messages=self._messages,
            )
            msg = response.choices[0].message
            self._messages.append(msg)

            if not msg.tool_calls:
                return msg.content

            for tc in msg.tool_calls:
                fn = self._tool_map.get(tc.function.name)
                args = json.loads(tc.function.arguments) or {}
                result = fn(**args) if fn else f"Unknown tool: {tc.function.name}"
                self._messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

    @property
    def schedule(self):
        """Direct access to the underlying Schedule object (for the UI)."""
        return self._inst.schedule
