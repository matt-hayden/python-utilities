
"""Different methods for opening MDB files.
"""
try:
    import ceODBC as import_driver
except ImportError:
    info("ceODBC not found... trying pyodbc")
    try:
        import pyodbc as import_driver
    except ImportError:
        info("pyodbc not found... trying adodbapi")
        import adodbapi as import_driver