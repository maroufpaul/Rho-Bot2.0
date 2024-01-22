# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions








# actions/actions.py
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pathlib import Path
import json

# Path to your JSON file
DATA_PATH = Path(__file__).parent.parent / "data/cs_department_data.json"

# Function to load data from JSON
def load_data(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)

# Load the data once at the start to avoid reloading it with each call
cs_data = load_data(DATA_PATH)
class ActionFacultySpecialization(Action):
    def name(self) -> Text:
        return "action_faculty_specialization"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        specialization = tracker.get_slot('specialization')
        
        # Check if the specialization slot is None or empty
        if not specialization:
            dispatcher.utter_message(text="Please specify a specialization.")
            return []

        message = "I couldn't find information on that specialization."

        # Search for the faculty with the given specialization
        for faculty_member in cs_data['faculty']:
            if specialization.lower() in faculty_member['specialization'].lower():
                message = f"{faculty_member['name']} specializes in {specialization}."
                break

        dispatcher.utter_message(text=message)
        return []




# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
