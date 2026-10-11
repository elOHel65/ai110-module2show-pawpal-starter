"""Run a small PawPal+ daily scheduling demo."""

from datetime import datetime, time
from zoneinfo import ZoneInfo

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    """Print today's selected tasks chronologically with their pets."""
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
    owner = Owner("Jordan", available_minutes=60)
    dog = Pet("Biscuit", "dog")
    cat = Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task("Morning walk", 30, "high", datetime.combine(today, time(8))))
    cat.add_task(Task("Breakfast", 10, "high", datetime.combine(today, time(9))))
    cat.add_task(Task("Playtime", 15, "medium", datetime.combine(today, time(17))))
    plan = Scheduler(owner).generate_daily_plan(today)
    pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
    plan.sort(key=lambda task: (task.scheduled_time is None, task.scheduled_time))
    print("Today's Schedule")
    for task in plan:
        start = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "Unscheduled"
        print(f"{start} | {pet_names[id(task)]} | {task.name} | {task.duration_minutes} min | {task.priority}")


if __name__ == "__main__":
    main()
