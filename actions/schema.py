from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.future import Engine

# Define the base class for all your models
Base = declarative_base()

# Define the Departments table
class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)

# Define the Faculty table
class Faculty(Base):
    __tablename__ = 'faculty'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String)
    joined = Column(Integer)
    education = Column(Text)
    specialization = Column(Text)
    department_id = Column(Integer, ForeignKey('departments.id'))
    # Set up the relationship to the Department table
    department = relationship("Department", back_populates="faculty")

# Define the Courses table
class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    code = Column(String)
    name = Column(String)
    credits = Column(Integer)
    department_id = Column(Integer, ForeignKey('departments.id'))
    # Set up the relationship to the Department table
    department = relationship("Department", back_populates="courses")

# Define the Programs table
class Program(Base):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    degree_type = Column(String)
    requirements = Column(Text)
    department_id = Column(Integer, ForeignKey('departments.id'))
    # Set up the relationship to the Department table
    department = relationship("Department", back_populates="programs")

# Define the ProgramRequirements table
class ProgramRequirement(Base):
    __tablename__ = 'program_requirements'
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey('programs.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    requirement_type = Column(String)
    # Set up the relationships to the Program and Course tables
    program = relationship("Program", back_populates="requirements")
    course = relationship("Course")

# Define the HonorsProgram table
class HonorsProgram(Base):
    __tablename__ = 'honors_programs'
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey('programs.id'))
    requirements = Column(Text)
    eligibility_criteria = Column(Text)
    additional_information = Column(Text)
    # Set up the relationship to the Program table
    program = relationship("Program", back_populates="honors_program")

# Define relationships to be used by SQLAlchemy for querying
Department.faculty = relationship("Faculty", order_by=Faculty.id, back_populates="department")
Department.courses = relationship("Course", order_by=Course.id, back_populates="department")
Department.programs = relationship("Program", order_by=Program.id, back_populates="department")
Program.requirements = relationship("ProgramRequirement", order_by=ProgramRequirement.id, back_populates="program")
Program.honors_program = relationship("HonorsProgram", uselist=False, back_populates="program")

# Create a connection to the PostgreSQL database
# Note: Replace 'username', 'password', 'host', 'port', and 'database' with your PostgreSQL credentials
engine: Engine = create_engine(
    'postgresql://rhobot:rhobot@localhost/RHO-BOT',
    future=True  # Use the future flag for SQLAlchemy 2.0 compatibility
)





# Create all tables in the engine. This is equivalent to "Create Table" statements in raw SQL.
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine, future=True)  # Use the future flag here as well
session = Session()
