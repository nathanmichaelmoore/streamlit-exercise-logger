class Exercise:
    def __init__(self, name, muscle_group=None, video_location=None):
        # Initialize an Exercise object with name, muscle group, and video location
        self.name = name
        self.muscle_group = muscle_group
        self.video_location = video_location

class Workout:
    # Predefined exercises with their details
    predefined_exercises = {
        "curls": Exercise("Curls", "Biceps", "./videos/biceps/curls.mp4"),
        "push_up": Exercise("Push Up", "Chest", "./videos/chest/push_up.mp4"),
        "dumbell_upright_row": Exercise("Dumbell Upright Row", "Side/Rear Delts", "./videos/chest/push_up.mp4"),
        "dumbell_one-arm_row": Exercise("Dumbell One-Arm Row", "Back", "./videos/chest/push_up.mp4"),
        "alternating_curls": Exercise("Alternating Curls", "Biceps", "./videos/chest/push_up.mp4"),
        "stiff-legged_deadlifts": Exercise("Stiff-Legged Deadlifts", "Hamstrings", "./videos/chest/push_up.mp4"),
        "crunches_with_top_holds": Exercise("Crunches with Top Holds", "Abs", "./videos/chest/push_up.mp4"),
        "sumo_deadlifts": Exercise("Sumo Deadlifts", "Glutes", "./videos/chest/push_up.mp4"),
        "chair_shoulder_presses": Exercise("Chair Shoulder Presses", "Triceps", "./videos/chest/push_up.mp4"),
        "goblet_squats": Exercise("Goblet Squats", "Quads", "./videos/chest/push_up.mp4"),
        # Add more predefined exercises here
    }
    
    # Valid set types for exercises
    SET_TYPES = ["straight", "superset", "circuit", "drop set", "down", "giant", "myo", "myo match"]

    def __init__(self, workout_name):
        # Initialize a Workout object with a name and an empty list of exercises
        self.workout_name = workout_name
        self.exercises = []

    def add_exercise(self, name, sets, set_type, muscle_group=None, video_location=None):
        # Validate the set type
        if set_type.lower() not in Workout.SET_TYPES:
            raise ValueError(f"Invalid set type: {set_type}. Valid set types are: {Workout.SET_TYPES}")
        # Check if the exercise is predefined, otherwise create a new Exercise object
        if name.lower() in Workout.predefined_exercises:
            exercise = Workout.predefined_exercises[name.lower()]
        else:
            exercise = Exercise(name, muscle_group, video_location)
        
        # Add the exercise to the workout
        self.exercises.append({
            "exercise": exercise,
            "sets": sets,
            "set_type": set_type
        })

    def add_superset(self, name1, name2, sets, muscle_group1=None, muscle_group2=None, video_location1=None, video_location2=None):
        # Check if the first exercise is predefined, otherwise create a new Exercise object
        if name1.lower() in Workout.predefined_exercises:
            exercise1 = Workout.predefined_exercises[name1.lower()]
        else:
            exercise1 = Exercise(name1, muscle_group1, video_location1)
        
        # Check if the second exercise is predefined, otherwise create a new Exercise object
        if name2.lower() in Workout.predefined_exercises:
            exercise2 = Workout.predefined_exercises[name2.lower()]
        else:
            exercise2 = Exercise(name2, muscle_group2, video_location2)
        
        # Add the superset to the workout
        self.exercises.append({
            "exercise": (exercise1, exercise2),
            "sets": sets,
            "set_type": "superset"
        })

    def get_exercise_names(self):
        # Get the names of all exercises in the workout
        names = []
        for exercise in self.exercises:
            if isinstance(exercise["exercise"], tuple):
                names.append(exercise["exercise"][0].name)
                names.append(exercise["exercise"][1].name)
            else:
                names.append(exercise["exercise"].name)
        return names

    def get_exercise_details(self):
        # Get the details of all exercises in the workout
        details = []
        for item in self.exercises:
            if item["set_type"] == "superset":
                exercise1, exercise2 = item["exercise"]
                details.append({
                    "name": (exercise1.name, exercise2.name),
                    "muscle_group": (exercise1.muscle_group, exercise2.muscle_group),
                    "sets": item["sets"],
                    "set_type": item["set_type"],
                    "video_location": (exercise1.video_location, exercise2.video_location)
                })
            else:
                exercise = item["exercise"]
                details.append({
                    "name": exercise.name,
                    "muscle_group": exercise.muscle_group,
                    "sets": item["sets"],
                    "set_type": item["set_type"],
                    "video_location": exercise.video_location
                })
        return details



# Example usage:
# Create a new workout instance
workout1 = Workout("RP At Home Day 1")

# Add exercises to the workout
workout1.add_exercise("push_up", 4, "straight")  # Changed from "regular" to "straight"
workout1.add_superset("chair_shoulder_presses", "deadlift", 4)
workout1.add_exercise("dumbell_upright_row", 4, "straight")
workout1.add_superset("one-arm_rows", "goblet_squats", 4)
workout1.add_superset("alternating_curls", "stiff-legged_deadlifts", 4)
workout1.add_superset("crunches_with_top_holds", "sumo_deadlifts", 4)

# Get and print the names of the exercises
exercise_names = workout1.workout_name
print(exercise_names)

# Get and print the details of all exercises
exercise_details = workout1.get_exercise_names()
print(exercise_details)

