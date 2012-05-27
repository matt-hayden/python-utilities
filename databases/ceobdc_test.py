#!env python
import ceODBC as input_db_driver

input_filename = "S:\\TW5\\60080.MDB"
input_connection_string_template = ';'.join(
    ["Driver={Microsoft Access Driver (*.mdb)}",
    "Dbq=%s",
    "File Mode=Read Only"])

icon = input_db_driver.connect(input_connection_string_template % input_filename)
icur = icon.tables(type='TABLE')
print "Tables in %s:" % input_filename
print icur.fetchall()
#icon.close()