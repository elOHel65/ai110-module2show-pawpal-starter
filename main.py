"""Demonstrate PawPal+ smarter scheduling with two pets."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title: str, pairs: list[tuple[Pet, Task]], scheduler: Scheduler) -> None:
    """Print pet-linked occurrences with times and completion status."""
    print(title)
    pet_by_task = {id(task): pet for pet, task in pairs}
    for task in scheduler.sort_by_time([task for _, task in pairs]):
        pet = pet_by_task[id(task)]
        start = task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled"
        status = "complete" if task.completed else "incomplete"
        print(f"{start} | {pet.name} | {task.name} | {task.duration_minutes} min | {task.priority} | {status}")


def main() -> None:
    """Demonstrate sorting, filtering, recurrence history, and cross-pet conflicts."""
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    owner = Owner("Jordan", available_minutes=90)
    dog, cat = Pet("Biscuit", "dog"), Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    # Deliberately add later tasks before earlier ones.
    cat.add_task(Task("Playtime", 15, "medium", datetime.combine(today, time(17))))
    weekly = Task("Grooming", 20, "medium", datetime.combine(today, time(10)), "weekly")
    dog.add_task(weekly)
    daily = Task("Morning walk", 30, "high", datetime.combine(today, time(8)), "daily")
    dog.add_task(daily)
    cat.add_task(Task("Breakfast", 10, "high", datetime.combine(today, time(8, 15))))
    scheduler = Scheduler(owner)
    pet_by_task = {id(task): pet for pet, task in scheduler.filter_tasks()}
    plan = scheduler.sort_by_time(scheduler.generate_daily_plan(today))
    print_tasks("Today's Schedule", [(pet_by_task[id(task)], task) for task in plan], scheduler)
    print("Conflicts across pets")
    for first, second in scheduler.detect_conflicts():
        print(f"WARNING: {pet_by_task[id(first)].name}: {first.name} ({first.scheduled_time:%Y-%m-%d %H:%M}) overlaps {pet_by_task[id(second)].name}: {second.name} ({second.scheduled_time:%Y-%m-%d %H:%M})")
    dog.complete_task(daily, today)
    dog.complete_task(weekly, today)
    dog.complete_task(daily, today)  # Repeated completion creates no duplicate.
    print_tasks("Biscuit's tasks (pet filter)", scheduler.filter_tasks(pet_name="Biscuit"), scheduler)
    print_tasks("Completed tasks (status filter)", scheduler.filter_tasks(completed=True), scheduler)
    print_tasks("Biscuit's next occurrences (both filters)", scheduler.filter_tasks("Biscuit", False), scheduler)


if __name__ == "__main__":
    main()
