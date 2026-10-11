"""Streamlit interaction checks for task editing."""
from datetime import datetime
from pathlib import Path

from streamlit.testing.v1 import AppTest

from pawpal_system import Owner, Pet, Task


def test_edit_form_updates_selected_task_and_rejects_blank_title():
    """Switching tasks loads their values; saving preserves ownership across reruns."""
    due = datetime(2026, 10, 11, 8)
    first = Task("Walk", 20, "high", due, "daily")
    second = Task("Feed", 10, "low", due, completed=True)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.session_state.owner = Owner("Jordan", 60, pets=[
        Pet("Biscuit", "dog", tasks=[first]), Pet("Mochi", "cat", tasks=[second]),
    ])
    app.run()

    def field(items, label):
        return next(item for item in items if item.label == label)

    assert not app.exception
    field(app.selectbox, "Task to edit").select(1).run()
    assert field(app.text_input, "Edited task title").value == "Feed"
    assert field(app.number_input, "Edited duration (minutes)").value == 10
    field(app.text_input, "Edited task title").set_value(" ")
    field(app.number_input, "Edited duration (minutes)").set_value(15)
    field(app.button, "Save Changes").click().run()
    assert any("Enter a task name" in error.value for error in app.error)
    assert (second.name, second.duration_minutes) == ("Feed", 10)
    field(app.text_input, "Edited task title").set_value("  Breakfast  ")
    field(app.selectbox, "Edited priority").select("medium")
    field(app.button, "Save Changes").click().run()
    assert any("Updated Breakfast for Mochi" in message.value for message in app.success)
    app.run()
    assert not app.exception
    assert app.session_state.owner.pets[1].tasks[0] is second
    assert (second.name, second.duration_minutes, second.priority) == ("Breakfast", 15, "medium")
    assert second.scheduled_time == due and second.completed and second.recurrence is None
    assert (first.name, first.duration_minutes, first.priority, first.recurrence) == ("Walk", 20, "high", "daily")
