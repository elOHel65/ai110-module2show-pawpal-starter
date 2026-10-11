from datetime import datetime, time
from zoneinfo import ZoneInfo

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Save your pets and care tasks, then build a daily plan
using your available time.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

Add tasks for each pet and generate a plan for your chosen day.
"""
    )

with st.expander("What PawPal+ does", expanded=True):
    st.markdown(
        """
Use PawPal+ to:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Check selected tasks for overlapping times
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)
owner = st.session_state.owner

today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
owner_name = st.text_input("Owner name", value=owner.name)
available_minutes = st.number_input(
    "Available minutes per day", min_value=0, value=owner.available_minutes, step=5
)
owner.name = owner_name.strip()
owner.available_minutes = int(available_minutes)
if not owner.name:
    st.error("Enter an owner name before adding pets, tasks, or generating a plan.")
st.caption(
    "Pets and tasks stay available between interactions in this browser session. "
    "This is not permanent storage; a new session or server restart can lose the data."
)

with st.form("add_pet"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    if not owner.name:
        st.error("Enter an owner name first.")
    elif not pet_name.strip():
        st.error("Enter a pet name.")
    else:
        owner.add_pet(Pet(name=pet_name.strip(), species=species))
        st.success(f"Added {pet_name.strip()}.")

st.markdown("### Tasks")
st.caption("Choose a saved pet and add a care task.")
with st.form("add_task"):
    pet_index = st.selectbox(
        "Pet", options=list(range(len(owner.pets))),
        format_func=lambda index: f"{owner.pets[index].name} ({owner.pets[index].species}) — Pet {index + 1}",
        index=None, placeholder="Select a pet",
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    recurrence = st.selectbox("Recurrence", ["None", "daily", "weekly"])
    scheduled = st.checkbox("Set a scheduled time", value=True)
    task_date = st.date_input("Task date", value=today)
    task_time = st.time_input("Task time", value=time(8))
    add_task = st.form_submit_button("Add Task")

if add_task:
    if not owner.name:
        st.error("Enter an owner name first.")
    elif pet_index is None or not 0 <= pet_index < len(owner.pets):
        st.error("Add and select a pet before adding a task.")
    elif not task_title.strip():
        st.error("Enter a task name.")
    elif duration <= 0:
        st.error("Task duration must be positive.")
    elif recurrence != "None" and not scheduled:
        st.error("Recurring tasks require a scheduled date and time.")
    else:
        task = Task(
            name=task_title.strip(), duration_minutes=int(duration), priority=priority,
            scheduled_time=datetime.combine(task_date, task_time) if scheduled else None,
            recurrence=None if recurrence == "None" else recurrence,
        )
        owner.pets[pet_index].add_task(task)
        st.success(f"Added {task.name} for {owner.pets[pet_index].name}.")

st.markdown("### Complete a task")
completion_date = st.date_input("Completion date", value=today)
st.caption("Recurring tasks keep their history and add the next occurrence on the same cadence after completion.")
for pet_index, pet in enumerate(owner.pets):
    for task_index, task in enumerate(list(pet.tasks)):
        if not task.completed:
            due = task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled"
            if st.button(
                f"Complete {pet.name}: {task.name} ({due})",
                key=f"complete_{pet_index}_{task_index}",
            ):
                try:
                    pet.complete_task(task, completion_date)
                except ValueError as error:
                    st.error(str(error))
                else:
                    st.rerun()

st.markdown("### Saved pets and tasks")
if owner.pets:
    for pet in owner.pets:
        st.write(f"**{pet.name}** ({pet.species})")
        if pet.tasks:
            st.table([
                {
                    "Task": task.name,
                    "Duration (minutes)": task.duration_minutes,
                    "Priority": task.priority,
                    "Scheduled": task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled",
                    "Completed": task.completed,
                    "Recurrence": task.recurrence or "None",
                }
                for task in pet.tasks
            ])
        else:
            st.info("No tasks saved for this pet yet.")
else:
    st.info("No pets saved yet. Add a pet above.")

scheduler = Scheduler(owner)
pet_names = {id(task): pet.name for pet, task in scheduler.filter_tasks()}
for first, second in scheduler.detect_conflicts():
    st.warning(
        f"Overlapping tasks: {first.name} ({pet_names[id(first)]}, {first.scheduled_time:%Y-%m-%d %H:%M}) "
        f"and {second.name} ({pet_names[id(second)]}, {second.scheduled_time:%Y-%m-%d %H:%M})."
    )

st.divider()
st.subheader("Build Schedule")
st.caption("Select tasks by priority and time within your daily time budget.")
plan_date = st.date_input("Plan date", value=today)

if st.button("Generate Plan"):
    if not owner.name:
        st.error("Enter an owner name first.")
    elif not owner.pets:
        st.error("Add a pet and its tasks before generating a plan.")
    elif not owner.get_all_tasks():
        st.error("Add a task before generating a plan.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_daily_plan(plan_date)
        plan = scheduler.sort_by_time(plan)
        pet_names = {id(task): pet.name for pet in owner.pets for task in pet.tasks}
        st.write(f"**Schedule for {plan_date:%Y-%m-%d}**")
        if plan:
            st.table([
                {
                    "Time": task.scheduled_time.strftime("%Y-%m-%d %H:%M") if task.scheduled_time else "Unscheduled",
                    "Pet": pet_names[id(task)],
                    "Task": task.name,
                    "Duration (minutes)": task.duration_minutes,
                    "Priority": task.priority,
                }
                for task in plan
            ])
            st.caption(f"Selected {sum(task.duration_minutes for task in plan)} of {owner.available_minutes} available minutes.")
        else:
            st.info("No unfinished tasks fit this date and time budget.")
