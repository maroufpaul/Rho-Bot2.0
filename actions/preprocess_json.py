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
            "description": department_info.get("description", ""),
            #"faculty": [],
            "programs": [],
            "minorRequirements": [],
            "honorsProgram": []
        }
        '''
        # Clean and structure faculty information
        for faculty_member in department_info.get("faculty", []):
            department = faculty_member.get("department", department_name) if isinstance(faculty_member, dict) else department_name
            # Add this print statement just before the line causing the KeyError
            if isinstance(faculty_member, dict):  # Check if faculty_member is a dictionary
                structured_data[department_name]["faculty"].append({
                    "name": faculty_member.get("name", ""),
                    "title": faculty_member.get("title", ""),
                    "education": faculty_member.get("education", ""),
                    "specialization": faculty_member.get("specialization", "").lower().split(", "),
                    "department": faculty_member.get("department", "")  # Include department information
                })
            elif isinstance(faculty_member, str):  # Handle the case where faculty_member is a string
                structured_data[department_name]["faculty"].append({
                    "name": faculty_member,
                    "title": "",  # You can set default values for title and specialization if needed
                    "specialization": [],
                    "department": "" # Include department information
                })'''

        
        # Clean and structure programs
        for program in department_info.get("programs", []):
            structured_data[department_name]["programs"].append({
                "programName": program.get("programName", ""),
                "degreeType": program.get("degreeType", ""),
                "requirements": program.get("requirements", {})
            })

        # Check if minorRequirements is present
        if "minorRequirements" in department_info:
            # Get the list of minor requirements
            minor_requirements_list = department_info["minorRequirements"]
            # Iterate over each set of minor requirements
            for minor_requirements in minor_requirements_list:
                if isinstance(minor_requirements, dict):  # Check if it's a dictionary
                    structured_data[department_name]["minorRequirements"].append({
                        "totalCredits": minor_requirements.get("totalCredits", ""),
                        "courses": minor_requirements.get("courses", [])
                    })
                else:
                    # Handle the case where minorRequirements is not a dictionary
                    # Set default values or handle it as needed
                    structured_data[department_name]["minorRequirements"] = {}
        else:
            # If minorRequirements is not present, handle it gracefully
            structured_data[department_name]["minorRequirements"] = {}



        # Clean and structure honors program details
        honors_program_list = department_info.get("honorsProgram", [])
        for honors_program in honors_program_list:
            structured_data[department_name]["honorsProgram"].append({
                "requirements": honors_program.get("requirements", [])
            })
        
        # Clean and structure additional info
        additional_info = department_info.get("additional_info", {})
        if additional_info:
            structured_data[department_name]["additional_info"] = additional_info
    
    return structured_data


def save_processed_data(processed_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(processed_data, file, indent=4)

if __name__ == "__main__":
    # Paths to department JSON files
    department_files = [
        "/Users/danyalbukhari/Rho-Bot2.0/data/Africana_Studies_Department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Asian_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Art_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Bio_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/BMB_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Business_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Chem_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Chinese_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/CS_department_data.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Econ_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Education_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Env_science_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Env_studies_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/French_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/German_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/GSS_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/History_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/JI&ME_studies_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Latin_american_studies_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Math&stats_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Media_studies_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Music_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Neuro_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/P_law_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Philosophy_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Physics_department_data.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Psychology_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Religious_studies_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Russian_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Spanish_department.json",
        "/Users/danyalbukhari/Rho-Bot2.0/data/Urban_studies_department.json"

    ]
    
    all_data = {}
    for department_file in department_files:
        try:
            department_data = load_json_data(department_file)
            department_name = department_data["departmentName"]  # Assuming each file contains "departmentName"
            all_data[department_name] = department_data
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading JSON from file: {department_file}")
            print(e)
    
    processed_data = clean_and_structure_data(all_data)
    # Add this print statement just before the line causing the KeyError
    print("Department Names in all_data:", all_data.keys())

    save_processed_data(processed_data, Path("/Users/danyalbukhari/Rho-Bot2.0/data/processed_unified_data.json"))
