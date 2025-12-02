# trainer.py

from datetime import datetime, timedelta
import state

# listAllTrainers(), showTrainerAvailability(), trainerViewAvail(),
# showMemberSummaryForStaff(), trainerMemberLookup(), trainerAddAvail()

# -----------------
# TRAINER SECTION....
# -----------------

def listAllTrainers():
    """
    helper fn: print all trainers w their ids and course offerings
    both available to member + staff
    """
    conn = state.conn
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


def showTrainerAvailability(trainer_id: int):
    """
    this is a helper function
    given a trainer_id, print trainer availability
    for trainerViewAvail() + staff views
    """
    conn = state.conn
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


def trainerViewAvail():
    """
    MEMBER FUNCTION:
    - MUST BE logged-in as a member or staff
    - shows trainers + lets user pick a trainer
    - shows their availability
    - repeats until u wanna exit
    """
    if state.currentRole == "System":
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

        # show chosen trainer availability
        showTrainerAvailability(trainer_id)

        # reprompt --> LOOP THIS
        again = input("View another trainer? (y/n): ").strip().lower()
        if again != "y":
            print("Returning to Main Menu...")
            return


def showMemberSummaryForStaff(member_id: int):
    """
    HELPER FUNC: (access only to trainer + admin)
    given member_id, DISPLAY:
    - basic info
    - last recorded metrics
    - all current goals
    """
    conn = state.conn
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
    if state.currentRole not in ("Trainer", "Admin"):
        print("\nERROR: Staff access only. Please log in as a trainer or admin.\n")
        return

    conn = state.conn

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
    - WITHIN business hours (06:00–22:00)
    - Session end time is after start time
    - No overlap with existing slots for that trainer
    - No availability in the past
    """
    if state.currentRole not in ("Trainer", "Admin"):
        print("\nERROR: Staff/Admin access only. Please log in as a trainer or admin first.\n")
        return

    conn = state.conn

    while True:
        cur = conn.cursor()
        print("\n|     Staff: Add Trainer Availability Slot     |")
        print("(type 0 at ANY prompt to go back to main menu)\n")
        try:
            # which trainer id we're adding to
            if state.currentRole == "Trainer":
                trainer_id = state.currentStaffId
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

                # Don't allow time slots in the past
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
                print("\nAvailability end time must be AFTER start time. Try again.\n")
                continue
            
            if start_dt - end_dt < timedelta(hours = 1):
                print("\nAvailability times must be longer than 1 hour\n")
                continue

            # business hours
            if not (6 <= start_dt.hour < 22 and 6 <= end_dt.hour <= 22):
                print("\nOur club only operates between 06:00 and 22:00.")
                print("Please choose a time window within business hours.\n")
                continue

            # check for overlapping slots for this specific trainer
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

            # add the new session
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
