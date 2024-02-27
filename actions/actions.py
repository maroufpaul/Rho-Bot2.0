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
s
UNIFIED_INDEX_PATH = Path(__file__).parent.parent / "data/processed_unified_index.json"


def load_unified_index():
    with open(UNIFIED_INDEX_PATH, 'r') as file:
        return json.load(file)

UNIFIED_INDEX = load_unified_index()

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

class ActionRetrieveInformation(Action):
    def name(self) -> Text:
        return "action_retrieve_information"

    def process_query(self, query: str):
        """
        Use Spacy to process the query and extract relevant entities like subjects, courses, and specializations.
        """
        doc = nlp(query)
        # Example: Extract subjects and named entities;  might need to customize this part
        subjects = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
        entities = [ent.text.lower() for ent in doc.ents]
        return subjects, entities

    def match_information(self, subjects, entities, department_data):
        """
        Match extracted subjects and entities against the unified index to find relevant information.
        """
        found_info = []
        # Iterate through department data to find matches; this is simplified and might need adjustments
        for department, data in department_data.items():
            for keyword in subjects + entities:
                if keyword in data.get("keywords", []):
                    found_info.append(f"Information related to '{keyword}' found in the {department} department.")
                    # Extend this with more specific matching logic as needed
        return found_info

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text').lower()
        subjects, entities = self.process_query(user_message)
        
        found_info = self.match_information(subjects, entities, UNIFIED_INDEX)

        if found_info:
            dispatcher.utter_message(text=" ".join(found_info))
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find relevant information for your query.")
        return []




def lod_data(department):
    file_path = Path(__file__).parent / f"data/{department}_department_data.json"
    if file_path.exists():
        with open(file_path) as json_file:
            return json.load(json_file)
    else:
        return None

class ActionFacultySpecialization(Action):
    def name(self) -> Text:
        return "action_faculty_specialization"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot('department')
        specialization = tracker.get_slot('specialization')

        department_data = load_data(department)
        if department_data is None:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        found = False
        for faculty in department_data.get("faculty", []):
            if specialization.lower() in faculty["specialization"].lower():
                dispatcher.utter_message(text=f"{faculty['name']} specializes in {specialization}.")
                found = True
                break

        if not found:
            dispatcher.utter_message(text="I couldn't find a faculty member with that specialization.")
        
        return []


class ActionRetrieveDepartmentChair(Action):
    def name(self) -> Text:
        return "action_retrieve_department_chair"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        department = tracker.get_slot("department")
        data_path = Path(__file__).parent / f"data/{department}_department_data.json"

        if not department:
            dispatcher.utter_message(text="Please specify a department.")
            return []

        try:
            with data_path.open() as json_file:
                department_data = json.load(json_file)
            chair_info = department_data.get("chair", "I don't know who it is.")
            dispatcher.utter_message(text=f"The department chair for {department} is {chair_info}.")
        except FileNotFoundError:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")

        return []

class ActionProvideCourseDetails(Action):
    def name(self) -> Text:
        return "action_provide_course_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        course = tracker.get_slot("course")
        department = tracker.get_slot("department")  # Assuming course details also depend on the department
        data_path = Path(__file__).parent / f"data/{department}_department_data.json"

        if not department or not course:
            dispatcher.utter_message(text="Please specify both a department and course.")
            return []

        try:
            with data_path.open() as json_file:
                department_data = json.load(json_file)

            for course_detail in department_data.get("courses", []):
                if course.lower() == course_detail["code"].lower():
                    dispatcher.utter_message(text=f"Course: {course_detail['name']}, Description: {course_detail['description']}")
                    return []
            dispatcher.utter_message(text=f"No details found for {course} in the {department} department.")
        except FileNotFoundError:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")

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
