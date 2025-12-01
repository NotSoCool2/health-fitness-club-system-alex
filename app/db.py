# db.py
import psycopg2
import state

# connectToDB() and resetDB()

# -----------------
# GENERAL FUNCTIONS ....
# -----------------

def connectToDB():
	state.conn = psycopg2.connect(
		dbname="FinalProject",
		user="postgres",
		password="password", # GLORIA CHANGE IF TESTING TESTING ******** CHANGE THIS IF UR TESTING
		host="localhost",
		port="5432"
	)

def resetDB():
    conn = state.conn
    if conn is None:
        print("No DB Connection; call connectToDB() first")
        return

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