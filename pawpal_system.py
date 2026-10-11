"""PawPal+ pet care models and basic daily scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
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

    def complete_task(self, task: Task, completion_date: date) -> Task | None:
        """Complete an owned occurrence once and append its next recurring occurrence."""
        if not any(existing is task for existing in self.tasks):
            raise ValueError("Task does not belong to this pet.")
        if task.completed:
            return None
        next_task = None
        if task.recurrence is not None:
            if task.recurrence not in ("daily", "weekly") or task.scheduled_time is None:
                raise ValueError("Recurring tasks require daily/weekly recurrence and a scheduled time.")
            interval = 1 if task.recurrence == "daily" else 7
            days_late = (completion_date - task.scheduled_time.date()).days
            steps = max(1, days_late // interval + 1)
            next_task = replace(
                task,
                scheduled_time=task.scheduled_time + timedelta(days=interval * steps),
                completed=False,
            )
        task.mark_complete()
        if next_task is not None:
            self.add_task(next_task)
        return next_task


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: str  # Intended values: "low", "medium", "high".
    scheduled_time: datetime | None = None
    recurrence: str | None = None  # None means a one-off task.
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate recurrence values and require a scheduled recurring occurrence."""
        if self.recurrence not in (None, "daily", "weekly"):
            raise ValueError("Recurrence must be None, daily, or weekly.")
        if self.recurrence is not None and self.scheduled_time is None:
            raise ValueError("Recurring tasks require a scheduled date and time.")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Scheduler:
    owner: Owner

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks chronologically, placing unscheduled tasks last."""
        return sorted(tasks, key=lambda task: (task.scheduled_time is None, task.scheduled_time))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Filter across pets by exact name and/or completion, preserving pet/task pairs."""
        return [
            (pet, task)
            for pet in self.owner.pets
            if pet_name is None or pet.name == pet_name
            for task in pet.tasks
            if completed is None or task.completed == completed
        ]

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

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[tuple[Task, Task]]:
        """Return overlapping pairs from supplied tasks or all pets' incomplete tasks."""
        if tasks is None:
            tasks = [task for _, task in self.filter_tasks(completed=False)]
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
                (task.recurrence is not None and task.scheduled_time.date() <= plan_date)
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
