# member.py
from datetime import datetime
import state

# -----------------
# MEMBER FUNCTIONS ....
# -----------------

# getMetricHistory(), getCurrentMetrics(), updateMetrics(),
# listMemberGoals(), editGoal(), manageGoals(),
# buildProgressBar(), colorRatio(), showDashboard(), updatePersonalDetails()


def getMetricHistory():
    """
    Health History: Log multiple metric entries
    DO NOT OVERWRITE!
    """
    if state.currentUser == -1:
        print("\nYou must login first to view metric history.\n")
        return

    conn = state.conn
    cur = conn.cursor()

    try:
        # try to get every metric entry for the logged in member + order by DATE
        cur.execute("""
            SELECT metric_id, metric_date, weight, body_fat, heart_rate
            FROM metrics
            WHERE member_id = %s
            ORDER BY metric_date ASC;
        """, (state.currentUser,))
        rows = cur.fetchall()

        if not rows:
            print("\nNo metrics recorded yet.\n")
            return

        print("\n────────────── Metric History ──────────────")
        print(f"{'ID':<4} {'Date':<20} {'Weight(kg)':<12} {'BodyFat(%)':<12} {'HR(bpm)':<8}")
        print("─" * 60)

        for metric_id, metric_date, weight, body_fat, heart_rate in rows:
            date_str = metric_date.strftime("%Y-%m-%d %H:%M")
            print(f"{metric_id:<4} {date_str:<20} {weight:<12} {body_fat:<12} {heart_rate:<8}")

        print("─" * 60 + "\n")
    finally:
        cur.close()


def getCurrentMetrics():
    """
    get ONLY the latest metric entry for this user
    DESC + LIMIT 1 -> gives whatever most recently recorded
    """
    if state.currentUser == -1:
        print("\nYou must login first to view metrics.\n")
        return

    conn = state.conn
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT metric_date, weight, body_fat, heart_rate
            FROM metrics
            WHERE member_id = %s
            ORDER BY metric_date DESC
            LIMIT 1;
        """, (state.currentUser,))

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
    if state.currentUser == -1:
        print("\nYou must login first to update metrics.\n")
        return

    conn = state.conn
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO metrics (member_id, metric_date, weight, body_fat, heart_rate)
            VALUES (%s, NOW(), %s, %s, %s)
            """,
            (state.currentUser, weight, bf, hr)
        )
        conn.commit()
    except Exception as e:
        print("Could not update metrics:", e)
        conn.rollback()
    finally:
        cur.close()


def listMemberGoals():
    """
    print all goals for the currently logged-in member
    """
    if state.currentUser == -1:
        print("\nYou must log in first to view goals.\n")
        return []

    conn = state.conn
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
            (state.currentUser,)
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
            (state.currentUser,)
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
                # if unknown metric
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
    if state.currentUser == -1:
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
    conn = state.conn
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE goals
            SET goal_metric = %s
            WHERE goal_id = %s
              AND member_id = %s;
            """,
            (new_target, goal_id, state.currentUser)
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
    if state.currentUser == -1:
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
        return state.RED
    elif ratio < 0.67:
        return state.YELLOW
    else:
        return state.GREEN


# GLORIA LI SHOW DASHBOARD
def showDashboard():
    """
    Member dashboard showing metrics + active goals.
    """
    #1 check if user is logged in
    if state.currentUser == -1:
        print("You must log in first to view the dashboard.")
        return

    conn = state.conn
    cur = conn.cursor()

    # 2 get member info
    cur.execute(
        "SELECT fname, lname, class_count "
        "FROM members WHERE member_id = %s",
        (state.currentUser,)
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
        "FROM metrics WHERE member_id = %s "
        "ORDER BY metric_date ASC",
        (state.currentUser,)
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
        (state.currentUser,)
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
        # format the date and time to look clean
        datentime = metric_date.strftime("%Y-%m-%d %H:%M:%S")
        print(f"Last Updated On: {datentime}")
        # print metric data info
        print(f"   • Current Weight:       {current_weight} kg")
        print(f"   • Body Fat Percentage:  {current_body_fat}%")
        print(f"   • Average Heart Rate:   {current_heart_rate} bpm")

    # print goals label (58!)
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
                print(f"   Progress: {color}{bar} ({percent_str}){state.RESET}")

    print("\n" + "─" * 62)
    input("Press the any button + ENTER to return to the Main Menu...\n")


def updatePersonalDetails():
    if state.currentUser == -1:
        print("You must log in first.")
        return

    conn = state.conn
    cur = conn.cursor()

    # 1. Get current values
    cur.execute(
        "SELECT fname, lname, email, birthday, gender "
        "FROM members WHERE member_id = %s",
        (state.currentUser,)
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
            (new_fname, new_lname, new_email, new_bday, new_gender, state.currentUser)
        )
        conn.commit()
        print("\nProfile updated successfully!\n")
    except Exception as e:
        print("Could not update personal details:", e, "\n")
        conn.rollback()
    finally:
        cur.close()


def registerForClass():
    if state.currentUser == -1:
        print("You must log in first to register for classes.")
        return
    
    print("\n|     Member: Register For a Class     |")
    print("(type 0 at ANY prompt to go back to main menu)\n")

    conn = state.conn
    cur = conn.cursor()

    cur.execute("SELECT * FROM available_classes;")
    ret = cur.fetchall()
    if len(ret) == 0:
        print("There are currently no classes available for registration")
        return
    
    while True:
        classes = []
        print("Here are all the available classes for registration")
        print("   | Trainer Name    | Type    | Starting Time       | Ending Time         | Room  | Attendance | Capacity |")
        for i in range(len(ret)):
            class_id, name, purpose, start, end, room, attendance, capacity = ret[i]
            print(f"{i + 1}: | {name:<15} | {purpose:<7} | {start} | {end} | {room:<5} | {attendance:<10} | {capacity:<8} |")
            classes.append(class_id)
        
        while True:
            try:
                index = int(input("\nSelect which class you wish to register in: ")) - 1
                if index < 0:
                    print("Returning to Main Menu...")
                    return
            except ValueError:
                print("Please use one of the numbers to specify which class you wish to register in")
                continue
            break
        
        class_id = classes[i]
        cur.execute("SELECT * FROM class_regs WHERE class_id = %s AND member_id = %s", (class_id, state.currentUser))
        if cur.fetchone():
            print("You are already registered for this class")
            continue
        break
    cur.execute("INSERT INTO class_regs (class_id, member_id) VALUES (%s, %s);", (class_id, state.currentUser))
    cur.execute("UPDATE classes SET attendance = attendance + 1 WHERE class_id = %s", (class_id,))

    print("You have successfully registered for this class, enjoy!")
    input("Press enter to continue")