# app.py

""" GO TO
	state.py   for initialization values
	db.py      for general DB functions
	auth.py    for login() and register() functions
	member.py  for Member Functions
	trainer.py for Trainer Functions
"""

import state
from db import connectToDB, resetDB
from auth import login, register
from member import (
	getMetricHistory,
	getCurrentMetrics,
	updateMetrics,
	showDashboard,
	updatePersonalDetails,
	manageGoals,
	registerForClass
)
from trainer import (
	trainerViewAvail,
	trainerAddAvail,
	trainerMemberLookup,
)
from admin import createClass

def main():
	# open DB connection once at startup
	connectToDB()
	conn = state.conn

	try:
		while True:
			print("────────────────────────────────────────────────────────────────────────────")
			print("- <3 Health & Fitness Club <3 | Main Menu -\n")
			print(f"You are viewing as: {state.currentRole}")
			print("────────────────────────────────────────────────────────────────────────────")
			print("Choose from the options below.")
			print("        0: Exit")
			print("        1: Reset Database")
			print("        2: Login")
			print("        3: Register a Member")
			print("\n        Member Exclusive Functions")
			print("        4: Get Metric History")
			print("        5: Get Current Metrics")
			print("        6: Update Metrics")
			print("        7: Show My Active Dashboard")
			print("        8: Profile Management")
			print("        9: Member Goal Manager")
			print("        10: View Availability from Trainers")
			print("        11: Register For A Class")
			print("\n        Trainer Exclusive Functions")
			print("        12: Add Availability")
			print("        13: Member Lookup")
			print("\n        Admin Exclusive Functions")
			print("        14: Create Class")
			option = input("Type your option as a number: ")
			try:
				option = int(option)
			except Exception:
				print("\nPlease input an integer\n")
				continue

			match option:
				case 0:
					break
				case 1:
					resetDB()
				case 2:
					email = input("To login, please enter your Email: ")
					password = input("Now enter your password: ")
					login(email, password)
				case 3:
					print("\n-- Member Registration --")
					print("Please fill in the details below.")
					email = input("Email: ").strip()
					password = input("Password: ").strip()
					fname = input("First Name: ").strip()
					lname = input("Last Name: ").strip()
					bday = input("Birthday (YYYY-MM-DD): ").strip()
					gender = input("Gender (e.g., F/M/NB): ").strip()
					register(fname, lname, email, password, bday, gender)
				case 4:
					getMetricHistory()
				case 5:
					getCurrentMetrics()
				case 6:
					try:
						weight = float(input("Weight (kg): "))
						bf = float(input("Body Fat %: "))
						hr = float(input("Heartrate (bpm): "))
					except Exception:
						print("\nInvalid input, make sure to use real numbers\n")
						continue
					updateMetrics(weight, bf, hr)
				case 7:
					showDashboard()
				case 8:
					updatePersonalDetails()
				case 9:
					manageGoals()
				case 10:
					if state.currentRole == "System":
						print("\nPlease log in first. This feature is only available for Members and Staff.\n")
						continue
					trainerViewAvail()
				case 11:
					registerForClass()
				case 12:
					trainerAddAvail()
				case 13:
					trainerMemberLookup()
				case 14:
					createClass()
				case _:
					print("\nInvalid option, try again\n")
	finally:
		if conn is not None:
			conn.close()

if __name__ == "__main__":
	main()
