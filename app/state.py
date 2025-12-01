# state.py
# global values + vars for app

# -----------------
# INITIALIZATION VALUES....
# -----------------

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