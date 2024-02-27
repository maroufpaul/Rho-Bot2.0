from actions.schema import Session, Department, Faculty, Course, Program, ProgramRequirement, HonorsProgram

def delete_everything_from_database():
    session = Session()

    try:
        # Delete all entries from the tables
        # The order of deletion matters due to foreign key constraints
        session.query(ProgramRequirement).delete()
        session.query(HonorsProgram).delete()
        session.query(Course).delete()
        session.query(Program).delete()
        session.query(Faculty).delete()
        session.query(Department).delete()

        session.commit()
        print("All data deleted successfully.")

    except Exception as e:
        session.rollback()  # Rollback the changes on error
        print(f"Failed to delete data: {e}")
    finally:
        session.close()  # Close the session to free resources

if __name__ == "__main__":
    delete_everything_from_database()
