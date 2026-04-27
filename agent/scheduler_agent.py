"""
PawPal+ Scheduler Agent — Gemini function-calling loop.

Flow:
  1. User message → Gemini (with tool schemas from callable signatures/docstrings)
  2. Gemini emits FunctionCall parts → we execute matching tool closures
  3. Tool results sent back → Gemini emits next response
  4. Repeat until Gemini returns a plain-text message (no more function calls)

The tool closures each close over a single SchedulerTools instance so the
agent and the Streamlit UI can share the same Schedule state.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

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


class SchedulerAgent:
    """
    Wraps a Gemini chat session with a manual tool loop.

    Pass an existing SchedulerTools instance via `tools_instance` to share
    state with the Streamlit UI; omit it to create a fresh one.
    """

    def __init__(
        self,
        owner_name: str = "Owner",
        pet_name: str = "Pet",
        available_minutes: int = 120,
        tools_instance: SchedulerTools | None = None,
    ):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Add GEMINI_API_KEY=<your_key> to your .env file."
            )
        genai.configure(api_key=api_key)

        self._inst = tools_instance or SchedulerTools(
            owner_name, pet_name, available_minutes
        )
        inst = self._inst  # shorthand for closures below

        # --------------------------------------------------------------- tools
        # Each closure delegates to SchedulerTools and returns a plain string.
        # The SDK reads the function signature + one-line docstring to build
        # the JSON schema it sends to Gemini.

        def add_task(task_type: str, duration_minutes: int, priority: int, notes: str = "") -> str:
            """Add a pet care task. priority is 1 (lowest) to 10 (highest)."""
            return inst.add_task(task_type, duration_minutes, priority, notes)

        def remove_task(task_type: str) -> str:
            """Remove all tasks with the given name from the schedule."""
            return inst.remove_task(task_type)

        def list_tasks() -> str:
            """Return all tasks currently in the schedule as JSON."""
            return inst.list_tasks()

        def get_schedule() -> str:
            """Return the prioritised schedule (highest priority first)."""
            return inst.get_schedule()

        def check_conflicts() -> str:
            """Check for budget overruns, duplicate tasks, or all-completed state."""
            return inst.check_conflicts()

        def complete_task(task_type: str) -> str:
            """Mark all tasks with the given name as completed."""
            return inst.complete_task(task_type)

        def get_summary() -> str:
            """Return a high-level summary: owner, pet, task count, and budget status."""
            return inst.get_summary()

        def reset_schedule() -> str:
            """Clear every task from the schedule."""
            return inst.reset_schedule()

        self._tool_map: dict[str, object] = {
            "add_task": add_task,
            "remove_task": remove_task,
            "list_tasks": list_tasks,
            "get_schedule": get_schedule,
            "check_conflicts": check_conflicts,
            "complete_task": complete_task,
            "get_summary": get_summary,
            "reset_schedule": reset_schedule,
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            tools=list(self._tool_map.values()),
            system_instruction=SYSTEM_PROMPT,
        )
        self.chat = self.model.start_chat()

    # ----------------------------------------------------------------- public

    def run(self, user_message: str) -> str:
        """Send *user_message* and run the tool loop until a text reply arrives."""
        response = self.chat.send_message(user_message)

        # Tool loop — Gemini may chain multiple rounds of function calls before
        # producing a final text response.
        while True:
            function_calls = [
                part.function_call
                for part in response.parts
                if hasattr(part, "function_call") and part.function_call.name
            ]
            if not function_calls:
                break

            # Execute every function call and collect results
            result_parts = []
            for fc in function_calls:
                fn = self._tool_map.get(fc.name)
                result = fn(**dict(fc.args)) if fn else f"Unknown tool: {fc.name}"
                result_parts.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=fc.name,
                            response={"result": result},
                        )
                    )
                )

            response = self.chat.send_message(result_parts)

        return response.text

    @property
    def schedule(self):
        """Direct access to the underlying Schedule object (for the UI)."""
        return self._inst.schedule
