import sqlite3



def dbconnect(db_path):

	try:
		conn = sqlite3.connect(db_path)
	except sqlite3.Error as e:
		sys.exit(1)

	return conn
