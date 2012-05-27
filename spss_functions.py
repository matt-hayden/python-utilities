#!env python
"""These are helper functions for SPSS, used in multiple Aquacraft projects.
"""

import os
import spss, spssaux
import sys
from textwrap import TextWrapper

linesep = os.linesep
spssterm = "."

def VarTableNameAndLabelList(*vars):
	"""
	"""
	if not vars or "*" in vars:
		vars = None
	#l = [ (v.Attributes['table'], v.VariableName, v.VariableLabel) for v in spssaux.VariableDict(vars) ]
	l = []
	for v in spssaux.VariableDict(vars):
		a = v.Attributes
		try:
			l += [ (a['table'] or "", v.VariableName, v.VariableLabel) ]
		except KeyError:
			l += [ ("", v.VariableName, v.VariableLabel) ]
	return l

def VarNameAndLabelList(*vars):
	"""
	"""
	if not vars or "*" in vars:
		vars = None
	l = [ (v.VariableName, v.VariableLabel) for v in spssaux.VariableDict(vars) ]
	return l

def VarLabelReplace(old, new, *vars):
	"""
	"""
	if not vars or "*" in vars:
		vars = None
	vd = spssaux.VariableDict(vars)
	for v in vd:
		oldlabel = v.VariableLabel
		newlabel = oldlabel.replace(old, new).strip()
		if newlabel.lower() != oldlabel.lower():
			v.VariableLabel = newlabel

def SetUnitsByVariablePattern(pattern, units):
	"""
	Set the units attribute based on a variable name pattern. For example:
	SetUnitsByVariablePattern(r'.*LPD, 'litres per day')
	"""
	vd = spssaux.VariableDict(pattern)
	for v in vd:
		# somehow, setting key=value in the dictionary doesn't work
		a = v.Attributes
		a['units'] = units
		v.Attributes = a

def VarNameReplace(old, new, *vars):
	"""
	Renames variables by substituting old with new.
	"""
	#syntax = [ "rename variables" ]
	syntax = []
	if not vars or "*" in vars:
		vars = None
	vd = spssaux.VariableDict(vars)
	for v in vd:
		oldname = v.VariableName
		newname = oldname.replace(old,new).strip()
		if newname.lower() != oldname.lower():
			syntax += [ "(%s=%s)" % (oldname, newname) ]
	if syntax:
		syntax.insert(0, "rename variables")
		syntax += [ spssterm ]
		if __debug__:
			print " ".join(syntax)
		spss.Submit(syntax)

def linewrap(width = None):
    """Returns a function that wraps long lines to a max of 251 characters.
	Note that this function returns a list of lines, which is suitable as the
	argument for the spss.Submit function.
    """
    wrapper = TextWrapper()
    wrapper.width = width or 251
    wrapper.replace_whitespace = True
    wrapper.break_long_words = False
    wrapper.break_on_hyphens = False
    return wrapper.wrap

wrap = linewrap()

def pythonInfo():
	print "executable:", sys.executable
	print "cwd:", os.getcwd()
	print "path:", linesep.join(sys.path)

def chdir(path):
	"""Wrapper that changes both Python and SPSS current working directory.
	"""
	os.chdir(path)
	syntax = "cd '%s'." % path
	if __debug__:
		print syntax
	spss.Submit(syntax)

def SpssMapToVar(function_name, vars, outvars = None):
    """function_name may be an SPSS function that takes one argument such
    as "lower", or a Python-formatted string such as "foo(bar,%s,baz)"
	"""
    if '%s' not in function_name:
        function_name += "(%s)"
    if outvars:
        if len(vars) != len(outvars):
            raise IndexError("number of input variables and output "
                             "variables don't match")
    else:
        outvars = vars
    syntax = []
    for old, new in zip(vars, outvars):
        rhs = function_name % old
        syntax += ["compute %(new)s=%(rhs)s." % locals()]
    if __debug__:
        print syntax
    spss.Submit(syntax)
	# Does not perform EXECUTE
def Int2Boolean(*args):
	"""Changes variables from Access boolean format to SPSS boolean format.
	"""
	SpssMapToVar("(%s ~= 0)", args)
	# Does not perform EXECUTE.
def SpssLower(*args):
	"""Try to manipulate all arguments into lowercase.
	"""
	SpssMapToVar("lower", args)
	# Does not perform EXECUTE

def AddSpssArgs(syntax, *args):
	"""
	>>> AddSpssArgs("echo foo.", "/bar", "/baz")
	echo foo /bar /baz.
	"""
	sep = " "
	syntax = syntax.strip()
	if syntax.endswith(spssterm):
		syntax = syntax[:-1]
	return syntax+sep+sep.join(args)
    # does not append . to the end of syntax
#
def MissingReplace(value, *vars):
	"""
	Converts missing values in variables indicated to a specific value.
	"""
	if value and vars:
		vd = spssaux.VariableDict()
		for v in vars:
			if v in vd:
				syntax = "if missing(%s) %s = %s." %(v,v,value)
				if __debug__:
					print syntax
				spss.Submit(syntax)
			else:
				raise ValueError("Variable %s not found" % v)
		try:
			if syntax:
				spss.Submit("execute.")
		except NameError:
			pass
	else:
		raise ValueError("MissingReplace called with bad arguments")
#
def autorecodeIntoSameVariable(*args):
	backup_varname_func = lambda v: "@%s_orig" % v
	recode_varname_func = lambda v: "@%s_recode" % v
	autorecode_options = [ "/print", ]
	if len(args) > 1:
		autorecode_options.append("/group")
	###
	backup_orig = True
	if args:
		#oldvarnames = list(map(str, args))
		oldvarnames = args
		newvarnames = map(recode_varname_func, oldvarnames)
		vd = spssaux.VariableDict()
		for v in newvarnames:
			if v in vd:
				syntax = "delete variable %s." % v
				if __debug__:
					print syntax
				spss.Submit(syntax)
		syntax = "autorecode variables=%s /into %s." % (" ".join(oldvarnames),
														" ".join(newvarnames) )
		if autorecode_options:
			syntax = AddSpssArgs(syntax, *autorecode_options)
		syntax = wrap(syntax) # syntax is now a list
		if __debug__:
			print syntax
		spss.Submit(syntax)
		###
		vd = spssaux.VariableDict()
		for old, new in zip(oldvarnames, newvarnames):
			if new in vd:
				if backup_orig:
					backup_var = backup_varname_func(old)
					if backup_var in vd:
						syntax = "delete variable %s." % backup_var
						if __debug__:
							print syntax
						spss.Submit(syntax)
					syntax = "rename variable %s = %s." % (old, backup_var)
				else:
					syntax = "delete variable %s." % old
				if __debug__:
					print syntax
				spss.Submit(syntax)
				syntax = "rename variable %s = %s." % (new, old)
				if __debug__:
					print syntax
				spss.Submit(syntax)
			else:
				raise NameError("Variable %s not found. Check AUTORECODE for failure." % new)
	# Does not perform EXECUTE, but execute following this function is 
	# recommended.

def RecodeYesNo(*args):
    backup_varname_func = lambda v: "@%s_verbatim" % v
    recode_varname_func = lambda v: "@%s_recode" % v
    ###
    if not args:
        raise ValueError("RecodeYesNo called without arguments")
    oldvarnames = list(args)
    newvarnames = map(recode_varname_func, oldvarnames)
    backupnames = map(backup_varname_func, oldvarnames)
    ###
    syntax = []
    vd = spssaux.VariableDict() # re-run every time veriables are likely to change, like after execute.
    ### delete backups of old vars
    ### delete target new vars, not necessary because RECODE overwrites args
    #delvars = [ v for v in newvarnames if v in vd ]+[ v for v in backupnames if v in vd ]
    delvars = [ v for v in backupnames if v in vd ]
    if delvars:
        syntax += [ "delete variables %s." % " ".join(delvars) ]
    syntax += [ "string #recode_me (A2)." ]
    for old, new in zip(oldvarnames, newvarnames):
        syntax += [ "compute #recode_me = lower(ltrim(%s))." % old,
                    "recode #recode_me ('ye','y','y_','1','-1','si'=1) ('no','n','n_','0'=0) INTO %s." % new]
    if syntax:
        syntax += [ "execute." ]
        if __debug__:
            print syntax
        spss.Submit(syntax)
        syntax = []
    ### assuming lists stay in order:
    syntax += [ "rename variables (%s = %s)." %(" ".join(oldvarnames), " ".join(backupnames)) ]
    syntax += [ "rename variables (%s = %s)." %(" ".join(newvarnames), " ".join(oldvarnames)) ]
    syntax += [ "variable level %s (nominal)." % " ".join(oldvarnames) ]
    syntax += [ "value labels %s 1 'Yes' 0 'No'." % " ".join(oldvarnames) ]
    syntax += [ "formats %s (F1.0)." % " ".join(oldvarnames) ]
    if syntax:
        # syntax += [ "execute." ] # not necessary for RENAME or FORMATS
        if __debug__:
            print syntax
        spss.Submit(syntax)
###
def AutorecodeIntoSameVariable(*args):
    backup_varname_func = lambda v: "@%s_verbatim" % v
    recode_varname_func = lambda v: "@%s_recode" % v
    ###
    if not args:
        raise TypeError("RecodeYesNo called without arguments")
    oldvarnames = list(args)
    newvarnames = map(recode_varname_func, oldvarnames)
    backupnames = map(backup_varname_func, oldvarnames)
    ###
    syntax = []
    vd = spssaux.VariableDict() # re-run every time veriables are likely to change, like after execute.
    ### delete backups of old vars
    ### delete target new vars, because AUTORECODE doesnt overwrite
    delvars = [ v for v in newvarnames if v in vd ]+[ v for v in backupnames if v in vd ]
    #delvars = [ v for v in backupnames if v in vd ]
    if delvars:
        syntax += [ "delete variables %s." % " ".join(delvars) ]
    syntax += [ "autorecode variables=%s /into %s." % (" ".join(oldvarnames),
                                                       " ".join(newvarnames) ) ]
    if syntax:
        syntax += [ "execute." ]
        if __debug__:
            print syntax
        spss.Submit(syntax)
        syntax = []
    ### assuming lists stay in order:
    syntax += [ "rename variables (%s = %s)." %(" ".join(oldvarnames), " ".join(backupnames)) ]
    syntax += [ "rename variables (%s = %s)." %(" ".join(newvarnames), " ".join(oldvarnames)) ]
    if syntax:
        # syntax += [ "execute." ] # not necessary for RENAME or FORMATS
        if __debug__:
            print syntax
        spss.Submit(syntax)