import streamlit as st
from datetime import time

from pawpal_system import Owner, Pet, Task, Scheduler, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
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
    col1, col2, col3, col4, col5 = st.columns(5)
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
        freq = st.selectbox("Frequency", [f.value for f in Frequency], index=1)

    if st.button("Add task"):
        pet = next(p for p in pets if p.name == pet_choice)
        pet.add_task(
            Task(task_title, task_time, Frequency(freq), duration_minutes=int(duration))
        )
        st.success(f"Added '{task_title}' ({int(duration)} min) for {pet.name}.")

# Show every task across all pets, pulled through the Owner's public accessor.
all_tasks = owner.iter_pet_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "pet": pet.name,
            "task": task.description,
            "time": task.time.strftime("%H:%M"),
            "duration": f"{task.duration_minutes} min",
            "frequency": str(task.frequency),
            "done": task.completed,
        }
        for pet, task in all_tasks
    ])

st.divider()

st.subheader("Build Schedule")
st.caption("Generates a time-ordered plan across all of your pets.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    if scheduler.pending_tasks():
        # Monospace so the aligned columns line up.
        st.code(scheduler.render_schedule(), language=None)
    else:
        st.info("Nothing to schedule yet — add a pet and some tasks first.")
