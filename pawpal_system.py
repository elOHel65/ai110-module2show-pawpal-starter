"""PawPal+ design skeletons; method bodies intentionally have no logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    care_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: str  # Intended values: "low", "medium", "high".
    scheduled_time: datetime | None = None
    recurrence: str | None = None  # None means a one-off task.
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Scheduler:
    owner: Owner

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order candidate tasks by priority and owner preferences."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return pairs of tasks with overlapping scheduled intervals."""
        pass

    def generate_daily_plan(self, plan_date: date) -> list[Task]:
        """Select the owner's pets' tasks within the daily time budget."""
        pass
