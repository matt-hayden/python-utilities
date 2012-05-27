"""This script runs through MeterMaster files and builds a histogram of flow
rate for each one. The output is two CSV files: meters.csv and hist.csv.
Meters.csv has one row per file with meter information. Hist.csv is a
series of histogram tables organized by filename.
"""

from logging import debug, info, warning, error
import os.path
connection_string_template = ';'.join(
    ["Driver={Microsoft Access Driver (*.mdb)}",
    "Dbq=%s",
    "File Mode=Read Only"])
flow_rate_by_raw_sql_header = \
    [ 'RawData', 'Intervals', 'Average Flow Rate', 'Total Volume' ]
flow_rate_by_raw_sql = "SELECT RawData, Count(*) As Intervals," + \
    " Avg(RateData) AS MidPointGPM, Sum(RateData)/6 AS TotalVolumeGal" + \
    " FROM MMData where RawData > 0 GROUP BY RawData;"
meter_type_sql_header = [ 'Make', 'Model', 'Size', 'Unit',
                          'StorageInterval' ]
meter_type_sql = "SELECT "+' ,'.join(meter_type_sql_header)+" FROM MeterInfo;"
##
def findfiles(search_me, extensions = [ '.MDB', 'MDB' ]):
    """Extensions must be upper-case.
"""
    if '*' in search_me:
        from glob import glob
        return glob(search_me)
    else:
        from os import walk
        for root, dirs, files in walk(search_me):
            return [ os.path.join(root, filename) for filename in
                     filter(lambda x: os.path.splitext(x)[-1].upper()
                            in extensions, files) ]
##
"""There are at least 3 python database connectors. These are tried in
order. With some modification, Qt may be able to provide a connector
through PyQt.
"""
try:
    """mx.ODBC.iODBC is a commercial driver manager."""
    from mx.ODBC.iODBC import Connect as connect
    debug("Using mx.ODBC.iODBC")
except ImportError:
    try:
        """pyodbc is a free driver manager."""
        from pyodbc import connect, DatabaseError
        debug("Using pyodbc")
    except ImportError:
        try:
            """adodbapi is a Windows COM database driver."""
            from adodbapi import connect, DatabaseError
            debug("Using adodbapi")
        except ImportError:
            error("No valid database drivers installed")
            raise

def build_flow_histograms(search_me,
                          histo_table_filename, meter_type_filename):
    info("Opening files %s" % search_me)
    info("Output filenames are %s and %s"
         %(histo_table_filename, meter_type_filename))
    
    meter_type_sql_header.insert(0, "Filename")
    flow_rate_by_raw_sql_header.insert(0, "Filename")
    
    import csv
    mdb_files = findfiles(search_me)
    hist_wo = csv.writer(open(histo_table_filename, 'wb'))
    meter_wo = csv.writer(open(meter_type_filename, 'wb'))
    
    hist_wo.writerow(flow_rate_by_raw_sql_header)
    meter_wo.writerow(meter_type_sql_header)
    for pn in mdb_files:
        fn = os.path.split(pn)[-1]
        fn = os.path.splitext(fn)[0]
        fn = fn[0:5] ### five-digit keycodes
        info("Opening %s" % pn)
        try:
            con = connect(connection_string_template % pn)
            cur = con.cursor()
            ###
            cur.execute(meter_type_sql)
            cached_table = cur.fetchone()
            insert_me = [ i for i in cached_table ] ### i.strip() didn't work
            insert_me.insert(0, fn)
            cur.close()
            meter_wo.writerow(insert_me)
            ###
            cur = con.cursor()
            cur.execute(flow_rate_by_raw_sql)
            cached_table = cur.fetchall()
            cur.close()
            for i in cached_table:
                insert_me = list(i)
                insert_me.insert(0, fn)
                hist_wo.writerow(insert_me)
            ###
        except DatabaseError, e:
            warning("Opening database %s failed: %s" %(fn, e.message))
        finally:
            con.close()
    del hist_wo, meter_wo # irrelevant?
    
if __name__ == '__main__':
    search_me = r'Z:\Projects\IRWD SF Study 2005\T3 Logging\City of Davis\Davis MM'
    histo_table_filename = r's:\temp\hist.csv'
    meter_type_filename = r's:\temp\meters.csv'

    build_flow_histograms(search_me,
                          histo_table_filename,
                          meter_type_filename)