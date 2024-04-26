
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
from fuzzywuzzy import process, fuzz
from rasa_sdk.events import SlotSet
from transformers import pipeline
import spacy


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
                print("Closest Match: ",closest_match)
                return {closest_match.lower(): data[closest_match]}
            else:
                return {key.lower(): value for key, value in data.items()}
    else:
        return None
    
def load_faculty_data():
    file_path = Path(__file__).parent.parent / "data/Faculty_Info.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            return data
    else:
        return None

class ActionRetrieveInformation(Action):
    def name(self) -> Text:
        return "action_retrieve_information"

    def process_query(self, query: str):
        # List of department names
        department_names = ['Africana_Studies', 'Art_and_Art_History', 'Asian_Studies', 'Biochemistry_and_molecular_Biology', 'Biology', 'Business', 'Chemistry', 'Chinese_Studies', 'Computer_Science', 'Economics', 'Educational_Studies', 'Enviromental_Science', 'Enviromental_Studies', 'French', 'Gender_and_Sexuality_Studies', 'German_Studies', 'History', 'Jewish,_Islamic,_and_Middle_Eastern_Studies_Program', 'Latin_American_and_Latinx_Studies', 'Mathematics_and_Statistics', 'Media_Studies', 'Music', 'Neuroscience', 'Philosophy', 'Physics', 'Politics_and_Law', 'Psychology', 'Religious_Studies', 'Russian', 'Spanish', 'Urban_Studies_Program']

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
        specialization = tracker.get_slot('specialization')

        if specialization is None:
            dispatcher.utter_message(text="Please provide a specialization.")
            return []

        faculty_data = load_faculty_data()

        if faculty_data is None:
            dispatcher.utter_message(text="Sorry, I couldn't find information about the faculty members.")
            return []

        matching_faculty = []
        for faculty in faculty_data:
            if "specialization" in faculty:
                faculty_specializations = [s.strip().lower() for s in faculty["specialization"].split(",")]
                closest_match, score = process.extractOne(specialization.lower(), faculty_specializations, scorer=fuzz.token_sort_ratio)
                if score >= 60:
                    department_name = faculty.get("departmentName", "Unknown Department")
                    matching_faculty.append((faculty['name'], closest_match, department_name, score))

        if matching_faculty:
            dispatcher.utter_message(text=f"Here are the professors who specialize in {specialization}:")
            for i, (name, match, department, score) in enumerate(sorted(matching_faculty, key=lambda x: x[3], reverse=True)[:3], start=1):
                dispatcher.utter_message(text=f"{i}. {name} specializes in {match} and is in the {department} department. (Match score: {score}%)")
        else:
            dispatcher.utter_message(text="I couldn't find a faculty member with that specialization.")

        return []
        
class ActionRetrieveDepartmentChair(Action):
    def name(self) -> Text:
        return "action_retrieve_department_chair"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")
        department_info = UNIFIED_INDEX.get(department.lower(), {})
        if department_info:
            chair_info = department_info.get("chair", "I don't know who it is.")
            dispatcher.utter_message(text=f"The department chair for {department} is {chair_info}.")
            return []
        dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
        return []

class ActionProvideCourseDetails(Action):
    def name(self) -> Text:
        return "action_provide_course_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        course = tracker.get_slot("course")
        department = tracker.get_slot("department")

        if not course:
            dispatcher.utter_message(text="Please specify a course.")
            return []

        department_info = UNIFIED_INDEX.get(department.lower(), {})
        if not department_info:
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
    
class ActionProvideMinorRequirements(Action):
    def name(self) -> Text:
        return "action_provide_minor_requirements"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) about the {department} department.")
            return []
        
        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            minorReq = department_info.get("minorRequirements", [])
            if minorReq :
                for minor in minorReq :
                    response = f"Minor Requirements for {department.replace('_', ' ')}:\n"
                    total_credits = minor.get("totalCredits", "")
                    response += f"Total Credits: {total_credits}\n"
                    courses = minor.get('courses', [])
                    if courses:
                        response += "\nCourses:"
                        response += "\n".join(f"- {course}" for course in courses)
                        response += "\n"
                    else:
                        response += "\nNo specific courses listed."
                    dispatcher.utter_message(text=response)
                return []
            else:
                dispatcher.utter_message(text=f"Sorry, {department} does not offer a minor")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) for the {department} department.")

        return []
  
class ActionProvideHonorProgramDetails(Action):
    def name(self) -> Text:
        return "action_provide_honor_program_details"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) about the {department} department.")
            return []
        
        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            honors = department_info.get("honorsProgram", [])
            if honors:
                for honor in honors :
                    response = f"Honors Requirements for {department.replace('_', ' ')}:\n"
                    reqs = honor.get('requirements', [])
                    if reqs:
                        response += "\nRequirements:"
                        response += "\n".join(f"- {req}" for req in reqs)
                        response += "\n"
                    else:
                        response += "\nNo specific requirements listed."
                    dispatcher.utter_message(text=response)
                return []
            else:
                dispatcher.utter_message(text=f"Sorry, {department} does not offer an Honors Program")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) for the {department} department.")

        return []
    
class ActionProvideMajorRequirements(Action):
    def name(self) -> Text:
        return "action_provide_major_requirements"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")
        department_data = load_data(department)


        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) about the {department} department.")
            return []
        
        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            programs = department_info.get("programs", [])
            if programs:
                for program in programs:
                    response = f"Major Requirements for {department} - {program['programName']}:"
                    response += f"\nTotal Credits: {program['requirements'].get('totalCredits', 'N/A')}"
                    courses = program['requirements'].get('courses', [])
                    if courses:
                        response += "\nCourses:"
                        response += "\n".join(f"- {course}" for course in courses)
                        response += "\n"
                    else:
                        response += "\nNo specific courses listed."
                        response += "\n"
                    dispatcher.utter_message(text=response)
                return []
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find major requirements for any programs in the {department} department.")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information (no data) for the {department} department.")

        return []



class ActionProvideRecommendedCourses(Action):
    def name(self) -> Text:
        return "action_provide_recommended_courses"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info

        if department_info:
            recommended_courses = department_info.get("additional_info", {}).get("recommendedCourses", [])
            if recommended_courses:
                response = f"Recommended Courses for {department}:"
                response += "\n" + "\n".join(recommended_courses)
                dispatcher.utter_message(text=response)
                return []

        dispatcher.utter_message(text="Sorry, I couldn't find recommended courses for this department.")
        return []


class ActionProvideElectiveOptions(Action):
    def name(self) -> Text:
        return "action_provide_elective_options"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = department_data.get(department)  # Retrieve department info

        if department_info:
            programs = department_info.get("programs", [])
            if programs:
                response = f"Elective Options for {department}:"
                for program in programs:
                    response += f"\nProgram: {program['programName']}"
                    elective_info = program['requirements'].get('electives', {})
                    for elective_type, elective_courses in elective_info.items():
                        response += f"\n{elective_type.capitalize()} Electives: {', '.join(elective_courses)}"
                dispatcher.utter_message(text=response)
                return []

        dispatcher.utter_message(text="Sorry, I couldn't find elective options for this department.")
        return []



class ActionProvideAdditionalInformation(Action):
    def name(self) -> Text:
        return "action_provide_additional_information"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        department = tracker.get_slot("department")

        department_data = load_data(department)

        if department_data is None or not department_data:
            dispatcher.utter_message(text=f"Sorry, I couldn't find information about the {department} department.")
            return []

        department_info = list(department_data.values())[0]  # Retrieve department info
        
        if department_info:
            additional_info = department_info.get("additional_info", {})
            if additional_info:
                response = f"Additional Information for {department}:"
                for key, value in additional_info.items():
                    if isinstance(value, dict):
                        response += f"\n{key.capitalize()}:"
                        for sub_key, sub_value in value.items():
                            response += f"\n- {sub_key.capitalize()}: {sub_value}"
                    else:
                        response += f"\n{key.capitalize()}: {value}"
                dispatcher.utter_message(text=response)
                return []

        dispatcher.utter_message(text="Sorry, I couldn't find additional information for this department.")
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