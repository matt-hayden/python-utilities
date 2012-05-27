#!env python
import adodbapi as input_db_driver

input_filename = "S:\\TW5\\60058.MDB"
input_filename = "S:\\TW5\\db1.MDB"
input_connection_string_template = ';'.join(
    ["Provider=Microsoft.Jet.OLEDB.4.0",
    "Data Source=%s"])
sql_for_table_list="""
SELECT Database, Null AS F2, Name, Type, Null AS f5
FROM MSysObjects
WHERE Type In (1);
"""

icon = input_db_driver.connect(input_connection_string_template % input_filename)

### adodbapi.adodbapi.DatabaseError
try:
    cur=icon.cursor()
    cur.execute(sql_for_table_list)
    print cur.fetchall()
except input_db_driver.adodbapi.DatabaseError, e:
    raise RuntimeError("""SQL code for ADODBAPI table list failed, possibly because of no read permission on MSysObjects.
For read-write database files, Tools -> Security and give Admin Read permissions on MSysObjects. """)
finally:
    del cur