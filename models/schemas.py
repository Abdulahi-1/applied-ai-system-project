from dataclasses import dataclass, field


@dataclass
class Task:
    task_type: str
    duration_minutes: int
    priority: int  # 1–10
    notes: str = ""
    is_completed: bool = False

    def complete(self) -> None:
        self.is_completed = True

    def is_high_priority(self) -> bool:
        return self.priority >= 8

    def get_summary(self) -> str:
        status = "✅" if self.is_completed else "⏳"
        return f"{status} {self.task_type} — {self.duration_minutes} min (priority {self.priority})"

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "notes": self.notes,
            "is_completed": self.is_completed,
        }


@dataclass
class Pet:
    name: str
    breed: str
    size: str       # small | medium | large
    species: str    # dog | cat | other
    age_years: int
    health_notes: str = ""

    def get_profile(self) -> dict:
        return {
            "name": self.name,
            "breed": self.breed,
            "size": self.size,
            "species": self.species,
            "age_years": self.age_years,
            "health_notes": self.health_notes,
        }

    def update_health_notes(self, notes: str) -> None:
        self.health_notes = notes


@dataclass
class Owner:
    name: str
    email: str
    available_minutes: int
    pets: list = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def set_available_time(self, minutes: int) -> None:
        self.available_minutes = minutes

    def get_preferences(self) -> list[str]:
        return self.preferences


@dataclass
class Schedule:
    owner: Owner
    pet: Pet
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_type: str) -> int:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_type != task_type]
        return before - len(self.tasks)

    def generate_plan(self) -> list[Task]:
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def get_total_duration(self) -> int:
        return sum(t.duration_minutes for t in self.tasks)

    def is_over_budget(self) -> bool:
        return self.get_total_duration() > self.owner.available_minutes

    def check_conflicts(self) -> list[str]:
        warnings: list[str] = []
        total = self.get_total_duration()
        budget = self.owner.available_minutes

        if total > budget:
            overage = total - budget
            warnings.append(
                f"Tasks total {total} min but {self.owner.name} only has "
                f"{budget} min available ({overage} min over budget)."
            )

        seen: set[str] = set()
        for task in self.tasks:
            if task.task_type in seen:
                warnings.append(
                    f"Duplicate task detected: '{task.task_type}' appears more than once."
                )
            seen.add(task.task_type)

        if self.tasks and all(t.is_completed for t in self.tasks):
            warnings.append("All tasks are already marked as completed.")

        return warnings

    def explain_plan(self) -> str:
        total = self.get_total_duration()
        budget = self.owner.available_minutes
        remaining = budget - total
        if remaining >= 0:
            return f"Plan fits within budget — {remaining} min to spare."
        return f"Plan exceeds budget by {-remaining} min."

    def to_dict(self) -> dict:
        return {
            "owner": self.owner.name,
            "pet": self.pet.name,
            "budget_minutes": self.owner.available_minutes,
            "total_minutes": self.get_total_duration(),
            "tasks": [t.to_dict() for t in self.tasks],
        }
