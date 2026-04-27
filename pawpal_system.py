from dataclasses import dataclass


@dataclass
class Pet:
    name: str
    breed: str
    size: str
    species: str
    age_years: int
    health_notes: str = ""

    def get_profile(self) -> dict:
        "gets the pet's profile information as a dictionary"
        return {
            "name": self.name,
            "breed": self.breed,
            "size": self.size,
            "species": self.species,
            "age_years": self.age_years,
            "health_notes": self.health_notes
        }

    def update_health_notes(self, notes: str) -> None:
        "updates the health notes for the pet"
        self.health_notes = notes


@dataclass
class CareTask:
    task_type: str
    duration_minutes: int
    priority: int
    notes: str = ""
    is_completed: bool = False

    def complete(self) -> None:
        "Marks the task as completed."
        self.is_completed = True

    def is_high_priority(self) -> bool:
        "Returns True if the task priority is 8 or above."
        return self.priority >= 8

    def get_summary(self) -> str:
        "Returns a short string summary of the task."
        return f"{self.task_type} - {self.duration_minutes} mins - Priority: {self.priority}"


class Owner:
    def __init__(self, name: str, email: str, available_minutes: int):
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.preferences: list[str] = []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        "Adds a pet to the owner's list of pets."
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        "Updates the owner's daily time budget in minutes."
        self.available_minutes = minutes

    def get_preferences(self) -> list[str]:
        "Returns the owner's list of care preferences."
        return self.preferences


class DailyScheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[CareTask] = []
        self.scheduled_plan: list[CareTask] = []

    def add_task(self, task: CareTask) -> None:
        "Adds a care task to the task pool."
        self.tasks.append(task)

    def remove_task(self, task_type: str) -> None:
        "Removes all tasks matching the given task type from the pool."
        self.tasks = [task for task in self.tasks if task.task_type != task_type]

    def generate_plan(self) -> list[CareTask]:
        "Sorts tasks by priority and returns the scheduled plan."
        # Placeholder for the actual scheduling algorithm
        self.scheduled_plan = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        return self.scheduled_plan

    def explain_plan(self) -> str:
        "Returns a plain-English explanation of the scheduled plan."
        return "Here's your daily care plan!"

    def get_total_duration(self) -> int:
        "Returns the total duration of all tasks in minutes."
        return sum(task.duration_minutes for task in self.tasks)

    def reset_plan(self) -> None:
        "Clears the current scheduled plan."
        self.scheduled_plan = []

    def check_conflicts(self) -> list[str]:
        "Returns a list of warning strings for any scheduling conflicts detected."
        warnings = []

        # Warn if total task time exceeds the owner's available time
        total = self.get_total_duration()
        if total > self.owner.available_minutes:
            overage = total - self.owner.available_minutes
            warnings.append(
                f"Tasks total {total} min but {self.owner.name} only has "
                f"{self.owner.available_minutes} min available ({overage} min over budget)."
            )

        # Warn about duplicate task types
        seen = set()
        for task in self.tasks:
            if task.task_type in seen:
                warnings.append(f"Duplicate task detected: '{task.task_type}' appears more than once.")
            seen.add(task.task_type)

        # Warn if all tasks are already completed
        if self.tasks and all(t.is_completed for t in self.tasks):
            warnings.append("All tasks are already marked as completed.")

        return warnings