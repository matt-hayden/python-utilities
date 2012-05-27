#! python
# stole from stackoverflow
import os
def is_exe(fpath):
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
def which(program):
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        #for path in os.environ["PATH"].split(os.pathsep):
        for path in os.get_exec_path():
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None