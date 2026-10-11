"""PawPal+ pet care models and basic daily scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks from every pet belonging to the owner."""
        return [task for pet in self.pets for task in pet.tasks]


@dataclass
class Pet:
    name: str
    species: str
    care_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's tasks."""
        self.tasks.append(task)


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: str  # Intended values: "low", "medium", "high".
    scheduled_time: datetime | None = None
    recurrence: str | None = None  # None means a one-off task.
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Scheduler:
    owner: Owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort by high, medium, low priority, then time with unscheduled last."""
        priorities = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            tasks,
            key=lambda task: (
                priorities[task.priority],
                task.scheduled_time is None,
                task.scheduled_time,
            ),
        )

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of tasks with overlapping scheduled intervals."""
        scheduled = [task for task in tasks if task.scheduled_time is not None]
        conflicts = []
        for index, first in enumerate(scheduled):
            first_end = first.scheduled_time + timedelta(minutes=first.duration_minutes)
            for second in scheduled[index + 1:]:
                second_end = second.scheduled_time + timedelta(minutes=second.duration_minutes)
                if first.scheduled_time < second_end and second.scheduled_time < first_end:
                    conflicts.append((first, second))
        return conflicts

    def generate_daily_plan(self, plan_date: date) -> list[Task]:
        """Select the owner's pets' tasks within the daily time budget."""
        candidates = [
            task for task in self.owner.get_all_tasks()
            if not task.completed
            and (
                task.recurrence is not None
                or task.scheduled_time is None
                or task.scheduled_time.date() == plan_date
            )
        ]
        remaining = self.owner.available_minutes
        plan = []
        for task in self.sort_tasks(candidates):
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan
