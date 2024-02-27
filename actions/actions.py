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
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import SlotSet
from transformers import pipeline
import spacy
from fuzzywuzzy import process

UNIFIED_INDEX_PATH = Path(__file__).parent.parent / "data/processed_unified_data.json"


def load_unified_index():
    with open(UNIFIED_INDEX_PATH, 'r') as file:
        return json.load(file)


UNIFIED_INDEX = load_unified_index()


def load_data(department=None):
    file_path = Path(__file__).parent.parent / "data/processed_unified_data.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            if department:
                department = department.lower()
                closest_match = process.extractOne(department, data.keys())[0]
                return {closest_match.lower(): data[closest_match]}
            else:
                return {key.lower(): value for key, value in data.items()}
    else:
        return None

class ActionRetrieveInformation(Action):
    def name(self) -> Text:
        return "action_retrieve_information"

    def process_query(self, query: str):
        # List of department names
        department_names = ["Computer_Science", "Physics"]

        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        # Use fuzzy matching to find the closest match
        closest_match, _ = process.extractOne(query_lower, department_names)
        return [closest_match]


    def match_information(self, department_name, department_data):
        found_info = []
        department_data_lower = {key.lower(): value for key, value in department_data.items()}
        if department_name.lower() in department_data_lower:
            department_info = department_data_lower[department_name.lower()]
            if "description" in department_info:
                found_info.append(department_info["description"])
            else:
                for program in department_info.get("programs", []):
                    found_info.append(program["programName"] + ": " + program["requirements"]["additionalCourses"])
                found_info.append("Minor Requirements: " + department_info["minorRequirements"]["courses"])
        return found_info

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text').lower()
        department_name = self.process_query(user_message)
        print(department_name)
        print("hello")

        if department_name:
            found_info = self.match_information(department_name[0], UNIFIED_INDEX)
            print("Found info is: ", found_info)
            if found_info:
                dispatcher.utter_message(text="\n".join(found_info))
                return []
        
        dispatcher.utter_message(text="Sorry, I couldn't find relevant information for your query.")
        return []

class ActionFacultySpecialization(Action):
    def name(self) -> Text:
        return "action_faculty_specialization"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot('department')
        specialization = tracker.get_slot('specialization')

        print(department)

        if specialization is None:
            dispatcher.utter_message(text="Please provide a specialization.")
            return []

        department_data = load_data(department)
        print(department_data)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info

        print(department_info)
       
        if department_info:
            faculty_list = department_info.get("faculty", [])
            # Fuzzy matching for specialization
            closest_match, _ = process.extractOne(specialization.lower(), [faculty["specialization"].lower() for faculty in faculty_list])
            for faculty in faculty_list:
                if closest_match in faculty["specialization"].lower():
                    dispatcher.utter_message(text=f"{faculty['name']} specializes in {faculty['specialization']}.")
                    return []
        
        dispatcher.utter_message(text="I couldn't find a faculty member with that specialization.")
        return []


class ActionRetrieveDepartmentChair(Action):
    def name(self) -> Text:
        return "action_retrieve_department_chair"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        department = tracker.get_slot("department")

        department_data = load_data(department)
        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info

        chair_info = department_info.get("chair", "I don't know who it is.")
        dispatcher.utter_message(text=f"The department chair for {department} is {chair_info}.")
        return []

class ActionProvideCourseDetails(Action):
    def name(self) -> Text:
        return "action_provide_course_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.get_slot("course")
        department = tracker.get_slot("department")

        if course is None:
            dispatcher.utter_message(text="Please specify a course.")
            return []

        department_data = load_data()
        if department_data is None:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = department_data.get(department)
        if department_info is None:
            # Find the closest matching department name
            department_options = list(department_data.keys())
            closest_match, _ = process.extractOne(department, department_options)
            department_info = department_data.get(closest_match)

            if department_info is None:
                dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
                return []

        programs = department_info.get("programs", [])
        for program in programs:
            for course_detail in program.get("requirements", {}).get("courses", []):
                if course_detail and course.lower() == course_detail.lower():
                    dispatcher.utter_message(text=f"Course: {course_detail['name']}, Description: {course_detail['description']}")
                    return []
        
        dispatcher.utter_message(text=f"No details found for {course} in the {department} department.")
        return []
    

class ActionProvideMajorRequirements(Action):
    def name(self) -> Text:
        return "action_provide_major_requirements"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            programs = department_info.get("programs", [])
            for program in programs:
                dispatcher.utter_message(text=f"Major Requirements for {program['programName']}: {program['requirements']['courses']}")
            return []

        dispatcher.utter_message(text="Sorry, I couldn't find major requirements for this department.")
        return []


class ActionProvideMinorRequirements(Action):
    def name(self) -> Text:
        return "action_provide_minor_requirements"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            minor_requirements = department_info.get("minorRequirements", {}).get("courses")
            if minor_requirements:
                dispatcher.utter_message(text=f"Minor Requirements: {minor_requirements}")
                return []

        dispatcher.utter_message(text="Sorry, I couldn't find minor requirements for this department.")
        return []


class ActionCustomClassifier(Action):
    def name(self) -> Text:
        return "action_custom_classifier"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Load the pre-trained model pipeline
        classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

        # Get the latest message text from the user
        user_message = tracker.latest_message.get('text')

        # Use the model to classify the user message
        prediction = classifier(user_message)

        # Extract the predicted label and score
        label = prediction[0]['label']
        score = prediction[0]['score']

        # Respond with the prediction
        dispatcher.utter_message(text=f"Predicted category: {label} with confidence {score:.2f}")
        return []


class ActionHandleAndAnalyzeFeedback(Action):
    def name(self) -> Text:
        return "action_handle_and_analyze_feedback"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        feedback = tracker.latest_message.get('text')
        # Log feedback
        log_feedback(feedback)
        
        # Sentiment analysis
        sentiment_pipeline = pipeline("sentiment-analysis")
        sentiment = sentiment_pipeline(feedback)[0]
        dispatcher.utter_message(text=f"Feedback received. Detected sentiment: {sentiment['label']}")
        
        return []

def log_feedback(feedback):
    # Your logging logic here
    pass


class ActionFallback(Action):
    def name(self) -> Text:
        return "action_custom_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="I'm not sure how to answer that. Can I help with something else?")
        return [UserUtteranceReverted()]




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
