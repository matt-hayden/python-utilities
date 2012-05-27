import sqlite3 as input_db_driver

input_filename = "S:\\TW5\\60080.sqlite"

icon = input_db_driver.connect(input_filename)
cur = icon.cursor()
cur.execute("""SELECT name FROM sqlite_master
WHERE type='table'""")
print cur.fetchall()
