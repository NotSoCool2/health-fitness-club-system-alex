import psycopg2
from datetime import datetime, date

# -----------------
# INITIALIZATION VALUES....
# -----------------

# maybe add more commentation later

conn = None
currentUser = -1

# ADDED ROLE NAMES
currentRole = "System" # System, Member, Trainer, Admin
currentStaffId = -1

# Basic setup for querying:
# cur = conn.cursor()
# cur.execute(QUERY)
# If return data:
# 	for row in cur.fetchall(): print(row)
# cur.close()
# Push modifications to the DB:
# 	conn.commit()

# ANSI colors for terminal output (GLORIA)
RESET = "\033[0m"
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"

# -----------------
# GENERAL FUNCTIONS ....
# -----------------

def connectToDB():
	global conn
	conn = psycopg2.connect(
		dbname="FinalProject",
		user="postgres",
		password="password", # GLORIA TESTING TESTING ******** CHANGE THIS IF UR TESTING
		host="localhost",
		port="5432"
	)

def resetDB():
    cur = conn.cursor()
    try:
        # RUNNING SCHEMA DDL
        with open("./sql/DDL.sql", encoding="utf-8") as ddl_file: # I need to put ./ instead of ../ but it may just depend on our computers
            ddl_sql = ddl_file.read()
        if ddl_sql.strip():
            cur.execute(ddl_sql)
            conn.commit()
        else:
            print("DDL.sql appears to be empty. Check sql/DDL.sql.")
            cur.close()
            return

        # DML SAMPLE DATA RUNNING
        try:
            with open("./sql/DML.sql", encoding="utf-8") as dml_file: # I need to put ./ instead of ../ but it may just depend on our computers
                dml_sql = dml_file.read()
            if dml_sql.strip():
                cur.execute(dml_sql)
                conn.commit()
                print("\nDatabase successfully reset with sample data!\n")
            else:
                print("DDL loaded, but DML.sql is empty (no sample data).")
        except FileNotFoundError:
            print("DDL loaded, but DML.sql not found (no sample data).")

    except Exception as e:
        print("Couldn't load DDL/DML:", e)
        conn.rollback()
    finally:
        cur.close()

# ADDED: passwords DONE!
def login(email: str, password: str):
	"""
	login func
	- Members (members table)
	- Trainers (trainers table)
	- Admin (special trainer account)
	ADD PASSWORDS LATER, login is only determined by email rn
	"""
	global currentUser, currentRole, currentStaffId

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
			currentUser = int(member_id)
			currentStaffId = -1
			currentRole = "Member"
			print(f"Successful MEMBER login: {fname} {lname} (Member ID {member_id})")
			return

		# 2) try as trainer or admin login
		cur.execute(
			"SELECT trainer_id, fname, lname, email FROM trainers WHERE email = %s AND password = %s;",
			(email, password)
		)
		row = cur.fetchone()
		if row is not None:
			trainer_id, fname, lname, trainer_email = row
			currentUser = -1 # shows that it is not logged in as a member
			currentStaffId = int(trainer_id)
			# use this specific trainer as ADMINf or now, others are TRAINERs
			# change this email later if u want a different admin acc or add later
			if trainer_email.lower() == "gloria.li@healthnfitness.com":
				currentRole = "Admin"
				print(f"Successful ADMIN login: {fname} {lname} (Trainer ID {trainer_id})")
			else:
				currentRole = "Trainer"
				print(f"Successful TRAINER login: {fname} {lname} (Trainer ID {trainer_id})")
			return

		# if user is still guest
		print("\nYour email and password combination does not exist as a member or staff. Try registering as a member first! :)")
		currentUser = -1
		currentStaffId = -1
		currentRole = "System"
	finally:
		cur.close()


# -----------------
# MEMBER FUNCTIONS ....
# -----------------

def register(fname: str, lname: str, email: str, password: str, bday: str, gender: str):
	"""
	User Registration: Create a new member with unique email and basic profile info.
	"""
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

def getMetricHistory():
	"""
	Health History: Log multiple metric entries; do not overwrite. Must support time-stamped entries.
	"""
	cur = conn.cursor() 
	try:
		# try n get every metric entry for the logged-in member
		# then order by date
		cur.execute("""
			SELECT metric_id, metric_date, weight, body_fat, heart_rate
			FROM metrics
			WHERE member_id = %s
			ORDER BY metric_date ASC;
		""", (currentUser,))
		rows = cur.fetchall()
		if not rows:
			print("\nNo metrics recorded yet.\n")
			return
		print("\n────────────── Metric History ──────────────")
		print(f"{'ID':<4} {'Date':<20} {'Weight(kg)':<12} {'BodyFat(%)':<12} {'HR(bpm)':<8}")
		print("─" * 60)
		# loop thru each metric row and format the timestamp
		for metric_id, metric_date, weight, body_fat, heart_rate in rows:
			date_str = metric_date.strftime("%Y-%m-%d %H:%M")
			print(f"{metric_id:<4} {date_str:<20} {weight:<12} {body_fat:<12} {heart_rate:<8}")
		print("─" * 60 + "\n")
	finally:
		cur.close()

def getCurrentMetrics():
	cur = conn.cursor()
	# get ONLY the latest metric entry for this user
	# DESC + LIMIT 1 gives whatever they recorded most recently
	try:
		cur.execute("""
			SELECT metric_date, weight, body_fat, heart_rate
			FROM metrics
			WHERE member_id = %s
			ORDER BY metric_date DESC
			LIMIT 1;
		""", (currentUser,))

		row = cur.fetchone()

		if not row:
			print("\nNo metrics recorded yet.\n")
			return

		metric_date, weight, body_fat, heart_rate = row
		date_str = metric_date.strftime("%Y-%m-%d %H:%M")

		print("\n────────────── Current Metrics ──────────────")
		print(f"{'Last Updated:':<20} {date_str}")
		print(f"{'Weight (kg):':<20} {weight}")
		print(f"{'Body Fat (%):':<20} {body_fat}")
		print(f"{'Heart Rate (bpm):':<20} {heart_rate}")
		print("─────────────────────────────────────────────\n")

	finally:
		cur.close()

def updateMetrics(weight: float, bf: float, hr: float):
	"""
	Profile Management: input new health metrics (e.g., weight, heart rate).
	"""
	cur = conn.cursor()
	try:
		cur.execute("INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate) " \
		"VALUES (%d, NOW(), %.1f, %.1f, %.1f)" % (currentUser, weight, bf, hr))
		conn.commit()
	except Exception as e:
		print("Could not update metrics:", e)
		conn.rollback()
	cur.close()

# helper function
def getCurrentGoals():
	cur = conn.cursor()
	try:
		cur.execute("SELECT * FROM goals WHERE member_id = %s", (currentUser,))
		for row in cur.fetchall():
			print(row)
	finally:
		cur.close()

def listMemberGoals():
    """
    print all goals for the currently logged-in member
    """
    if currentUser == -1:
        print("\nYou must log in first to view goals.\n")
        return []

    cur = conn.cursor()
    try:
        # 1) get the goals
        cur.execute(
            """
            SELECT goal_id, metric_name, goal_metric
            FROM goals
            WHERE member_id = %s
            ORDER BY goal_id;
            """,
            (currentUser,)
        )
        goal_rows = cur.fetchall()

        if not goal_rows:
            print("\nYou have no goals set yet.\n")
            return []

        # get metric history for start + current
        cur.execute(
            """
            SELECT metric_date, weight, body_fat, heart_rate
            FROM metrics
            WHERE member_id = %s
            ORDER BY metric_date ASC;
            """,
            (currentUser,)
        )
        metric_rows = cur.fetchall()
        if not metric_rows:
            print("\nYou have goals, but no metrics recorded yet.\n")
            # still show basic goal info, but no start/current
            print("\n────────────── Your Goals ──────────────")
            print(f"{'ID':<4} {'Metric':<10} {'Target':<10}")
            print("─" * 30)
            for goal_id, metric_name, goal_metric in goal_rows:
                print(f"{goal_id:<4} {metric_name:<10} {goal_metric:<10}")
            print("─" * 30 + "\n")
            return goal_rows
        # earliest and latest metrics
        _, start_weight, start_bf, start_hr = metric_rows[0]
        _, current_weight, current_bf, current_hr = metric_rows[-1]
        print("\n────────────── Your Goals ──────────────")
        print(f"{'ID':<4} {'Metric':<10} {'Start':<10} {'Current':<10} {'Target':<10}")
        print("─" * 54)
        out_rows = []
        for goal_id, metric_name, goal_target in goal_rows:
            if metric_name == "weight":
                start_val = start_weight
                current_val = current_weight
            elif metric_name == "body_fat":
                start_val = start_bf
                current_val = current_bf
            elif metric_name == "heart_rate":
                start_val = start_hr
                current_val = current_hr
            else:
                # if unknwon metric
                start_val = None
                current_val = None
            print(f"{goal_id:<4} {metric_name:<10} {str(start_val):<10} {str(current_val):<10} {goal_target:<10}")
            out_rows.append((goal_id, metric_name, start_val, current_val, goal_target))
        print("─" * 54 + "\n")
        return out_rows
    finally:
        cur.close()

def editGoal():
	"""
	Profile Management: Update fitness goals (e.g., weight target)
	"""
	if currentUser == -1:
		print("\nYou must log in first to edit goals.\n")
		return

	# show current goals
	rows = listMemberGoals()
	if not rows:
		return
	# MAP -> valid IDs
	valid_ids = {row[0] for row in rows}
	goal_id_input = input("Enter the Goal ID you want to edit (or 0 to cancel): ").strip()
	if goal_id_input == "0":
		print("Cancelled editing goal.\n")
		return
	try:
		goal_id = int(goal_id_input)
	except ValueError:
		print("\nInvalid Goal ID.\n")
		return
	if goal_id not in valid_ids:
		print("\nThat Goal ID does not belong to you or does not exist.\n")
		return
	new_target_str = input("Enter the NEW target value: ").strip()
	try:
		new_target = float(new_target_str)
	except ValueError:
		print("\nInvalid number for target.\n")
		return
	# update DB
	cur = conn.cursor()
	try:
		cur.execute(
			"""
			UPDATE goals
			SET goal_metric = %s
			WHERE goal_id = %s
			AND member_id = %s;
			""",
			(new_target, goal_id, currentUser)
		)
		if cur.rowcount == 0:
			print("\nCould not find a matching goal to update.\n")
		else:
			conn.commit()
			print("\nGoal updated successfully!\n")
	except Exception as e:
		print("\nCould not update goal:", e, "\n")
		conn.rollback()
	finally:
		cur.close()

def manageGoals():
    """
    FOR UI -> goal management menu for members:
    - View goals
    - Edit goal target
    """
    if currentUser == -1:
        print("\nYou must log in first.\n")
        return
    while True:
        print("\n──── Member Goal Management ────")
        print("1) View my goals")
        print("2) Edit an existing goal target")
        print("0) Back to Main Menu")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print()
            return
        elif choice == "1":
            listMemberGoals()
        elif choice == "2":
            editGoal()
        else:
            print("Invalid choice, try again.\n")

def createGoal(goalname: str, goalval: float):
	cur = conn.cursor()
	try:
		cur.execute(
			"""
			SELECT weight, body_fat, heart_rate
			FROM metrics
			WHERE member_id = %s
			ORDER BY metric_date DESC
			LIMIT 1;
			""",
			(currentUser,)
		)
		row = cur.fetchone()
		if row is None:
			print("\nYou need at least one metric recorded before creating a goal.\n")
			return
		if goalname == "weight":
			currentval = row[0]
		elif goalname == "body_fat":
			currentval = row[1]
		elif goalname == "heart_rate":
			currentval = row[2]
		else:
			print("\nUnknown goal metric type.\n")
			return
		cur.execute(
			"""
			INSERT INTO goals (member_id, metric_name, current_metric, goal_metric)
			VALUES (%s, %s, %s, %s);
			""",
			(currentUser, goalname, currentval, goalval)
		)
		conn.commit()
	except Exception as e:
		print("\nCould not create goal:", e, "\n")
		conn.rollback()
	finally:
		cur.close()


# helper function used in showDashboard()
def buildProgressBar(current: float, goal: float, start: float):
	"""
	calculates a member's progress:
	- weight loss, fat loss, HR improvement
	- weight gain
	"""
	# ERROR CASE make sure u cant divide by 0
	if start is None or current is None or goal is None:
		return "N/A", "N/A", 0.0
	if start == goal:
		return "N/A", "N/A", 0.0
	# WEIGHT LOSS (target is lower than init weight)
	if goal < start:
		ratio = (start - current) / (start - goal)
	# GAIN GOALS (target is higher)
	else:
		ratio = (current - start) / (goal - start)
	# clamp 0–1
	if ratio < 0:
		ratio = 0
	elif ratio > 1:
		ratio = 1

	filled = round(ratio * 10)
	bar = "◉" * filled + "○" * (10 - filled)
	percent = round(ratio * 100)

	return bar, f"{percent}%", ratio

def colorRatio(ratio: float) -> str:
	"""
	Choose color based on progress ratio:
	- 0–33%: red
	- 34–66%: yellow
	- 67–100%: green
	"""
	if ratio < 0.34:
		return RED
	elif ratio < 0.67:
		return YELLOW
	else:
		return GREEN

# GLORIA LI SHOW DASHBOARD
def showDashboard():
	#1 check if user is logged in
	if currentUser == -1:
		# if not:
		print("You must log in first to view the dashboard.")
		return
	cur = conn.cursor()
	# 2 get member info
	cur.execute(
		"SELECT fname, lname, class_count "
		"FROM members WHERE member_id = %d" % currentUser
	)
	member_row = cur.fetchone()
	if member_row is None:
		print("Member not found.")
		cur.close()
		return
	fname, lname, class_count = member_row
	# 3) get metrics
	cur.execute(
		"SELECT metric_date, weight, body_fat, heart_rate "
		"FROM metrics WHERE member_id = %d "
		"ORDER BY metric_date ASC" % currentUser
	)
	metric_rows = cur.fetchall()
	if not metric_rows:
		metric_date = None
		current_weight = None
		current_body_fat = None
		current_heart_rate = None
		start_weight = None
		start_body_fat = None
		start_heart_rate = None
	else:
		# earliest and latest metrics
		first_date, start_weight, start_body_fat, start_heart_rate = metric_rows[0]
		metric_date, current_weight, current_body_fat, current_heart_rate = metric_rows[-1]

	# 4 get member goals
	cur.execute(
		"SELECT metric_name, current_metric, goal_metric "
		"FROM goals WHERE member_id = %s",
		(currentUser,)
	)
	goal_rows = cur.fetchall()
	cur.close()
	# 5 printing dashboard
	print("\n" + "╔" + "═" * 58 + "╗")
	print("║" + "MEMBER DASHBOARD".center(58) + "║")
	print("╚" + "═" * 58 + "╝")
	print(f"Welcome to your dashboard, {fname} {lname}!")
	print(f"Classes Attended: {class_count}\n")
	# print metrics label (58!!!)
	print("────────────────────────── Metrics ──────────────────────────")
	if metric_date is None:
		print("No metrics recorded yet. To add your first metrics now, press Enter to go back to the menu for updates.")
	else:
		# format the date and time to look clean, use % and then Y, m, d, H, M, and S
		datentime = metric_date.strftime("%Y-%m-%d %H:%M:%S")
		print(f"Last Updated On: {datentime}")
		#print the metric data info, weight in kg, body fat (body_fat) as a % and heart rate (heart_rate) in bpm, remember to TAB to format
		print(f"   • Current Weight:     {current_weight} kg")
		print(f"   • Body Fat Percentage:   {current_body_fat}%")
		print(f"   • Average Heart Rate: {current_heart_rate} bpm")
	# print goals label (58!) might update later after alex codes goals fn
	print("\n────────────────────── Active Goals ────────────────────────")
	if not goal_rows:
		print("No goals set yet. Make your goal today!")
	else:
		for metric_name, current_metric, goal_metric in goal_rows:
			# pick the correct start + current value based on metric name
			if metric_name == "weight":
				start_val = start_weight
				current_val = current_weight
			elif metric_name == "body_fat":
				start_val = start_body_fat
				current_val = current_body_fat
			elif metric_name == "heart_rate":
				start_val = start_heart_rate
				current_val = current_heart_rate
			else:
				print(f"\n{metric_name} Goal:")
				print("   Progress: (unknown metric type)")
				continue
			print(f"\n{metric_name} Goal:")
			# show the REAL start/current based on metrics history
			print(f"   Start:   {start_val}")
			print(f"   Current: {current_val}")
			print(f"   Target:  {goal_metric}")
			bar, percent_str, ratio = buildProgressBar(current_val, goal_metric, start_val)
			if bar == "N/A":
				print("   Progress: N/A")
			else:
				color = colorRatio(ratio)
				print(f"   Progress: {color}{bar} ({percent_str}){RESET}")
	print("\n" + "─" * 62)
	input("Press the any button + ENTER to return to the Main Menu...\n")


def updatePersonalDetails():
	if currentUser == -1:
		print("You must log in first.")
		return
	# make sure check it is logged in
	cur = conn.cursor()
	# 1. Get current values
	cur.execute(
		"SELECT fname, lname, email, birthday, gender "
		"FROM members WHERE member_id = %d" % currentUser
	)
	# check if member exists
	row = cur.fetchone()
	if row is None:
		print("Member not found.")
		cur.close()
		return
	current_fname, current_lname, current_email, current_bday, current_gender = row
	print("\n| Edit Personal Details |")
	print("*** Press ENTER to keep the current value. ***\n")
	new_fname  = input(f"Change First name [Your current first name is: {current_fname}]: ").strip()
	new_lname  = input(f"Last name [Your last name currently is: {current_lname}]: ").strip()
	new_email  = input(f"Email [Current email:{current_email}]: ").strip()
	new_bday   = input(f"Birthday (YYYY-MM-DD) [Current BD: {current_bday}]: ").strip()
	new_gender = input(f"Gender [{current_gender}]: ").strip()
	# keep old var if user just pressed enter
	if new_fname  == "": new_fname  = current_fname
	if new_lname  == "": new_lname  = current_lname
	if new_email  == "": new_email  = current_email
	if new_bday   == "": new_bday   = current_bday
	if new_gender == "": new_gender = current_gender
	try:
		cur.execute(
			"UPDATE members SET fname = %s, lname = %s, email = %s, "
			"birthday = %s, gender = %s WHERE member_id = %s",
			(new_fname, new_lname, new_email, new_bday, new_gender, currentUser)
		)
		conn.commit()
		print("\nProfile updated successfully!\n")
	except Exception as e:
		print("Could not update personal details:", e, "\n")
		conn.rollback()
	finally:
		cur.close()

# helper fn
def listAllTrainers():
	"""
	helper fn: print all trainers w their ids and course offerings
	both available to member + staff
	"""
	cur = conn.cursor()
	print("\n--- Trainer Directory ---")
	try:
		cur.execute(
			"SELECT trainer_id, fname, lname, specialization "
			"FROM trainers ORDER BY trainer_id;"
		)
		trainers = cur.fetchall()

		if not trainers:
			print("No trainers found.\n")
		else:
			print("Available Trainers:\n")
			for tid, fname, lname, spec in trainers:
				print(f"  ID {tid}: {fname} {lname} — {spec}")
			print()
	except Exception as e:
		print("Could not fetch trainer list:", e)
	finally:
		cur.close()

# print availability of trainer
def showTrainerAvailability(trainer_id: int):
	"""
	this is a helper function
	given a trainer_id, print trainer availability
	for trainerViewAvail()
	"""
	cur = conn.cursor()
	try:
		cur.execute(
			"""
			SELECT t.fname, t.lname,
				   a.slot_id, a.start_time, a.end_time
			FROM trainer_availability a
			JOIN trainers t ON a.trainer_id = t.trainer_id
			WHERE a.trainer_id = %s
			ORDER BY a.start_time;
			""",
			(trainer_id,)
		)
		rows = cur.fetchall()
		if not rows:
			print("No availability slots found for this trainer.\n")
			return
		trainer_fname, trainer_lname = rows[0][0], rows[0][1]
		print(f"\nAvailability for Trainer {trainer_id} — {trainer_fname} {trainer_lname}:\n")
		for _, _, slot_id, start_time, end_time in rows:
			print(f"  Slot {slot_id}: {start_time} -> {end_time}")
		print()
	except Exception as e:
		print("Could not fetch availability:", e)
	finally:
		cur.close()

#full function
def trainerViewAvail():
	"""
	MEMBER FUNCTION:
	- MUST BE logged-in as a member+
	- shows trainers + lets user pick a trainer
	- shows their availability
	- repeats until u wanna exit
	"""
	global currentRole
	if currentRole == "System":
		print("Please log in first to view trainer availability.")
		return
	while True:
		# show all the trainers that are in db
		listAllTrainers()
		# prompt: choose by trainer id
		print("| Trainer: View Availability |")
		trainer_id_input = input("Enter Trainer ID (or '0' to return to menu): ").strip()
		if trainer_id_input == "0":
			print("Returning to Main Menu...")
			return
		try:
			trainer_id = int(trainer_id_input)
		except Exception:
			print("Invalid input. Please enter a valid trainer ID.\n")
			continue
		# 3. show chosen trainer availability
		showTrainerAvailability(trainer_id)
		# 4. reprompt --> LOOP THIS
		again = input("View another trainer? (y/n): ").strip().lower()
		if again != "y":
			print("Returning to Main Menu...")
			return


# -----------------
# TRAINER SECTION....
# -----------------

def showMemberSummaryForStaff(member_id: int):
	"""
	HELPER FUNC: (access only to trainer + admin)
	given member_id, DISPLAY:
	- basic info
	- last recorded metrics
	- all current goals
	"""
	cur = conn.cursor()
	try:
		# 1) basic member info
		cur.execute(
			"""
			SELECT fname, lname, email
			FROM members
			WHERE member_id = %s;
			""",
			(member_id,)
		)
		row = cur.fetchone()
		if not row:
			print("\nMember not found.\n")
			return
		fname, lname, email = row
		# 2) last metrics
		cur.execute(
			"""
			SELECT metric_date, weight, body_fat, heart_rate
			FROM metrics
			WHERE member_id = %s
			ORDER BY metric_date DESC
			LIMIT 1;
			""",
			(member_id,)
		)
		latest_metric = cur.fetchone()
		# 3) goals
		cur.execute(
			"""
			SELECT metric_name, current_metric, goal_metric
			FROM goals
			WHERE member_id = %s
			ORDER BY metric_name;
			""",
			(member_id,)
		)
		goals = cur.fetchall()
		print("\n──────── Member Snapshot ────────")
		print(f"Name:  {fname} {lname}")
		print(f"Email: {email}")
		if latest_metric is None:
			print("\nLast Recorded Metrics: (none yet)")
		else:
			metric_date, weight, body_fat, heart_rate = latest_metric
			print("\nLast Recorded Metrics:")
			print(f"  Date:        {metric_date.strftime('%Y-%m-%d %H:%M')}")
			print(f"  Weight (kg): {weight}")
			print(f"  Body Fat %:  {body_fat}")
			print(f"  HR (bpm):    {heart_rate}")
		print("\nGoals:")
		if not goals:
			print("  (no goals set yet)")
		else:
			print(f"{'Metric':<10} {'Current':<10} {'Target':<10}")
			print("─" * 32)
			for metric_name, current_metric, goal_metric in goals:
				print(f"{metric_name:<10} {current_metric:<10} {goal_metric:<10}")
		print("────────────────────────────────\n")
	finally:
		cur.close()

def trainerMemberLookup():
	"""
	TRAINER/ADMIN FUNCTION CHECKLIST
	- search for members by name MAKE SURE ITS case insensitive
	- View last metrics + current goals in READ-ONLY mode
	"""
	global currentRole
	if currentRole not in ("Trainer", "Admin"):
		print("\nERROR: Staff access only. Please log in as a trainer or admin.\n")
		return
	while True:
		print("\n| Staff: Member Lookup |")
		name_query = input("Enter member name (or '0' to return to main menu): ").strip()
		if name_query == "0":
			print("Returning to Main Menu...\n")
			return
		search_pattern = f"%{name_query.lower()}%"
		cur = conn.cursor()
		try:
			# case-insensitive search: fname, lname, or full name
			cur.execute(
				"""
				SELECT member_id, fname, lname, email
				FROM members
				WHERE LOWER(fname) LIKE %s
				OR LOWER(lname) LIKE %s
				OR LOWER(fname || ' ' || lname) LIKE %s
				ORDER BY member_id;
				""",
				(search_pattern, search_pattern, search_pattern)
			)
			matches = cur.fetchall()
			if not matches:
				print("\nNo members found with that name, please try again.\n")
				continue
			print("\nSearch results:")
			for mid, fname, lname, email in matches:
				print(f"  ID {mid}: {fname} {lname} ({email})")
			chosen = input("\nEnter Member ID to view details (or '0' to search again): ").strip()
			if chosen == "0":
				continue
			try:
				member_id = int(chosen)
			except ValueError:
				print("\nInvalid member ID. Please try again.\n")
				continue
			valid_ids = {row[0] for row in matches}
			if member_id not in valid_ids:
				print("\nThat member ID was not in the search results. Pls try again.\n")
				continue
			# display
			showMemberSummaryForStaff(member_id)
			again = input("Look up another member? (y/n): ").strip().lower()
			if again != "y":
				print("Returning to Main Menu...\n")
				return
		finally:
			cur.close()


def trainerAddAvail():
	"""
	TRAINER / ADMIN FUNCTION
	- Trainer: can only add availability for themselves
	- Admin: can add availability for any trainer
	FORMATTING
	- Date (YYYY-MM-DD)
	- Start time (HH:MM, 24-hr)
	- End time (HH:MM, 24-hr)
	MAKE SURE IT IS:
	- WITHIN business hours (06:00–22:00) (we're just gonna do that for now, can change it later)
	- Session end time is after start time
	- No overlap with existing slots for that trainer
	"""
	global currentRole, currentStaffId
	# only trainers/admin can even enter this function
	if currentRole not in ("Trainer", "Admin"):
		print("\nERROR: Staff/Admin access only. Please log in as a trainer or admin first.\n")
		return
	while True:
		cur = conn.cursor()
		print("\n|     Staff: Add Trainer Availability Slot     |")
		print("(type 0 at ANY prompt to go back to main menu)\n")
		try:
			# which trainer id we're adding to
			if currentRole == "Trainer":
				trainer_id = currentStaffId
				if trainer_id == -1:
					print("ERROR: No staff ID associated with this session. Please log in again.")
					cur.close()
					return
				print(f"Adding availability for YOURSELF (Trainer ID {trainer_id}).")
			else:
				# allow admin to have all access
				listAllTrainers()
				trainer_id_input = input("Enter Trainer ID (or 0 to cancel): ").strip()
				if trainer_id_input == "0":
					print("Returning to Main Menu...")
					return
				try:
					trainer_id = int(trainer_id_input)
				except ValueError:
					print("Invalid Trainer ID. Try again.\n")
					continue
			# ask for date and time separately
			date_str = input("Date (YYYY-MM-DD): ").strip()
			if date_str == "0":
				print("Returning to Main Menu...")
				return
			start_time_str = input("Start time (HH:MM, 24-hour): ").strip()
			if start_time_str == "0":
				print("Returning to Main Menu...")
				return
			end_time_str = input("End time   (HH:MM, 24-hour): ").strip()
			if end_time_str == "0":
				print("Returning to Main Menu...")
				return
			# combine to time strings
			start_str = f"{date_str} {start_time_str}"
			end_str   = f"{date_str} {end_time_str}"
			# make them into datetime objects
			try:
				start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
				end_dt   = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
				# 3.5) Don't allow time slots in the past
				today = datetime.now().date()
				if start_dt.date() < today:
					print("\nYou can't create availability in the past.")
					print("Please choose today or a future date.\n")
					continue
			except ValueError:
				print("\nInvalid date/time format. Please use:")
				print("  Date: YYYY-MM-DD   (e.g. 2025-12-01)")
				print("  Time: HH:MM (24-hr, e.g. 18:30)\n")
				continue
			# end after start (one of the CHECKS)
			if end_dt <= start_dt:
				print("\nSession end time must be AFTER start time. Try again.\n")
				continue
			# 5) business hours
			if not (6 <= start_dt.hour < 22 and 6 <= end_dt.hour <= 22):
				print("\nOur club only operates between 06:00 and 22:00.")
				print("Please choose a time window within business hours.\n")
				continue
			# 6) check for overlapping slots for this specific trainer
			cur.execute(
				"""
				SELECT slot_id, start_time, end_time
				FROM trainer_availability
				WHERE trainer_id = %s
				AND NOT (%s <= start_time OR %s >= end_time);
				""",
				(trainer_id, end_dt, start_dt)
			)
			conflict = cur.fetchone()
			if conflict is not None:
				slot_id, s_time, e_time = conflict
				print("\nERROR: This new slot overlaps with an existing one (so it can't be added).")
				print(f"Conflicting Slot {slot_id}: {s_time} -> {e_time}\n")
				continue
			# 7) add the new session
			cur.execute(
				"""
				INSERT INTO trainer_availability (trainer_id, start_time, end_time)
				VALUES (%s, %s, %s);
				""",
				(trainer_id, start_dt, end_dt)
			)
			conn.commit()
			print("\nAvailability slot added successfully!!! :D\n")
			# ask user if they want to add another one before leaving
			again = input("Add another slot? (y/n): ").strip().lower()
			if again != "y":
				print("Returning to Main Menu...")
				return
		except Exception as e:
			print("\nSomething went wrong while adding the slot:", e)
			print("Try again.\n")
			conn.rollback()
			continue
		finally:
			cur.close()









connectToDB()
# Run the program
while True:
	print("────────────────────────────────────────────────────────────────────────────")
	print("- <3 Health & Fitness Club <3 | Main Menu -\n")
	print(f"You are viewing as: {currentRole}")
	print("────────────────────────────────────────────────────────────────────────────")
	print("Choose from the options below.")
	print("		1: Reset Database")
	print("		2: Login")
	print("		3: Register a Member ")
	print("		4: Get Metric History")
	print("		5: Get Current Metrics")
	print("		6: Update Metrics")
	print("		7: Show My Active Dashboard")
	print("		8: Profile Management")
	print("		9: Member Goal Manager")
	print("		10: Get Training Now | View Availability from Trainers")
	print("		11: Trainer Access ONLY -> Add Availability")
	print("		12: Trainer Access ONLY -> Member Lookup")
	print("		0: Exit")
	option = input("Type your option as a number: \n")
	try:
		option = int(option)
	except Exception:
		print("\nPlease input an integer\n")
		continue
	match option: # FOR MEMBER ONLY FUNCTIONS YOU CAN CHECK WITH currentUser == -1:
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
			if currentUser == -1:
				print("\nERROR: Could not get metric history.\n")
				continue
			getMetricHistory()
		case 5:
			if currentUser == -1:
				print("\nERROR: Could not retrieve current metrics.\n")
				continue
			getCurrentMetrics()
		case 6:
			if currentUser == -1:
				print("\nERROR: Could not update metrics. Try again.\n")
				continue
			try:
				weight = float(input("Weight (kg): "))
				bf = float(input("Body Fat %: "))
				hr = float(input("Heartrate (bpm): "))
			except Exception:
				print("\nInvalid input, make sure to use real numbers\n")
				continue
			updateMetrics(weight, bf, hr)
		case 7:
			if currentUser == -1:
				print("ERROR: Could not show dashboard, try logging in.\n")
				continue
			showDashboard()
		case 8:
			if currentUser == -1:
				print("\nERROR: Could not update personal details. Pls try again!\n")
				continue
			updatePersonalDetails()
		case 9:
			if currentUser == -1:
				print("\nERROR: You must be logged in as a member to manage goals.\n")
				continue
			manageGoals()

		case 10:
			if currentRole == "System":
				print("\nPlease log in first. This feature is only available for Members and Staff.\n")
				continue
			trainerViewAvail()
		case 11:
			trainerAddAvail()
		case 12:
			trainerMemberLookup()
		case _:
			print("\nInvalid option, try again\n")

conn.close()