import streamlit as st
from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Frequency, Priority

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Plan the day's care for all of your pets in one place. Add pets and tasks below and
PawPal+ builds a **time-ordered schedule**, flags **timing conflicts**, and lets you
**filter** by pet or status — all powered by the `Scheduler` logic layer.
"""
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

st.divider()

# Create the Owner once and keep it in the session "vault" so it (and all its
# pets and tasks) survives Streamlit's reruns instead of being rebuilt each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.markdown("### Add a Pet")
col_name, col_species = st.columns(2)
with col_name:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    if not pet_name.strip():
        st.warning("Give the pet a name first.")
    elif any(p.name == pet_name for p in owner.get_pets()):
        st.warning(f"{owner.name} already has a pet named {pet_name}.")
    else:
        owner.add_pet(Pet(pet_name, species))
        st.success(f"Added {pet_name} the {species}.")

pets = owner.get_pets()
if pets:
    st.write("Current pets:")
    for pet in pets:
        st.write(f"• {pet}")
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Schedule a Task")
if not pets:
    st.caption("Add a pet before scheduling tasks.")
else:
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        pet_choice = st.selectbox("For pet", [p.name for p in pets])
    with col2:
        task_title = st.text_input("Task", value="Morning walk")
    with col3:
        task_time = st.time_input("Time", value=time(8, 0))
    with col4:
        duration = st.number_input(
            "Duration (min)", min_value=1, max_value=240, value=20
        )
    with col5:
        priority = st.selectbox(
            "Priority", [str(p) for p in Priority], index=1
        )
    with col6:
        freq = st.selectbox("Frequency", [f.value for f in Frequency], index=1)

    if st.button("Add task"):
        pet = next(p for p in pets if p.name == pet_choice)
        pet.add_task(
            Task(
                task_title,
                task_time,
                Frequency(freq),
                duration_minutes=int(duration),
                priority=Priority[priority.upper()],
            )
        )
        st.success(
            f"Added '{task_title}' ({int(duration)} min, {priority} priority) "
            f"for {pet.name}."
        )

st.divider()

# One Scheduler drives every view below; it reads tasks through the Owner's
# public accessors, so the UI never touches Pet internals directly.
scheduler = Scheduler(owner)


def strip_icon(msg: str) -> str:
    """Drop the leading ⚠️ from a Scheduler warning string so it isn't doubled
    up next to st.warning/st.info's own built-in icon."""
    return msg.removeprefix("⚠️").strip()


def task_rows(pairs):
    """Turn (pet_name, task) pairs into aligned dict rows for st.table."""
    return [
        {
            "Time": f"{task.time.strftime('%H:%M')}–{task.end_time().strftime('%H:%M')}",
            "Pet": pet_name,
            "Task": task.description,
            "Min": task.duration_minutes,
            "Priority": str(task.priority),
            "Frequency": str(task.frequency),
            "Status": "✅ Done" if task.completed else "⬜ Pending",
        }
        for pet_name, task in pairs
    ]


st.subheader("📋 Your Day's Plan")

if not scheduler.all_tasks():
    st.info("Nothing planned yet — add a pet and some tasks above to see the schedule.")
else:
    # Quick action first: completing a task here (before the views below are
    # built) means the schedule, totals, and conflict checks all reflect it
    # immediately in this same run.
    schedulable = scheduler.daily_schedule()
    if schedulable:
        with st.expander("✅ Mark a task complete"):
            options = {
                f"{task.time.strftime('%H:%M')} — {task.description} ({pet.name})": task
                for pet, task in schedulable
            }
            done_label = st.selectbox("Which task did you finish?", list(options))
            if st.button("Mark done"):
                finished = options[done_label]
                follow_up = scheduler.mark_task_complete(finished)
                if follow_up is not None:
                    st.success(
                        f"'{finished.description}' done — its next occurrence is "
                        f"auto-scheduled for {follow_up.due_date.strftime('%b %d')}."
                    )
                else:
                    st.success(f"'{finished.description}' done. (One-off — it won't repeat.)")

    # Conflicts come first: they're the one thing a pet owner can't resolve just
    # by working down the list, because two tasks want them at the same instant.
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.warning(
            f"**{len(conflicts)} timing conflict"
            f"{'s' if len(conflicts) > 1 else ''} found.** Two tasks need you at "
            "the same moment — you can't be in two places at once, so consider "
            "moving one earlier or later."
        )
        for conflict in conflicts:
            st.warning(strip_icon(conflict))
    else:
        st.success("No timing conflicts — every task has its own slot. 🎉")

    # Preference nudges are softer than conflicts (the plan still works), so
    # they're shown as informational notes rather than warnings.
    for note in scheduler.preference_warnings():
        st.info(strip_icon(note))

    st.markdown("#### Sorted schedule")
    # daily_schedule() is already time-ordered with priority breaking ties, so
    # this table shows the Scheduler's ordering — the UI adds no sorting of its own.
    plan = scheduler.daily_schedule()
    if plan:
        st.table(task_rows([(pet.name, task) for pet, task in plan]))
        total = sum(task.duration_minutes for _, task in plan)
        next_up = plan[0][1]
        st.caption(
            f"{len(plan)} task(s) pending · {total} min total · "
            f"next up: **{next_up.description}** at {next_up.time.strftime('%H:%M')}"
        )
    else:
        st.success("All caught up — nothing pending for today. 🎉")

    with st.expander("Terminal view"):
        # The Scheduler's own aligned-column renderer, kept for a compact text view.
        st.code(scheduler.render_schedule(), language=None)

    st.divider()
    st.subheader("🔎 Browse tasks")

    # Filtering is delegated straight to Scheduler.filter_tasks(); the selectboxes
    # just translate the UI choices into its (pet_name, completed) arguments.
    col_pet, col_status = st.columns(2)
    with col_pet:
        pet_filter = st.selectbox("Pet", ["All pets"] + [p.name for p in pets])
    with col_status:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])

    pet_arg = None if pet_filter == "All pets" else pet_filter
    completed_arg = {"All": None, "Pending": False, "Completed": True}[status_filter]

    filtered = scheduler.filter_tasks(completed=completed_arg, pet_name=pet_arg)
    if filtered:
        # Map each task back to its pet for display, then show in time order to
        # match the Scheduler's sort_by_time() ordering.
        pet_of = {id(task): pet.name for pet, task in owner.iter_pet_tasks()}
        ordered = sorted(filtered, key=lambda t: t.time)
        st.table(task_rows([(pet_of.get(id(t), "—"), t) for t in ordered]))
        st.caption(f"{len(filtered)} task(s) match.")
    else:
        st.info("No tasks match those filters.")
