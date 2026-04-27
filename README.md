# PawPal+ — Applied AI Scheduling System

A Gemini-powered pet care scheduler with a Streamlit UI and a function-calling agent loop.

## Project structure

```
applied-ai-system-project/
├── app.py                    # Streamlit UI (manual + AI chat)
├── agent/
│   ├── scheduler_agent.py    # Gemini agent + manual tool loop
│   └── tools.py              # SchedulerTools — stateful tool layer
├── models/
│   └── schemas.py            # Task, Pet, Owner, Schedule dataclasses
├── tests/
│   └── test_scheduler.py     # 36 pytest unit tests (no API key needed)
├── .env                      # GEMINI_API_KEY (gitignored)
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

Add your key to `.env`:

```
GEMINI_API_KEY=your_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey).

## Run the app

```bash
streamlit run app.py
```

The manual scheduling UI works without an API key.  The AI Assistant section
activates once `GEMINI_API_KEY` is set.

## Run tests

```bash
pytest tests/
```

All 36 tests run without a Gemini API key.

## Architecture

### Agent loop (`agent/scheduler_agent.py`)

![Agent loop](assets/agent_loop.png)

`SchedulerAgent` passes Python callables as tools; the SDK builds the JSON
schema from their signatures and docstrings.  The manual tool loop in `run()`
iterates until Gemini returns a message with no `function_call` parts.

### Shared state

![Architecture](assets/architecture.png)

`SchedulerAgent` accepts an existing `SchedulerTools` instance so the AI chat
and the manual Streamlit UI operate on the **same** `Schedule` object — any
task the agent adds is immediately visible in the task table.

### Class diagram

![Class diagram](assets/class_diagram.png)

### Available tools

| Tool | What it does |
|---|---|
| `add_task` | Add a care task with type, duration, and priority |
| `remove_task` | Remove tasks by name |
| `list_tasks` | JSON list of all tasks |
| `get_schedule` | Priority-sorted schedule |
| `check_conflicts` | Budget overruns, duplicates, all-done state |
| `complete_task` | Mark a task as done |
| `get_summary` | High-level owner/pet/budget snapshot |
| `reset_schedule` | Clear all tasks |

## Example AI prompts

- "Add a 30-minute morning walk at high priority"
- "Build me a schedule for Mochi with feeding, grooming, and playtime"
- "Check if there are any conflicts"
- "I finished the walk — mark it complete"
- "Remove the grooming task"
