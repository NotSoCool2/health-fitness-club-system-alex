# admin.py

from datetime import datetime
import state
from trainer import showTrainerAvailability

def bookRoom(room_id: int, start: datetime, end: datetime, purpose: str):
	conn = state.conn
	cur = conn.cursor()
	
	cur.execute(
		"""
		SELECT start_time, end_time
		FROM room_bookings
		WHERE room_id = %s
		AND NOT (%s <= start_time OR %s >= end_time);
		""",
		(room_id, end, start)
	)

	conflict = cur.fetchone()
	if conflict is not None:
		s_time, e_time = conflict
		raise Exception(f"\nERROR: This new booking overlaps with an existing one (so it can't be added).\nConflicting booking in room {room_id}: {s_time} -> {e_time}\n")

	cur.execute("INSERT into room_bookings (room_id, start_time, end_time, purpose) VALUES (%s, %s, %s, %s) RETURNING booking_id;", (room_id, start, end, purpose))
	ret = cur.fetchone()[0]
	if ret != None:
		conn.commit()
		print("Successfully booked the room")
	else:
		print("Something happened")
	cur.close()
	return ret


def createClass():
	if state.currentRole != "Admin":
		print("\nERROR: Admin access only. Please log in as an admin first.\n")
		return
	
	conn = state.conn
	cur = conn.cursor()
	print("\n|     Admin: Create a Class     |")
	print("(type 0 at ANY prompt to go back to main menu)\n")

	while True:
		purpose = input("Please enter the nature of your class (Private/Group): ").lower()
		if purpose not in ("private", "group"):
			print("\nPlease use one of the specified options\n")
			continue
		elif purpose == "0":
			print("Returning to Main Menu...")
			return
		else:
			break
	
	while True:
		try:
			trainer_id = int(input("Please input the ID of the trainer leading the class: "))
			if trainer_id == 0:
				print("Returning to Main Menu...")
				return
			cur.execute(f"SELECT fname, lname FROM trainers WHERE trainer_id = {trainer_id};")
			fname, lname = cur.fetchone()
			if fname == None:
				print("\nPlease input a valid trainer ID\n")
				continue
			print(f"You have chosen {fname} {lname}")
			break
		except ValueError:
			print("\nPlease input a positive integer\n")
			continue
	
	showTrainerAvailability(trainer_id)
	
	while True:
		try:
			date_str = input("Please input the date of the class (YYYY-MM-DD): ")
			if date_str == "0":
				print("Returning to Main Menu...")
				return
			start_str = input("Please input the starting time of the class (HH:MM): ")
			if start_str == "0":
				print("Returning to Main Menu...")
				return
			end_str = input("Please input the ending time of the class (HH:MM): ")
			if end_str == "0":
				print("Returning to Main Menu...")
				return

			start = datetime.strptime(f"{date_str} {start_str}", "%Y-%m-%d %H:%M")
			end   = datetime.strptime(f"{date_str} {end_str}", "%Y-%m-%d %H:%M")

		except Exception:
			print("Invalid date format, Please try again")
			continue

		cur.execute("SELECT end_time FROM trainer_availability WHERE trainer_id = %s AND start_time <= %s AND end_time >= %s;", (trainer_id, end, start))
		ret = cur.fetchone()
		if ret == None:
			print(f"\n{fname} {lname} is not available for those times\n")
			continue

		# Split up availability into 2 timeslots
		cur.execute("UPDATE trainer_availability SET end_time = %s WHERE trainer_id = %s AND start_time <= %s AND end_time >= %s;", (start, trainer_id, start, end))
		cur.execute("INSERT INTO trainer_availability (trainer_id, start_time, end_time) VALUES (%s, %s, %s);", (trainer_id, end, ret[0]))
		cur.execute("DELETE FROM trainer_availability WHERE trainer_id = %s AND end_time - start_time < INTERVAL '1 hour';", (trainer_id,)) # Maintain 1 hour availability

		cur.execute( # Show available rooms
			"""
			SELECT r.room_id, r.room_name, r.max_capacity
			FROM rooms r
			WHERE NOT EXISTS (
				SELECT 1
				FROM room_bookings b
				WHERE b.room_id = r.room_id
				AND b.start_time <= %s
				AND b.end_time >= %s
			);
			""", (end, start)
		)

		ret = cur.fetchall()
		if len(ret) == 0:
			print("\nThere are no available rooms for your given time, please try again\n")
			continue

		print("Here are the following available rooms")
		available_rooms = []
		for i in range(len(ret)):
			room_id, name, capacity = ret[i]
			print(f"{i + 1}: ({name}, Capacity: {capacity})")
			available_rooms.append(room_id)
		
		while True:
			try:
				room_id = int(input(f"\nPlease select a room "))
				if room_id == 0:
					return
				break
			except Exception:
				print("\nPlease input a valid number\n")

		break
		
	try:
		booking_id = bookRoom(room_id, start, end, purpose)
	except Exception:
		print("\nCould not book room, please try again\n")
		conn.rollback()
		return
	
	cur.execute("INSERT INTO classes (booking_id, trainer_id) VALUES (%s, %s);", (booking_id, trainer_id))
	print("Class successfully booked!")
	conn.commit()
	cur.close()