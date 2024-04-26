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

# List to store department names
departments = []

# Read department names from each file
for file_path in file_paths:
    with open(file_path, 'r') as file:
        data = json.load(file)
        if 'departmentName' in data:
            department_name = data['departmentName']
            departments.append(department_name)

# Clean up department names
departments = [department.strip() for department in departments]

# Remove duplicates while preserving order
departments = list(dict.fromkeys(departments))

# Sort the departments alphabetically
departments.sort()

print(departments)
