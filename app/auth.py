# auth.py

import psycopg2
from datetime import datetime
import state

# login() and register() functions

# ADDED: passwords DONE!
def login(email: str, password: str):
    """
    login func
    - Members (members table)
    - Trainers (trainers table)
    - Admin (special trainer account by email)
    """
    conn = state.conn
    if conn is None:
        print("No DB connection from auth. Pls restart app.")
        return

    cur = conn.cursor()
    email = email.strip()

    try:
        # a) member login
        cur.execute(
            "SELECT member_id, fname, lname FROM members WHERE email = %s AND password = %s;",
            (email, password)
        )
        row = cur.fetchone()
        if row is not None:
            member_id, fname, lname = row
            state.currentUser = int(member_id)
            state.currentStaffId = -1
            state.currentRole = "Member"
            print(f"Successful MEMBER login: {fname} {lname} (Member ID {member_id})")
            return

        # b) try as trainer
        cur.execute(
            "SELECT trainer_id, fname, lname, email FROM trainers WHERE email = %s AND password = %s;",
            (email, password)
        )
        row = cur.fetchone()
        if row is not None:
            trainer_id, fname, lname, trainer_email = row
            state.currentUser = -1  # show that it is not logged in as a member
            state.currentStaffId = int(trainer_id)
            state.currentRole = "Trainer"
            print(f"Successful TRAINER login: {fname} {lname} (Trainer ID {trainer_id})")
            return

        # c) try as admin
        cur.execute(
            "SELECT admin_id FROM admins WHERE email = %s AND password = %s;",
            (email, password)
        )
        row = cur.fetchone()
        if row != None:
            admin_id = row[0]
            state.currentUser = -1
            state.currentStaffId = -1
            state.currentRole = "Admin"
            print(f"Successful ADMIN login: (Admin ID {admin_id})")
            return

        # if user is still guest
        print("\nYour email and password combination does not exist as a member or staff.")
        print("Try registering as a member first! :)\n")
        state.currentUser = -1
        state.currentStaffId = -1
        state.currentRole = "System"
    finally:
        cur.close()


def register(fname: str, lname: str, email: str, password: str, bday: str, gender: str):
    """
    User Registration: Create a new member with unique email and basic profile info.
    """
    conn = state.conn
    if conn is None:
        print("No DB connection in register.auth, pls restart the app.")
        return

    cur = conn.cursor()
    try:
        # registration checks 1) make sure there is an "@" somewhere
        if not email or "@" not in email:
            print("\nInvalid email. Please try again.\n")
            return
        # registration checks 2) make sure password prompt is filled
        if not password:
            print("\nPassword cannot be empty.\n")
            return
        # check birthday format
        try:
            datetime.strptime(bday, "%Y-%m-%d")
        except ValueError:
            print("\nBirthday must be in format YYYY-MM-DD (e.g., 2004-03-03).\n")
            return
        # check gender prompt
        if gender.strip() == "":
            print("\nGender cannot be empty.\n")
            return

        # INSERT w parameters
        cur.execute(
            """
            INSERT INTO members (fname, lname, email, password, birthday, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (fname, lname, email, password, bday, gender)
        )
        conn.commit()
        print("\nRegistration successful! Logging you in now...\n")

        # login using same email + password
        login(email, password)

    except psycopg2.errors.UniqueViolation:
        print("\nThat email is already taken! Try logging in instead.\n")
        conn.rollback()
    except Exception as e:
        print("\nCould not register user:", e, "\n")
        conn.rollback()
    finally:
        cur.close()
