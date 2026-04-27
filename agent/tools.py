import json
from models.schemas import Task, Schedule, Owner, Pet


class SchedulerTools:
    """
    Stateful tool layer that backs the Gemini scheduler agent.

    Every public method returns a plain string so Gemini can read the result
    and decide what to do next.  The underlying Schedule object is also
    accessible directly for the Streamlit UI.
    """

    def __init__(
        self,
        owner_name: str = "Owner",
        pet_name: str = "Pet",
        available_minutes: int = 120,
        species: str = "other",
        breed: str = "Unknown",
        size: str = "medium",
        age_years: int = 0,
    ):
        owner = Owner(name=owner_name, email="", available_minutes=available_minutes)
        pet = Pet(name=pet_name, breed=breed, size=size, species=species, age_years=age_years)
        self.schedule = Schedule(owner=owner, pet=pet)

    # ------------------------------------------------------------------ tools

    def add_task(
        self,
        task_type: str,
        duration_minutes: int,
        priority: int,
        notes: str = "",
    ) -> str:
        if not (1 <= priority <= 10):
            return "Error: priority must be between 1 and 10."
        if duration_minutes <= 0:
            return "Error: duration_minutes must be positive."
        self.schedule.add_task(
            Task(
                task_type=task_type,
                duration_minutes=duration_minutes,
                priority=priority,
                notes=notes,
            )
        )
        return f"Added '{task_type}' ({duration_minutes} min, priority {priority})."

    def remove_task(self, task_type: str) -> str:
        removed = self.schedule.remove_task(task_type)
        if removed:
            return f"Removed {removed} task(s) named '{task_type}'."
        return f"No task named '{task_type}' found."

    def list_tasks(self) -> str:
        if not self.schedule.tasks:
            return "No tasks scheduled."
        return json.dumps([t.to_dict() for t in self.schedule.tasks], indent=2)

    def get_schedule(self) -> str:
        plan = self.schedule.generate_plan()
        if not plan:
            return "No tasks to schedule."
        lines = [f"{i + 1}. {t.get_summary()}" for i, t in enumerate(plan)]
        return "\n".join(lines)

    def check_conflicts(self) -> str:
        warnings = self.schedule.check_conflicts()
        return "\n".join(warnings) if warnings else "No conflicts detected."

    def complete_task(self, task_type: str) -> str:
        matched = [t for t in self.schedule.tasks if t.task_type == task_type]
        if not matched:
            return f"No task named '{task_type}' found."
        for t in matched:
            t.complete()
        return f"Marked {len(matched)} task(s) '{task_type}' as completed."

    def get_summary(self) -> str:
        total = self.schedule.get_total_duration()
        budget = self.schedule.owner.available_minutes
        remaining = budget - total
        status = "within budget" if remaining >= 0 else "OVER budget"
        return (
            f"Owner: {self.schedule.owner.name} | Pet: {self.schedule.pet.name}\n"
            f"Tasks: {len(self.schedule.tasks)} | Total: {total} min | Budget: {budget} min\n"
            f"Status: {status} "
            f"({abs(remaining)} min {'remaining' if remaining >= 0 else 'over'})"
        )

    def reset_schedule(self) -> str:
        count = len(self.schedule.tasks)
        self.schedule.tasks.clear()
        return f"Cleared {count} task(s) from the schedule."

    def dispatch(self, name: str, args: dict) -> str:
        """Route a function name + args dict to the matching tool method."""
        handlers: dict[str, object] = {
            "add_task": lambda a: self.add_task(**a),
            "remove_task": lambda a: self.remove_task(**a),
            "list_tasks": lambda _: self.list_tasks(),
            "get_schedule": lambda _: self.get_schedule(),
            "check_conflicts": lambda _: self.check_conflicts(),
            "complete_task": lambda a: self.complete_task(**a),
            "get_summary": lambda _: self.get_summary(),
            "reset_schedule": lambda _: self.reset_schedule(),
        }
        handler = handlers.get(name)
        return handler(args) if handler else f"Unknown tool: {name}"
