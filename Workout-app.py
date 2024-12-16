import streamlit as st
import pandas as pd
import os
from datetime import datetime
from workouts import Workout, Exercise
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt
import json

# Constants
CSV_FILE = 'workout_log.csv'
WORKOUT_FILE = 'workouts.json'
EXERCISE_FILE = 'exercises.json'
col = 10
row = 3

# Function to load exercises from file
def load_exercises():
    if os.path.isfile(EXERCISE_FILE):
        with open(EXERCISE_FILE, 'r') as f:
            return json.load(f)
    return {}

# Function to save exercises to file
def save_exercises(exercises):
    with open(EXERCISE_FILE, 'w') as f:
        json.dump(exercises, f, indent=4)

# Load exercises
def initialize_exercises():
    exercises = load_exercises()
    if not exercises:
        exercises = {
            "Chest": [], "Back": [], "Shoulders": [], "Biceps": [], "Triceps": [], "Legs": [], "Abs": []
        }
        save_exercises(exercises)
    return exercises

exercises = initialize_exercises()


# Function to save workouts to a file
def save_workouts(workouts):
    with open(WORKOUT_FILE, 'w') as f:
        json.dump(workouts, f)

# Function to load workouts from a file
def load_workouts():
    if os.path.isfile(WORKOUT_FILE):
        with open(WORKOUT_FILE, 'r') as f:
            return json.load(f)
    return []

# Load existing workouts
workouts = load_workouts()
if not workouts:
    save_workouts([{"name": "", "exercises": []}])


# Function to read the current workout number from the CSV
def read_current_workout_num():
    if os.path.isfile(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                return df['WorkoutNum'].max()
        except pd.errors.ParserError as e:
            st.error(f"Error reading CSV file: {e}")
    return 1

# Initialize session state variables if they don't exist
def initialize_session_state():
    if 'set_num' not in st.session_state:
        st.session_state['set_num'] = 0
    if 'rep' not in st.session_state:
        st.session_state['rep'] = None
    if 'workout_num' not in st.session_state:
        st.session_state['workout_num'] = read_current_workout_num()
    if 'set_rep_list' not in st.session_state:
        st.session_state['set_rep_list'] = []
    if 'weight' not in st.session_state:
        st.session_state['weight'] = 20
    if 'current_exercise_index' not in st.session_state:
        st.session_state['current_exercise_index'] = 0
    if 'selected_workout' not in st.session_state:
        st.session_state['selected_workout'] = None
    if 'superset_index' not in st.session_state:
        st.session_state['superset_index'] = 0
    if 'log_entries' not in st.session_state:
        st.session_state['log_entries'] = []
    if 'selected_workout_name' not in st.session_state:
        st.session_state['selected_workout_name'] = workouts[0]['name']
    if 'new_workout_name' not in st.session_state:
        st.session_state['new_workout_name'] = ''
    if 'new_workout_exercises' not in st.session_state:
        st.session_state['new_workout_exercises'] = []
    if 'selected_workout_index' not in st.session_state:
        st.session_state['selected_workout_index'] = None

initialize_session_state()


# Function to log data to CSV
def log_to_csv(date_time, workout_num, workout_name, exercise_name, weight, set_num, rep, set_type):
    log_entry = pd.DataFrame([[date_time, workout_num, workout_name, exercise_name, weight, set_num, rep, set_type]], 
                             columns=['DateTime', 'WorkoutNum', 'WorkoutName', 'ExerciseName', 'Weight', 'SetNum', 'Rep', 'SetType'])
    if not os.path.isfile(CSV_FILE):
        log_entry.to_csv(CSV_FILE, index=False)
    else:
        log_entry.to_csv(CSV_FILE, mode='a', header=False, index=False)

# Function to remove the last entry from the CSV
def undo_last_entry():
    if os.path.isfile(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            df = df[:-1]  # Remove the last row
            df.to_csv(CSV_FILE, index=False)

# Function to clear the state of the app
def clear_state():
    st.session_state['set_num'] = [0,0]
    st.session_state['rep'] = None
    st.session_state['set_rep_list'] = []
    st.session_state['current_exercise_index'] = 0
    st.session_state['superset_index'] = 0
    st.session_state['log_entries'] = []

# Function to increment workout number and save to CSV
def new_workout():
    st.session_state['workout_num'] = read_current_workout_num() + 1
    clear_state()
    st.rerun()

# Initialize workout number when the app starts
if 'initialized' not in st.session_state:
    st.session_state['workout_num'] = read_current_workout_num()
    st.session_state['initialized'] = True

# Automatically refresh the app every minute
st_autorefresh(interval=60000, key="datarefresh")

# Sidebar for navigation
st.sidebar.title("Navigation")
if 'page' not in st.session_state:
    st.session_state['page'] = "Workout"
page = st.sidebar.radio("Go to", ["Add Exercise","Create Workout", "Workout", "History"], index=["Add Exercise","Create Workout", "Workout", "History"].index(st.session_state['page']))

if page == "Add Exercise":
    st.title("Add a New Exercise")

    # Input for exercise details
    muscle_group = st.selectbox("Select Muscle Group", list(exercises.keys()))
    exercise_name = st.text_input("Exercise Name")
    exercise_explanation = st.text_area("Exercise Explanation")

    # Button to add the exercise
    if st.button("Add Exercise"):
        if exercise_name and exercise_explanation:
            new_exercise = {
                "name": exercise_name,
                "explanation": exercise_explanation
            }
            exercises[muscle_group].append(new_exercise)
            save_exercises(exercises)
            st.success(f"Exercise '{exercise_name}' added to {muscle_group} successfully!")
        else:
            st.error("Please fill in all fields before adding the exercise.")

    # Display existing exercises for the selected muscle group
    st.subheader(f"Exercises in {muscle_group}")
    if exercises[muscle_group]:
        for i, exercise in enumerate(exercises[muscle_group]):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"- **{exercise['name']}**: {exercise['explanation']}")
            with col2:
                if st.button(f"Remove", key=f"remove_{muscle_group}_{i}"):
                    exercises[muscle_group].pop(i)
                    save_exercises(exercises)
                    st.rerun()
    else:
        st.write("No exercises available for this muscle group.")

if page == "Create Workout":
    st.session_state['page'] = "Create Workout"
    st.title("Create a New Workout")

    # Input for workout name
    st.session_state['new_workout_name'] = st.text_input("Workout Name", st.session_state['new_workout_name'])

    # Dropdown to select an exercise
    muscle_group = st.selectbox("Select Muscle Group", list(exercises.keys()))
    exercise = st.selectbox("Select Exercise", [ex['name'] for ex in exercises[muscle_group]])

    # Dropdown to select the set type
    set_type = st.selectbox("Select Set Type", ["straight", "superset", "drop set", "down", "giant", "myo", "myo match"])

    # Handle superset case
    if set_type == "superset":
        superset_exercise = st.selectbox("Select Superset Exercise", [ex['name'] for ex in exercises[muscle_group]])

    # Button to add exercise to the workout
    if st.button("Add Exercise"):
        if set_type == "superset":
            st.session_state['new_workout_exercises'].append({"exercise": exercise, "set_type": set_type, "superset_exercise": superset_exercise})
        else:
            st.session_state['new_workout_exercises'].append({"exercise": exercise, "set_type": set_type})

    # Display the current exercises in the workout with remove buttons
    st.write("Exercises in Workout:")
    for i, ex in enumerate(st.session_state['new_workout_exercises']):
        col1, col2 = st.columns([4, 1])
        with col1:
            if ex['set_type'] == "superset":
                st.write(f"{ex['exercise']} (Superset with {ex['superset_exercise']})")
            else:
                st.write(f"{ex['exercise']} ({ex['set_type']})")
        with col2:
            if st.button(f"Remove", key=f"remove_{i}"):
                st.session_state['new_workout_exercises'].pop(i)
                st.rerun()

    # Button to save the workout
    if st.button("Save Workout"):
        new_workout = {
            "name": st.session_state['new_workout_name'],
            "exercises": st.session_state['new_workout_exercises']
        }
        if st.session_state['selected_workout_index'] is not None:
            workouts[st.session_state['selected_workout_index']] = new_workout
            st.session_state['selected_workout_index'] = None
        else:
            workouts.append(new_workout)
        save_workouts(workouts)
        st.session_state['new_workout_name'] = ''
        st.session_state['new_workout_exercises'] = []
        st.success("Workout saved successfully!")
        st.rerun()

    # Display existing workouts with options to edit, copy, or delete
    st.title("Existing Workouts")
    for i, workout in enumerate(workouts):
        st.write(f"**{workout['name']}**")
        for ex in workout['exercises']:
            if ex['set_type'] == "superset":
                st.write(f"- {ex['exercise']} (Superset with {ex['superset_exercise']})")
            else:
                st.write(f"- {ex['exercise']} ({ex['set_type']})")
        if st.button(f"Edit {workout['name']}", key=f"edit_{i}"):
            st.session_state['selected_workout_index'] = i
            st.session_state['new_workout_name'] = workout['name']
            st.session_state['new_workout_exercises'] = workout['exercises']
            st.rerun()
        if st.button(f"Copy {workout['name']}", key=f"copy_{i}"):
            st.session_state['new_workout_name'] = f"Copy of {workout['name']}"
            st.session_state['new_workout_exercises'] = workout['exercises']
        if st.button(f"Delete {workout['name']}", key=f"delete_{i}"):
            workouts.pop(i)
            save_workouts(workouts)
            st.success(f"Workout {workout['name']} deleted successfully!")
            st.rerun()

if page == "Workout":
    st.session_state['page'] = "Workout"
    # Display the current date and time at the top of the app
    current_time = datetime.now().strftime("%A - %b %d, %I:%M %p")
    st.title(f"{current_time}")

    # Function to get the last logged weight for an exercise
    def get_last_logged_weight(exercise_name):
        if os.path.isfile(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if not df.empty:
                exercise_df = df[df['ExerciseName'] == exercise_name]
                if not exercise_df.empty:
                    return exercise_df.iloc[-1]['Weight']
        return st.session_state['weight']  # Default weight if no previous log

    # Define the update_weight function
    def update_weight():
        st.session_state['weight'] = st.session_state['weight_input']

    # Display the current workout number
    st.title(f"Workout Number: {st.session_state['workout_num']}")

    # Add "New Workout" button and "Select Workout" dropdown in the same row, centered vertically
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(" ")  # Add an empty line for vertical centering
        if st.button("New Workout"):
            new_workout()
    with col2:
        workout_names = [workout['name'] for workout in workouts]
        selected_workout_name = st.selectbox("Select a workout", workout_names, index=workout_names.index(st.session_state['selected_workout_name']))
        if selected_workout_name != st.session_state['selected_workout_name']:
            st.session_state['selected_workout_name'] = selected_workout_name
            st.session_state['current_exercise_index'] = 0  # Reset current exercise index
            st.session_state['superset_index'] = 0  # Reset superset index
            st.session_state['set_num'] = [0, 0]  # Reset set numbers for superset exercises

    # Find the selected workout
    selected_workout = next(workout for workout in workouts if workout['name'] == selected_workout_name)
    st.session_state['selected_workout'] = selected_workout

    # Display exercises of the selected workout in a more compact format
    #st.write("Exercises:")
    exercise_details = selected_workout['exercises']

    # Ensure current_exercise_index is within the valid range
    if st.session_state['current_exercise_index'] >= len(exercise_details):
        st.session_state['current_exercise_index'] = 0

    # Initialize set_num if it doesn't exist
    if 'set_num' not in st.session_state:
        st.session_state['set_num'] = [0, 0]

    # Create a table with two columns
    table_html = "<table style='width:100%'>"
    for i, exercise_detail in enumerate(exercise_details):
        if exercise_detail['set_type'] == 'superset':
            table_html += "<tr>"
            for j, exercise_name in enumerate([exercise_detail['exercise'], exercise_detail['superset_exercise']]):
                if i == st.session_state['current_exercise_index'] and j == st.session_state['superset_index']:
                    table_html += f"<td style='color: lightblue;'>{exercise_name} - {exercise_detail['set_type']}</td>"
                else:
                    table_html += f"<td>{exercise_name} - {exercise_detail['set_type']}</td>"
            table_html += "</tr>"
        else:
            table_html += "<tr>"
            if i == st.session_state['current_exercise_index']:
                table_html += f"<td style='color: lightblue;'>{exercise_detail['exercise']} - {exercise_detail['set_type']}</td><td></td>"
            else:
                table_html += f"<td>{exercise_detail['exercise']} - {exercise_detail['set_type']}</td><td></td>"
            table_html += "</tr>"
    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

    # Add "Next Exercise" button and weight number input in the same row, centered vertically
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(" ")  # Add an empty line for vertical centering
        st.write(" ")  # Add an empty line for vertical centering
        if st.button("Next Exercise"):
            current_exercise = exercise_details[st.session_state['current_exercise_index']]
            if current_exercise['set_type'] == 'superset':
                if st.session_state['superset_index'] == 0:
                    st.session_state['superset_index'] = 1
                else:
                    st.session_state['superset_index'] = 0
                    if st.session_state['current_exercise_index'] < len(exercise_details) - 1:
                        st.session_state['current_exercise_index'] += 1
                    else:
                        st.write("All exercises completed!")
            else:
                if st.session_state['current_exercise_index'] < len(exercise_details) - 1:
                    st.session_state['current_exercise_index'] += 1
                else:
                    st.write("All exercises completed!")
            st.session_state['set_num'] = [0, 0]  # Reset set numbers for superset exercises
            st.rerun()
    with col2:
        if st.session_state['selected_workout']['name'] != "":
            current_exercise_name = exercise_details[st.session_state['current_exercise_index']]['exercise']
            initial_weight = get_last_logged_weight(current_exercise_name)
            st.number_input('Weight', value=initial_weight, step=5, key='weight_input', on_change=update_weight)

    # Create 3 rows of 10 columns each for rep buttons
    st.write("Click the buttons to log your reps")
    row, col = 3, 10
    for r in range(row):
        col_list = st.columns(col)
        for i, buttons in enumerate(col_list):
            button_number = r * col + i + 1
            if buttons.button(f"{button_number}", use_container_width=True):
                st.session_state['rep'] = button_number
                current_exercise = exercise_details[st.session_state['current_exercise_index']]
                workout_name = st.session_state['selected_workout']['name']
                if current_exercise['set_type'] == 'superset':
                    exercise_name = current_exercise['exercise'] if st.session_state['superset_index'] == 0 else current_exercise['superset_exercise']
                    st.session_state['set_num'][st.session_state['superset_index']] += 1  # Increment set number for the current superset exercise
                    set_num = st.session_state['set_num'][st.session_state['superset_index']]
                    st.session_state['superset_index'] = (st.session_state['superset_index'] + 1) % 2  # Switch to the next superset exercise
                else:
                    exercise_name = current_exercise['exercise']
                    st.session_state['set_num'] = [st.session_state['set_num'][0] + 1, 0]  # Increment set number for non-superset exercise
                    set_num = st.session_state['set_num'][0]
                current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO 8601 format with seconds
                log_to_csv(current_time, st.session_state['workout_num'], workout_name, exercise_name, st.session_state['weight'], set_num, st.session_state['rep'], current_exercise['set_type'])
                st.session_state['set_rep_list'].append({'Set': set_num, 'Rep': st.session_state['rep']})
                st.session_state['log_entries'].append({'Exercise': exercise_name, 'Set': set_num, 'Rep': st.session_state['rep'], 'Weight':st.session_state['weight_input']})
                st.rerun()

    # Add an "Undo" button
    if st.button("Undo"):
        if st.session_state['set_num'][0] > 1 or st.session_state['set_num'][1] > 1:
            if st.session_state['superset_index'] == 0:
                st.session_state['set_num'][0] -= 1
            else:
                st.session_state['set_num'][1] -= 1
            st.session_state['set_rep_list'].pop()
            st.session_state['log_entries'].pop()
            st.rerun()

    # Display the log table
    st.write("Workout Log:")
    log_df = pd.DataFrame(st.session_state['log_entries'])
    st.table(log_df)

elif page == "History":
    st.session_state['page'] = "History"
    st.title("Workout History")

    if os.path.isfile(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if not df.empty:
            # Calculate total volume for each exercise
            df['Volume'] = df['SetNum'] * df['Rep'] * df['Weight']
            exercise_names = df['ExerciseName'].unique()

            for exercise in exercise_names:
                #st.write(exercise_names)
                exercise_df = df[df['ExerciseName'] == exercise]
                volume_by_workout = exercise_df.groupby('WorkoutNum')['Volume'].sum().reset_index()

                # Filter to include only the last 5 times the exercise was performed based on DateTime
                exercise_df = exercise_df.sort_values('DateTime', ascending=False).head(5).sort_values('DateTime')
                volume_by_workout = exercise_df.groupby('WorkoutNum')['Volume'].sum().reset_index()

                # Plot the volume over workouts
                fig, ax = plt.subplots()
                x_ticks = range(-len(volume_by_workout), 0)
                ax.plot(x_ticks, volume_by_workout['Volume'], marker='o')
                ax.set_title(f"Total Volume for {exercise}")
                ax.set_xlabel("Last 5 Workouts")
                ax.set_ylabel("Total Volume")
                ax.set_xticks(x_ticks)  # Ensure x-axis labels are integers
                st.pyplot(fig)
        else:
            st.write("No workout data available.")
    else:
        st.write("No workout data available.")