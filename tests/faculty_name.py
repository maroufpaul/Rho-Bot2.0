import json
from os.path import join

# File paths
file_paths = [
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

# List to store faculty information
faculty_list = []

# Read faculty information from each department file
for file_path in file_paths:
    with open(file_path, 'r') as file:
        data = json.load(file)
        if 'faculty' in data and 'departmentName' in data:
            department_name = data['departmentName']

            for faculty_member in data['faculty']:
                faculty_member['departmentName'] = department_name
                faculty_list.append(faculty_member)

# Write faculty information to a new JSON file
output_file_path = "/Users/danyalbukhari/Rho-Bot2.0/data/Faculty_Info.json"
with open(output_file_path, 'w') as output_file:
    json.dump(faculty_list, output_file, indent=4)

print("Faculty information extracted and saved to:", output_file_path)