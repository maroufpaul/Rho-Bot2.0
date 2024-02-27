import json
from actions.schema import Session, Department, Faculty, Course, Program, ProgramRequirement, HonorsProgram  # Corrected import path

# Function to load JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Populates the 'departments' table with department data
def populate_departments(data, session):
    department = Department(name=data['departmentName'], description="A department at Rhodes College")
    session.add(department)
    session.commit()
    return department

# Populates the 'faculty' table with faculty data
def populate_faculty(data, department, session):
    for faculty_data in data['faculty']:
        faculty = Faculty(
            name=faculty_data['name'],
            title=faculty_data['title'],
            joined=int(faculty_data['joined']),
            education=faculty_data['education'],
            specialization=faculty_data['specialization'],
            department_id=department.id
        )
        session.add(faculty)
    session.commit()

# Populates the 'courses' table with courses data
def populate_courses(data, department, session):
    # Check if the department has a structured 'majorRequirements' with 'courses'
    if 'programs' in data:
        for program in data['programs']:
            if 'requirements' in program and 'courses' in program['requirements']:
                for course_data in program['requirements']['courses']:
                    # Assuming course_data is a string that contains both code and name
                    course_code, course_name = course_data.split(" ", 1) if " " in course_data else (course_data, course_data)
                    course = Course(
                        code=course_code,
                        name=course_name,
                        credits=None,  # Credits data to be added if available
                        department_id=department.id
                    )
                    session.add(course)
    session.commit()


def populate_programs(data, department, session):
    for program_data in data['programs']:
        # Serialize the requirements as a JSON string if it's not already a string
        requirements_str = json.dumps(program_data['requirements']) if not isinstance(program_data['requirements'], str) else program_data['requirements']
        
        program = Program(
            name=program_data['programName'],
            degree_type=program_data['degreeType'],
            requirements=requirements_str,
            department_id=department.id
        )
        session.add(program)
    session.commit()



# Populates the 'program_requirements' table
def populate_program_requirements(program, data, session):
    # Loop through each course in the major/minor requirements
    for course_data in data:
        # Extract the course code
        course_code = course_data.split()[0]
        # Find the course by its code
        course = session.query(Course).filter(Course.code == course_code).first()
        if course:
            program_requirement = ProgramRequirement(
                program_id=program.id,
                course_id=course.id,
                requirement_type='core'  # Assuming 'core' for this example
            )
            session.add(program_requirement)
    session.commit()

# Populates the 'honors_programs' table
def populate_honors_programs(data, program, session):
    # Check if honors program data exists
    if 'honorsProgram' in data:
        honors_program_data = data['honorsProgram']
        honors_program = HonorsProgram(
            program_id=program.id,
            requirements=json.dumps(honors_program_data['requirements']),
            eligibility_criteria='Minimum GPA of ' + str(honors_program_data.get('gpaRequirement')),
            additional_information=json.dumps(honors_program_data.get('additionalRequirements'))
        )
        session.add(honors_program)
        session.commit()

# Main function to execute the population scripts
def main():
    # Create a new database session
    session = Session()

    # Populate the CS department
    cs_data = load_json_data('data/cs_department_data.json')  # Load CS department data
    cs_department = populate_departments(cs_data, session)
    populate_faculty(cs_data, cs_department, session)
    populate_courses(cs_data, cs_department, session)
    cs_major_program, cs_minor_program = populate_programs(cs_data, cs_department, session)
    populate_program_requirements(cs_major_program, cs_data['majorRequirements']['courses'], session)
    populate_program_requirements(cs_minor_program, cs_data['minorRequirements']['courses'], session)
    populate_honors_programs(cs_data, cs_major_program, session)

    # Populate the Physics department
    physics_data = load_json_data('data/physics_department_data.json')  # Load Physics department data
    physics_department = populate_departments(physics_data, session)
    populate_faculty(physics_data, physics_department, session)
    populate_courses(physics_data, physics_department, session)
    physics_major_program, physics_minor_program = populate_programs(physics_data, physics_department, session)
    populate_program_requirements(physics_major_program, physics_data['majorRequirements']['courses'], session)
    populate_program_requirements(physics_minor_program, physics_data['minorRequirements']['courses'], session)
    populate_honors_programs(physics_data, physics_major_program, session)

    # Close the session
    session.close()

if __name__ == "__main__":
    main()

