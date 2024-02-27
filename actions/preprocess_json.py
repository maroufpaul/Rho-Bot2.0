import json
from pathlib import Path

def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def clean_and_structure_data(data):
    # Initialize a dictionary to hold structured and cleaned data
    structured_data = {}
    
    # Iterate over each department in the data
    for department_name, department_info in data.items():
        # Initialize containers for this department
        structured_data[department_name] = {
            "faculty": [],
            "courses": [],
            "programs": [],
            "additional_info": []
        }
        
        # Clean and structure faculty information
        for faculty_member in department_info.get("faculty", []):
            structured_data[department_name]["faculty"].append({
                "name": faculty_member.get("name"),
                "specialization": faculty_member.get("specialization").lower().split(", ")
            })
        
        # Clean and structure courses and programs
        for program in department_info.get("programs", []):
            for course in program.get("requirements", {}).get("courses", []):
                course_name = " ".join(course.split()[1:])
                structured_data[department_name]["courses"].append(course_name.lower())
            structured_data[department_name]["programs"].append(program.get("programName").lower())
        
        # Optionally, add additional info such as honors programs
        honors_info = department_info.get("honorsProgram", {}).get("requirements", [])
        structured_data[department_name]["additional_info"].extend([info.lower() for info in honors_info])
    
    return structured_data

def save_processed_data(processed_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(processed_data, file, indent=4)

if __name__ == "__main__":
    # Paths to department JSON files
    department_files = [
        "D:/rhobot_rasa/data/cs_department_data.json",  # Adjusted path
        "D:/rhobot_rasa/data/physics_department_data.json"  # Adjusted path
        # Add paths to other department files as needed
    ]
    
    all_data = {}
    for department_file in department_files:
        department_data = load_json_data(department_file)
        department_name = department_data["departmentName"]
        all_data[department_name] = department_data
    
    processed_data = clean_and_structure_data(all_data)
    save_processed_data(processed_data, Path("D:/rhobot_rasa/data/processed_unified_index.json"))
