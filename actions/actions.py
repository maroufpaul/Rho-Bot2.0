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
from fuzzywuzzy import process, fuzz
import requests
from bs4 import BeautifulSoup

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

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text').lower()

        # Load department data
        department_data = load_data()

        # Process query to find the closest department match
        department_name = self.process_query(user_message, department_data)

        if department_name:
            department_info = department_data.get(department_name, {})

            if "description" in department_info:
                dispatcher.utter_message(text=department_info["description"])
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find a description for {department_name}.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find relevant information for your query.")

        return []

    def process_query(self, query: str, department_data: Dict[str, Dict]) -> str:
        # List of department names
        department_names = list(department_data.keys())

        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        # Use fuzzy matching to find the closest match
        closest_match, _ = process.extractOne(query_lower, department_names)
        return closest_match


class ActionFacultySpecialization(Action):
    def name(self) -> Text:
        return "action_faculty_specialization"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        specialization = next(tracker.get_latest_entity_values("specialization"), None)

        if not specialization:
            # Provide a list of related specializations if no specific specialization is provided
            dispatcher.utter_message(text="Please provide a specialization or choose from the following related topics: machine learning, parallel computing, Islamic law, etc.")
            return []

        faculty_data = load_faculty_data()
        print("hello")
        
        if faculty_data is None:
            dispatcher.utter_message(text="Sorry, I couldn't find information about the faculty members.")
            return []

        matching_faculty = []
        seen_names = set()  # To avoid duplicate entries
        for faculty in faculty_data:
            if "specialization" in faculty:
                faculty_specializations = [s.strip().lower() for s in faculty["specialization"].split(",")]
                for spec in faculty_specializations:
                    score = fuzz.ratio(specialization.lower(), spec)
                    if score >= 70:  # Adjust the threshold as needed
                        name = faculty['name']
                        if name not in seen_names:
                            department_name = faculty.get("departmentName", "Unknown Department")
                            matching_faculty.append((name, spec, department_name, score))
                            seen_names.add(name)

        if matching_faculty:
            # Sort matching faculty by match score in descending order
            matching_faculty = sorted(matching_faculty, key=lambda x: x[3], reverse=True)
            dispatcher.utter_message(text=f"Here are the professors who specialize in {specialization}:")
            for i, (name, match, department, score) in enumerate(matching_faculty[:3], start=1):
                dispatcher.utter_message(text=f"{i}. {name} specializes in {match} and is in the {department} department. (Match score: {score}%)")
        else:
            dispatcher.utter_message(text="I couldn't find a faculty member with that specialization.")
        
        return []


class ActionFacultyInfo(Action):
    def name(self) -> Text:
        return "action_faculty_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        person_entity = next(tracker.get_latest_entity_values("person"), None)
        faculty_data = load_faculty_data()

        if faculty_data is None:
            dispatcher.utter_message(text="Sorry, I couldn't find information about the faculty members.")
            return []

        if person_entity:
            person_entity = person_entity.lower()
            name_matches = process.extract(person_entity, [f['name'].lower() for f in faculty_data], scorer=fuzz.partial_ratio)
            name_matches = [match for match in name_matches if match[1] >=60]  # Adjust the threshold as needed

            if name_matches:
                matching_faculty_name = name_matches[0][0]
                matching_faculty = [f for f in faculty_data if f['name'].lower() == matching_faculty_name]
                faculty = matching_faculty[0]
                dispatcher.utter_message(text=f"Here's the information about {faculty['name']}:")
                for key, value in faculty.items():
                    if key != 'name':
                        dispatcher.utter_message(text=f"{key.capitalize()}: {value}")
            else:
                dispatcher.utter_message(text=f"I couldn't find any information about {person_entity}.")
        else:
            dispatcher.utter_message(text="Please provide a faculty name to get their information.")

        return []

'''
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
        return [] '''
    

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
class ActionProvideLink(Action):
    def name(self) -> str:
        return "action_provide_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        JSON_FILE_PATH = Path(__file__).parent.parent / "scraped_links_preprocess.json"

        # Load JSON data
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            links_data = json.load(file)

        entity = next(tracker.get_latest_entity_values("service"), None)
        if entity:
            entity = entity.lower()  # Normalize entity to lower case

        # Flatten the JSON structure for sub-links, handling special characters and case sensitivity
        flattened_links = {}
        for main_key, main_val in links_data.items():
            main_key_normalized = main_key.lower()  # Normalize key to lower case
            flattened_links[main_key_normalized] = main_val['url']
            for sub_key, sub_val in main_val.get('sub_links', {}).items():
                sub_key_normalized = sub_key.lower()  # Normalize sub_key to lower case
                # Ensure no key collision
                if sub_key_normalized not in flattened_links:
                    flattened_links[sub_key_normalized] = sub_val

        if entity:
            # Find the closest match with case-insensitive comparison and special character handling
            match, confidence = process.extractOne(entity, flattened_links.keys())
            if confidence > 60:  # Adjust the confidence level as needed
                matched_key = next((key for key in flattened_links if key.lower() == match), None)
                if matched_key:
                    response_text = f"{match} - URL: {flattened_links[matched_key]}"
                    dispatcher.utter_message(text=response_text)
            else:
                dispatcher.utter_message(text="I'm not sure which link you're referring to. Please be more specific.")
        else:
            dispatcher.utter_message(text="Please specify which link you're looking for.")

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

'''
class ActionProvideLink(Action):
    def name(self) -> str:
        return "action_provide_link"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        JSON_FILE_PATH = Path(__file__).parent.parent / "scraped_links_preprocess.json"

        # Load JSON data
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
            links_data = json.load(file)

        entity = next(tracker.get_latest_entity_values("service"), None)
        print("entity:", entity)

        # Flatten the JSON structure for sub-links
        flattened_links = {}
        for main_key, main_val in links_data.items():
            flattened_links[main_key] = main_val['url']
            for sub_key, sub_val in main_val.get('sub_links', {}).items():
                print(sub_key)
                flattened_links[sub_key] = sub_val

        if entity:
            # Find the closest match
            match, confidence = process.extractOne(entity, flattened_links.keys())
            print("match is: ", match)
            if confidence > 50:  # Adjust the confidence level as needed
                response_text = f"{match} - URL: {flattened_links[match]}"
                dispatcher.utter_message(text=response_text)
            else:
                dispatcher.utter_message(text="I'm not sure which link you're referring to. Please be more specific.")
        else:
            dispatcher.utter_message(text="Please specify which link you're looking for.")

        return [] '''

class ActionSetLinkContext(Action):
    def name(self) -> Text:
        return "action_set_link_context"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("context", "link_request")]
    


class ActionGetCourseInfo(Action):

    def name(self) -> Text:
        return "action_get_course_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        course_code = next(tracker.get_latest_entity_values("course_code"), None)

        if not course_code:
            dispatcher.utter_message("I'm sorry, I couldn't identify the course code you're asking about. Please provide the course code (e.g., COMP 355).")
            return []

        base_url = "https://catalog.rhodes.edu"
        split_code = course_code.split()
        if len(split_code) == 2:
            dept_code, course_number = split_code
            url = f"{base_url}/{dept_code.lower()}/{course_number.lower()}"
        else:
            url = f"{base_url}/{course_code.lower()}"
        response = requests.get(url)

        if response.status_code != 200:
            dispatcher.utter_message(f"I'm sorry, I couldn't find information for {course_code}.")
            return []

        soup = BeautifulSoup(response.content, 'html.parser')

        course_title = soup.find('h1').text.strip()
        course_description = soup.find('p').text.strip()
        prerequisites_section = soup.find('h3', string='Prerequisites')
        
        degree_requirements_section = soup.find('h3', string='Degree Requirements')

        if prerequisites_section:
            prerequisites = prerequisites_section.find_next('div').find_all('a')
            prerequisites_text = ""
            for prerequisite in prerequisites:
                prereq_name = prerequisite.text.strip()
                prereq_link = f"{base_url}{prerequisite['href']}"
                prerequisites_text += f"[{prereq_name}]({prereq_link})\n"
        else:
            prerequisites_text = "No prerequisites found."

        if degree_requirements_section:
            degree_requirements_text = degree_requirements_section.find_next('div').text.strip()
        else:
            degree_requirements_text = "No degree requirements found."

        response = f"Course: {course_title}\n\nDescription: {course_description}\n\nPrerequisites:\n{prerequisites_text}\n\nDegree Requirements:\n{degree_requirements_text}"

        dispatcher.utter_message(response)

        return []



class ActionRetrieveDepartmentChair(Action):
    def name(self) -> Text:
        return "action_retrieve_department_chair"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Fetch the webpage
        url = "https://sites.rhodes.edu/academic-affairs/department-chairs-program-chairs"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract department-chair mappings
        department_chairs = {}
        table = soup.find("table")
        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            columns = row.find_all("td")
            department = columns[0].text.strip()
            chair = columns[1].text.strip()
            department_chairs[department] = chair

        # Extract department entity from user input
        department_entity = next(tracker.get_latest_entity_values("department"), None)
        if not department_entity:
            dispatcher.utter_message("Sorry, I couldn't identify the department.")
            return []

        # Find the closest matching department
        matched_department, score = process.extractOne(department_entity, department_chairs.keys())

        if score >= 80:  # Adjust similarity threshold as needed
            chair = department_chairs[matched_department]
            dispatcher.utter_message(f"The chair of {matched_department} department is {chair}.")
        else:
            dispatcher.utter_message("Sorry, I couldn't find information about that department.")

        return [SlotSet("department", matched_department)]  # Set the department slot for future tracking

    





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
