import streamlit as st
import pandas as pd
import os
from datetime import datetime
from workouts import Workout, Exercise
from streamlit_autorefresh import st_autorefresh
import matplotlib.pyplot as plt

# Constants
col = 10
row = 3
csv_file = 'workout_log.csv'

# Create workout instances
workout1 = Workout("RP At Home Day 1")
workout1.add_exercise("push_up", 4, "Myo")
workout1.add_exercise("dumbell_upright_row", 4, "Myo")
workout1.add_superset("dumbell_one-arm_row", "goblet_squats", 4)
workout1.add_superset("alternating_curls", "stiff-legged_deadlifts", 4)
workout1.add_superset("crunches_with_top_holds", "sumo_deadlifts", 4)

workout2 = Workout("RP At Home Day 2")
workout2.add_exercise("curls", 4, "straight")
workout2.add_exercise("push_up", 4, "straight")

# List of workouts
workouts = [workout1, workout2]

# Get workout names
workout_names = [workout.workout_name for workout in workouts]

# Function to read the current workout number from the CSV
def read_current_workout_num():
    if os.path.isfile(csv_file):
        try:
            df = pd.read_csv(csv_file)
            if not df.empty:
                return df['WorkoutNum'].max()
        except pd.errors.ParserError as e:
            st.error(f"Error reading CSV file: {e}")
    return 1

# Initialize session state variables if they don't exist
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
    st.session_state['selected_workout_name'] = workout_names[0]

# Function to log data to CSV
def log_to_csv(date_time, workout_num, workout_name, exercise_name, weight, set_num, rep):
    log_entry = pd.DataFrame([[date_time, workout_num, workout_name, exercise_name, weight, set_num, rep]], 
                             columns=['DateTime', 'WorkoutNum', 'WorkoutName', 'ExerciseName', 'Weight', 'SetNum', 'Rep'])
    if not os.path.isfile(csv_file):
        log_entry.to_csv(csv_file, index=False)
    else:
        log_entry.to_csv(csv_file, mode='a', header=False, index=False)

# Function to remove the last entry from the CSV
def undo_last_entry():
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        if not df.empty:
            df = df[:-1]  # Remove the last row
            df.to_csv(csv_file, index=False)

# Function to clear the state of the app
def clear_state():
    st.session_state['set_num'] = 0
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
page = st.sidebar.radio("Go to", ["Workout", "History"])

if page == "Workout":
    # Display the current date and time at the top of the app
    current_time = datetime.now().strftime("%A - %b %d, %I:%M %p")
    st.title(f"{current_time}")

    # Display the current workout number
    st.title(f"Workout Number: {st.session_state['workout_num']}")

    # Add "New Workout" button above workout selection
    if st.button("New Workout"):
        new_workout()

    # Select a workout
    selected_workout_name = st.selectbox("Select a workout", workout_names, index=workout_names.index(st.session_state['selected_workout_name']))
    st.session_state['selected_workout_name'] = selected_workout_name

    # Find the selected workout
    selected_workout = next(workout for workout in workouts if workout.workout_name == selected_workout_name)
    st.session_state['selected_workout'] = selected_workout

    # Display exercises of the selected workout in a more compact format
    st.write("Exercises:")
    exercise_details = selected_workout.get_exercise_details()

    # Create a table with two columns
    table_html = "<table style='width:100%'>"
    for i, exercise_detail in enumerate(exercise_details):
        if exercise_detail['set_type'] == 'superset':
            table_html += "<tr>"
            for j, exercise_name in enumerate(exercise_detail['name']):
                if i == st.session_state['current_exercise_index'] and j == st.session_state['superset_index']:
                    table_html += f"<td style='color: lightblue;'>{exercise_name} - {exercise_detail['sets']} sets ({exercise_detail['set_type']})</td>"
                else:
                    table_html += f"<td>{exercise_name} - {exercise_detail['sets']} sets ({exercise_detail['set_type']})</td>"
            table_html += "</tr>"
        else:
            table_html += "<tr>"
            if i == st.session_state['current_exercise_index']:
                table_html += f"<td style='color: lightblue;'>{exercise_detail['name']} - {exercise_detail['sets']} sets ({exercise_detail['set_type']})</td><td></td>"
            else:
                table_html += f"<td>{exercise_detail['name']} - {exercise_detail['sets']} sets ({exercise_detail['set_type']})</td><td></td>"
            table_html += "</tr>"
    table_html += "</table>"

    # Display the table
    st.markdown(table_html, unsafe_allow_html=True)

    # Add "Next Exercise" button
    if st.button("Next Exercise"):
        if st.session_state['current_exercise_index'] < len(exercise_details) - 1:
            st.session_state['current_exercise_index'] += 1
            st.session_state['set_num'] = 0  # Reset set_num
        else:
            st.write("All exercises completed!")
        st.rerun()

    # Add a number input for weight in a compact format
    def update_weight():
        st.session_state['weight'] = st.session_state['weight_input']

    #st.write("Weight:")
    weight_col = st.columns([1, 3])
    with weight_col[0]:
        st.number_input('Weight', value=st.session_state['weight'], step=5, key='weight_input', on_change=update_weight)

    # Create 3 rows of 10 columns each for rep buttons
    st.write("Click the buttons to log your reps")
    row, col = 3, 10
    for r in range(row):
        col_list = st.columns(col)
        for i, buttons in enumerate(col_list):
            button_number = r * col + i + 1
            if buttons.button(f"{button_number}", use_container_width=True):
                st.session_state['rep'] = button_number
                st.session_state['set_num'] += 1  # Increment set_num
                # Log the current date, time, set_num, rep, workout_num, weight, and exercise_name to CSV
                current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO 8601 format with seconds
                current_exercise = exercise_details[st.session_state['current_exercise_index']]
                workout_name = st.session_state['selected_workout'].workout_name
                if current_exercise['set_type'] == 'superset':
                    exercise_name = current_exercise['name'][st.session_state['superset_index']]
                    log_to_csv(current_time, st.session_state['workout_num'], workout_name, exercise_name, st.session_state['weight'], st.session_state['set_num'], st.session_state['rep'])
                    st.session_state['set_rep_list'].append({'Set': st.session_state['set_num'], 'Rep': st.session_state['rep']})
                    st.session_state['log_entries'].append({'Exercise': exercise_name, 'Set': st.session_state['set_num'], 'Rep': st.session_state['rep']})
                    st.session_state['superset_index'] += 1
                    if st.session_state['superset_index'] >= len(current_exercise['name']):
                        st.session_state['superset_index'] = 0
                else:
                    exercise_name = current_exercise['name']
                    log_to_csv(current_time, st.session_state['workout_num'], workout_name, exercise_name, st.session_state['weight'], st.session_state['set_num'], st.session_state['rep'])
                    st.session_state['set_rep_list'].append({'Set': st.session_state['set_num'], 'Rep': st.session_state['rep']})
                    st.session_state['log_entries'].append({'Exercise': exercise_name, 'Set': st.session_state['set_num'], 'Rep': st.session_state['rep']})
                st.rerun()

    # Add an "Undo" button
    if st.button("Undo"):
        if st.session_state['set_num'] > 1:
            st.session_state['set_num'] -= 1  # Decrement set_num
            st.session_state['rep'] = None  # Reset rep
            undo_last_entry()  # Remove the last entry from the CSV
            if st.session_state['log_entries']:
                st.session_state['log_entries'].pop()  # Remove the last entry from the log

    # Display the log table
    st.write("Workout Log:")
    log_df = pd.DataFrame(st.session_state['log_entries'])
    st.table(log_df)

elif page == "History":
    st.title("Workout History")

    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
        if not df.empty:
            # Calculate total volume for each exercise
            df['Volume'] = df['SetNum'] * df['Rep'] * df['Weight']
            exercise_names = df['ExerciseName'].unique()

            for exercise in exercise_names:
                exercise_df = df[df['ExerciseName'] == exercise]
                volume_by_workout = exercise_df.groupby('WorkoutNum')['Volume'].sum().reset_index()

                # Filter to include only the last 5 times the exercise was performed
                volume_by_workout = volume_by_workout.nlargest(5, 'WorkoutNum').sort_values('WorkoutNum')

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