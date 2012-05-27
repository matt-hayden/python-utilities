"""Another library of useful utility routines for SPSS"""


import spss, spssaux, spssdata
import sys
import time, os, re, fnmatch, glob, copy, random
from spssaux import _smartquote
from spssaux import u

#try:
    #import wingdbstub
#except:
    #pass

spssver = spssaux.getSpssVersion()
ok1600 = spssver >= [16,0,0]
ok1800 = spssver >= [18,0,0]


# (C) Copyright 2005-2009  SPSS Inc.

# JKP
#History
#    20-jan-2006 Add FindFilesWithVars function
#    05-Dec-2006 Add FindEmptyVars function
#    15-Dec-2006 Add FindUnlabelledValues function
#    12-Jan-2006 Add genCategoryList function
#    07-Feb-2007 Add rankvarsincase function
#    03-Jul-2007  Add support for weights to genCategoryList
#    24-Jul-2007  Add mergeByLabel function to add cases with renaming based on variable labels
#    02-Nov-2007 Add dupVarnameCheck function to expand and check variable lists
#    07-Jan-2008  Add genCategoriesWSubtotals and CopyValueSets
#    01-Apr-2008  Add getVarValues and generalizedSplit
#    13-Jun-2008  Add genValueLabels
#     19-Aug-2008 Add applySyntaxToFiles
#    9-Sep-2008    Add labelseparator option to CreateBasisVariables and robustify syntax.
#    14-Oct-2008  Add tallydates function to generate dataset for dates in interval
#     19-nov-2008 Add getMRSetNames and getMRSetInfo for  mult response set info
#     17-feb-2009  Add optional parameter to getVarValues for labels and add text output to generalizedSplit
#      19-feb-2009 Add genSortedVariableExpr to get variable list macro sorted by stats
#    29-apr-2009  Add ntiler to partition sums of values into approximately equal segments
#    28-sep-2009  Add setMacrosFromData to create macro values from a dataset
#    28-apr-2010  flatten getMRSetInfo return values
#    30-jun-2010   Add getRole
#    15-sep-2010  Add generateData to append data for current dictionary

__author__ =  'spss'
__version__=  '1.15.0'


class Error(Exception): pass

def _safeval(val, quot):
    "return safe value for quoting with quot, which may be single or double quote or blank"
    return quot == " " and val or val.replace(quot, quot+quot)


def CreateBasisVariables(varindex, root, maxvars=None, usevaluelabels=False, macroname=None, order="A",
        labelseparator=" = "):
    """Create a set of dummy variables that span the values of variable with index
    varindex (within any current filter) .  
    
    varindex can be an int or a Variable object (from a VariablDict)
    This function works for numeric and string variables except those with date or time format.  
    The new variables are named root n, starting with n=1 in ascending value order (by default).
    Any existing variables with these names are overwritten.
    Each variable is labeled with the underlying variable name and the value it represents.
    If usevaluelabels is True, the value label, if any, is used in place of the value. Since the new
    label will contain the name of the underlying variable, the underlying label may be truncated.

    Missing values are ignored.
    If maxvars is specified, no more than maxvars will be created.
    The function returns the number of variables created.
    If macroName is specified, an SPSS macro with that name will be
    produced containing the names of the created dummy variables
    omitting root 1 (making the reference category the first one).
    If order="D", the categories are in descending order, and the reference (omitted)
    category will the last one.
    Generated labels have the form variable = value by default.  labelseparator can be used to
      choose a different separator, e.g., labelseparator=": ".
    The function returns the maximum n for the root variables created.
    """
    
    varindex = int(varindex)
    varname = spss.GetVariableName(varindex)
    vartype = spss.GetVariableType(varindex)
    xptail, quot = vartype == 0 and ("@number", " ") or ("@string", "\"")
    xpath ="//pivotTable[@subType='Frequencies']/dimension/group[1]//category/" + xptail
    try:
        tag, ignore = spssaux.CreateXMLOutput("FREQUENCIES " + varname + (order=="D" and "/FORMAT DVALUE" or "") +"/statistics none.")
        freqvalues = spss.EvaluateXPath(tag, '/outputTree',    xpath)
        if maxvars: freqvalues = freqvalues[:maxvars]
        spss.DeleteXPathHandle(tag)
        if len(freqvalues) == 0:
            raise Error, "No variable values found"
        if usevaluelabels:
            vlabels = spssaux.GetValueLabels(varindex)
            for item in vlabels:
                vlabels[item] = vlabels[item].replace('"', '""')    #ensure dbl quoted text can be quoted

        compexpr = "COMPUTE %s_%d = %s EQ " + quot + "%s" + quot + "."
        labelexpr = """VARIABLE LABEL %s_%d "%s%s%s"."""
        genlist = [compexpr%(root, i, varname, _safeval(v, quot)) for i, v in enumerate(freqvalues)]
        if usevaluelabels:
            labellist = [labelexpr%(root, i, varname, labelseparator, vlabels.get(v,v)) for i, v in enumerate(freqvalues)]
        else:          
            labellist = [labelexpr%(root, i, varname, labelseparator, v) for i, v in enumerate(freqvalues)]
        spss.Submit(genlist)
        spss.Submit(labellist)
        
        if macroname:
            spss.SetMacroValue(macroname,
                " ".join([root + '_' + str(i) for i in range(1, len(freqvalues))]))

        return len(freqvalues)
    except:
        print sys.exc_info()
        raise

def CreateFileNameWDate(basename=None):
    """Create a filename, including path, of the form base_datetime.ext
    where datetime is the current date and time in a file system safe format of
    YYYY-MM-DD_HH-MM.
    
    If the basename is not specified, the filename of the active dataset is used.
    If there is none, ValueError is raised.
    If basename already contains a datetime stamp at the end (but before the extension),
    it is removed."""

     # create string with current date and time in format YYYY-MM-DD-HH-MM
    dt = time.strftime("_%Y-%m-%d_%H-%M")
    if not basename:
        basename= spssaux.GetDatasetInfo("Data")
    if not basename:
        raise ValueError("Default name not available")

    root, ext = os.path.splitext(basename)
    # remove datestamp if present
    datestamp = re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\Z",root)
    if datestamp:
        root = root[:datestamp.start()]
    return root + dt + ext
    
def FindMostRecentFile(basename):
    """Return the full filename, including path if included in basename, 
    of the most recent file matching basename or None if there is no match.
    
    Matching means the filename equals the basename with or without a timestamp.
    A timestamp has the format
    _YYYY-MM-DD_HH-MM 
    just before the extension.  
    If the basename already contains a timestamp, it is checked with and without it.
    The timestamp pattern conforms to what CreateFileNameWDate produces.
    """

    # date and time in format YYYY-MM-DD-HH-MM is what would be produced by
    # time.strftime("_%Y-%m-%d_%H-%M")
    
    root, ext = os.path.splitext(basename)
    # remove timestamp if present
    timestamp = re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\Z",root)
    if timestamp:
        root = root[:timestamp.start()]
    candidates = glob.glob(root+"_*"+ext)
        # select only items matching the timestamp pattern, if any
    candidates=[item for item in candidates
        if re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}\Z", 
            os.path.splitext(item)[0])]
    # include original filespec with and without any timestamp if it exists
    # exclude items that are not files
    candidates = \
        filter(os.path.isfile, candidates\
         + filter(os.path.exists, [basename, root+ext]))        
    if not candidates:
        return None
    # find most recent
    candidates = zip(map(os.path.getmtime, candidates),candidates)
    candidates.sort(reverse=True)
    return candidates[0][1]


# Search selected sav files for selected variable names or other variable attributes

def FindFilesWithVars(drivepath="c:/", searchlist=[".*"],infotype='names', filenames=r"*.sav",
  silent=False):
  """Print a report listing files searched and which ones contain all of the
  searchlist items specified.  Returns list of matching files.
  
  drivepath is a location that defines the root of the search (defaults to c:/).
  searchlist is a list of regular expressions of variable information to search for
  (defaults to any, which will list all SPSS data files found).
  infotype is a string that determinesthe type of information to search.  It can be
  names (the default)
  labels
  measurementlevels
  formats
  types (0=numeric, >0 = string of specified length
  filenames is a wildcard expression for filenames to search (defaults to *.sav).
  If silent is True, nothing is printed."""

  infotypes=['names','labels','measurementlevels','formats','types']
  infoapis=[spss.GetVariableName, spss.GetVariableLabel, spss.GetVariableMeasurementLevel,
            spss.GetVariableFormat, spss.GetVariableType]
  
  try:
    infof = infoapis[infotypes.index(infotype)]
  except:
    raise ValueError, "Invalid type of information to search for: "+infotype

  matches = []  
  searchlist = [str(item) for item in searchlist]  
  if not silent:
    print "searching directory tree " + drivepath + " and filenames like " + filenames
    print "for files containing all of the ", infotype+":\n" +\
      "\n".join(searchlist)
  
  searchlistregex = [re.compile(v, re.IGNORECASE) for v in searchlist]
  
  f = os.walk(drivepath)  #create generator function
  for (dirname, subdirs, files) in f:
    for sav in files:
      if fnmatch.fnmatch(sav, filenames):
        if not silent: print "searching: ", dirname + "/"+ sav
        try:
          spss.Submit("get file='"+dirname+"/"+sav+"'")
          savsearchlist=_getinfo(infof)
          if _matchlist(searchlistregex, savsearchlist):
            if not silent: print "***matched:", dirname + "/" + sav
            matches.append(dirname + "/" + sav)
        except:
          pass
  return matches

def _getinfo(f):
  """return a list of variable information of requested type in current data file"""
  kt = spss.GetVariableCount()
  vl = []
  for i in xrange(kt):
    vl.append(str(f(i)))
  return vl


def _matchlist(regex, texts):
  """regex is a list of compiled regular expressions.
  texts is a list of texts.
  matchlist returns True iff all items in regex match some item in texts."""
  
  for x in regex:
    for t in texts:
      if x.match(t):
        break;
    else:
      return False;   #x matches nothing in texts
  return True

def FindEmptyVars(vars=None, delete=False, alpha=True):
    """Scan specified or all variables and determine which are missing or blank for all cases.  
    Return list of names and optionally delete those variables.
    
    vars is a list of the (zero-based) index numbers of the variables to check.
    It can also be a single string of blank-separated numbers or a VariableDict object.  
    By default, all  variables are checked.  
    A value is considered empty if it is sysmis or user missing.
    String variables are also considered empty if their values are all blank.
    delete specifies whether empty variables should be deleted or not.
    The return value is a possibly empty list of variable names, not index numbers.
    Split files should be off when this function is used.
    
    If alpha is False, string variables are excluded from the checked list.  This is true
    even if the variable was listed in the vars parameter.
    
    Examples:
    # find but do not delete the empty variables
    print FindEmptyVars()

    # use a VariableDict object and do the same thing
    vard = spssaux.VariableDict()
    print FindEmptyVars(vars=vard)
    
    # use a string of variable numbers and do the same thing but delete the empty variables
    strvars = []
    for v in vard:
        strvars.append(str(int(v)))
    strvars = " ".join(strvars)
    print FindEmptyVars(vars=strvars, delete=True)
    """
    
    if vars is None:  # check all variables (except as governed by alpha)
        stillstanding = set(xrange(spss.GetVariableCount()))
    else:
        vars = spssaux._buildvarlist(vars)
        stillstanding = set([int(v) for v in vars])   #int ensures that names were not supplied and extracts index from VariableDict objects
    alphavars = set([])
    for v in stillstanding:
        if spss.GetVariableType(v) > 0:
            alphavars.add(v)
    if not alpha:
        stillstanding.difference_update(alphavars)  # remove alpha vars as candidates for deletion if only checking numerics
    curs = spss.Cursor()
    try:
        while True:
            case= curs.fetchone()
            if case is None:
                case = curs.fetchone()   #to allow for split file processing
            if case is None or len(stillstanding) == 0:
                break
            for v in stillstanding.copy():
                if v in alphavars:
                    if not (case[v] == None or case[v].strip() == ""):
                        stillstanding.discard(v)
                else:
                    if not case[v] is None:
                        stillstanding.discard(v)
    finally:
        curs.close()
    
    killlist = [spss.GetVariableName(v) for v in stillstanding]
    if delete and len(killlist) > 0:
        spss.Submit("DELETE VARIABLES " + " ".join(killlist))
    return killlist

def FindEmptyNumericVars(vars=None, delete=False):
    """Scan specified or all numeric variables and determine which are missing for all cases.  
    Return list of names and optionally delete those variables.
    
    vars is a list of the (zero-based) index numbers of the variables to check.
    It can also be a single string of blank-separated numbers or a VariableDict object.  
    By default, all numeric variables are checked.  Any string variables are silently ignored.
    delete specifies whether empty variables should be deleted or not.
    The return value is a possibly empty list of variable names.
    """
    return FindEmptyVars(vars, delete, alpha=False)

def FindUnlabelledValues(vardict):
    """Find all unlabelled values of specified set of variables if the variable has any value labels defined.
    
    Returns a dictionary where keys are variable names and each value is a possibly empty list of values 
    with no label (other than sysmis).
    If there are no variables to check, e.g., because no specified variables have any value labels, an empty
    dictionary is returned.
    vardict is an spssaux VariableDict object specifying the variables to check.
    split files should be off for this function.
    
    This function requires at least version 2.0.2 of spssaux."""
    
    # This function has to do an OMS operation for each variable in order to get the value labels.  This could be slow.
    
    varstocheck = []  # list of variable names
    labelledvalues = []   # list of sets of labelled values
    allvalues = []  # list of sets of values
    
    try:
        for v in vardict:
            lbls = v.ValueLabelsTyped
            if len(lbls) > 0:
                varstocheck.append(v.VariableName)
                labelledvalues.append(set(lbls.keys()))
                allvalues.append(set())
    except AttributeError:
        raise "This function requires at least version 2.0.2 of the spssaux module."
    if varstocheck == []:
        return {}
    
    try:
        curs = spssdata.Spssdata(indexes = varstocheck, names=False)
        for case in curs:
            for i, val in enumerate(case):
                if not val is None:
                    allvalues[i].add(val)
    finally:
        curs.CClose()
    
    # construct list of unlabelled values
    unlabelled = {}
    for i in xrange(len(varstocheck)):
        unlabelled[varstocheck.pop()] = list(allvalues.pop() - labelledvalues.pop())
    return unlabelled


import operator, spss, spssaux, spssdata

def genCategoryList(varnames, specialvalues=None, macroname=None, missing='EXCLUDE', order='D', weightvar=None):
    """Generate and return sorted list(s) of values with possible insertion of extra values.  Optionally create SPSS macros.
    
    varnames is a sequence of variable names to process.  It can also be a blank-separated string of variable names.
    specialvalues is a sequence of values that should be inserted before the first zero count or at the end if no zeros or None.
    If a special value already occurs in a varname, it will be moved.
    Note that for string variables, special values need to have the same width as the variable, including leading and trailing blanks.
    macroname is a list of macronames of the same length as varnames to generate or None.
    missing is 'INCLUDE' or 'EXCLUDE' to determine whether user missing values are included or excluded.
    order is 'A' or 'D' to specify the sort direction.
    weightvar can be specified as a variable name to be used as a weight in determing the counts to sort by.  It must not occur in varnames.

    This function is mainly useful as a helper function for Ctables in building CATEGORIES subcommands.
    It may be useful to combine it with OTHERNM and/or MISSING in the category list.
    """
    
    varnames = spssaux._buildvarlist(varnames)
    if macroname:
        macroname = spssaux._buildvarlist(macroname)
        if len(varnames) != len(macroname):
            raise ValueError, "Number of variables does not match number of macro names"
    if not missing in ['INCLUDE','EXCLUDE']:
        raise ValueError, "missing specification must be 'INCLUDE' or 'EXCLUDE'"
    
    if weightvar:
        #if weightvar in varnames:
        #    raise ValueError, "weightvar cannot be included in varnames"
        varnamesAndWeight = varnames + [weightvar]
    else:
        varnamesAndWeight = varnames
    curs = spssdata.Spssdata(indexes=varnamesAndWeight, names=False, convertUserMissing= missing=='INCLUDE')
    nvar = len(varnames)
    
    vvalues=[{} for i in range(nvar)]  # for accumulating counts for all variable values
    for cn, case in enumerate(curs):
        casecpy = copy.copy(case)
        if weightvar:
            w = casecpy[nvar]
            if w is None:
                w = 0.0
        else:
            w = 1.0
        for i in range(nvar):
            if not casecpy[i] is None:   # omit sysmis values and optionally user missing values
                curval = casecpy[i]
                vvalues[i][curval] = vvalues[i].get(curval,0.) + w   # count occurrences, possibly weighted
    curs.CClose()
    
    valuelist = []
    for i in range(nvar):
        if not specialvalues is None:  # remove special values from count list
            for v in specialvalues:
                if v in vvalues[i]:
                    del(vvalues[i][v])
        valuelist.append(sorted([(value, key) for (key, value) in vvalues[i].iteritems()], reverse = order == 'D'))
        if not specialvalues is None:
            for j in range(len(valuelist[i])):
                if valuelist[i][j][0] == 0:
                    valuelist[i] = valuelist[i][:j] + [(None, v) for v in specialvalues] + valuelist[i][j:]
                    break
            else:
                valuelist[i].extend([(None, v) for v in specialvalues])
        if macroname:
            if isinstance(valuelist[i][0][1], basestring):
                qchar = '"'
            else:
                qchar = ''
            spss.SetMacroValue("!" + macroname[i], " ".join([qchar + str(k) + qchar  for (value, k) in valuelist[i]]))
    return valuelist

# get a variable specification
# get value labels
# accept list of values for subtotals
# generate category list for /category
# save that as a macro


# Construct sorted variable lists for use in CTABLES or other procedures
# Usage example:
# genSortedVariableExpr("x y z", "!sortedxyz")
# Then, outside the program,
# CTABLES /TABLE=!sortedxyz.
# The subtables will be ordered in descending order of the variable means.

def genSortedVariableExpr(varnames, macroname, stat='mean', order='D', ctables=True, numvars=None):
    """Create macro with table expression for the variables in varnames sortd by a statistic and return list.
    
    varnames is a sequence of variable names to process.
    macroname is the name for the macro to hold the resulting table expression.
    stat specifies the ordering statistic: mean, count, or sum.
    order is 'A' or 'D' for the sort order.
    if ctables, a Ctables expression is generated for the macro; otherwise it is a blank-separated string.
    If numvars is None, the default, all varnames are returned in order.  If it is a positive integer, n, only
    the first n variables are returned after sorting.  If it is negative, the last n variables are returned.
    numvars thus interacts with the sort order
    User missing values are always excluded"""
    
    #TODO: argument checking
    stat = stat.lower()
    order = order.lower()
    if not stat in ['count', 'mean', 'sum']:
        raise ValueError("Sorting statistics must be mean, sum, or count")
    if not order in ['a', 'd']:
        raise ValueError("Sort order must be 'a' or 'd'")
    if ctables:
        joinchr = "+"
    else:
        joinchr = " "
    varnames = spssaux._buildvarlist(varnames)
    nvar = len(varnames)
    wtvar = spss.GetWeightVar()
    if not wtvar is None:
        varnames.append(wtvar)

    # accumulate counts and sums over case data

    varstats = dict([[i, [0,0]] for i in range(nvar)])
    curs = spssdata.Spssdata(varnames, names=False)
    for case in curs:
        for i in range(nvar):
            if wtvar:
                wt = case[-1]
            else:
                wt = 1.
            if not case[i] is None:   # exclude missing values
                varstats[i][0] = varstats[i][0] + wt
                varstats[i][1] = varstats[i][1] + case[i] * wt
    curs.CClose()
    
    if stat == 'count':
        sdata = [varstats[i][0] for i in range(nvar)]
    elif stat == 'sum':
        sdata = [varstats[i][1] for i in range(nvar)]
    else:
        sdata = []
        for i in range(nvar):
            if varstats[i][0] > 0:
                sdata.append(varstats[i][1] / varstats[i][0])
            else:
                sdata.append(-1e100)
    pairs = sorted(zip(sdata, varnames), reverse = order == 'd')
    if numvars > 0:   # first n
        pairs = pairs[:numvars]
    elif numvars < 0 and numvars is not None:  # last n
        pairs = pairs[len(pairs) + numvars:]
    tblexpr = joinchr.join([v for (s, v) in pairs])
    spss.SetMacroValue(macroname, tblexpr)
    return tblexpr

def genCategoriesWSubtotals(varname, subtotallist, macroname, subtotallabel="", specificlabels={}, sort='values', order='a', position='after'):
    """Define a macro for CTABLES containing all labelled categories with inserted subtotal specifications and return the macro value.
    
    This function generates a category list based on value labels with regular and hiding subtotal specifications at selected points.  
    It is useful for tables where a subtotal should not include all the categories preceding (or following) it since the previous subtotal.
    Note that with such subtotals, it is important to supply a clear label so that the table is not misleading.
    
    varname is the variable name whose labels will be used.  It is assumed to be numeric.
    subtotallist is a sequence of values of the appropriate type that should be followed by a subtotal.
    The subtotal will be a regular subtotal except when there is only one value being subtotaled, in which case it will
    be a hiding subtotal and the label will be the category label regardless of other settings below.
    macroname is the name of the macro to generate.
    If a subtotal label should be specific to the value in subtotallist, include it in a dictionary as specificlabels where the
    keys are the values of the appropriate type and the values are the specific label.  The subtotallabel or default will be used when
    there is no specific label.  If a specific label is given but the value is not in the subtotal list, it is ignored.
    If subtotallabel is specified, non-hiding subtotals will be labelled with that string 
    By default, the categories are sorted by the category values.  If sort is  'labels', the categories are sorted by
    the value label.
    order='a' or 'd' can be used to control the direction of the sort.
    If position is 'after' the category list is set for following subtotals; if 'before', it is set for preceding subtotals.
    #TODO: make this happen.
    
    If there is only one category in a subtotal, make it a hiding subtotal and use the category label as the subtotal label.

    Examples:
    genCategoriesWSubtotals("education", [12,16,20], '!categories')
    genCategoriesWSubtotals("education", [12,13, 16,20], "!categoriesSpLabels", subtotallabel="Together", 
      specificlabels={13:"thirteen", 16:"sixteen"})
    
    """
    
    if  sort not in ['values','labels'] or order not in ['a','d'] or position not in ['after','before']:
        raise ValueError("invalid value for function parameter")
    
    if ok1600 and spss.PyInvokeSpss.IsUTF8mode():
        unistr = unicode
    else:
        unistr = str
        
    catlist = []
    catcount = 0
    # addt will either append to catlist or insert at the beginning
    if position == "after":
        def addt(x):
            catlist.append(x)
    else:
        def addt(x):
            catlist.insert(0,x)
    
    vardict = spssaux.VariableDict(namelist=varname)
    isstr = vardict[0].VariableType
    vallabeldict = vardict[0].ValueLabels
    # get list of labeled values and convert to appropriate type so that they will sort correctly according to the type
    if isstr:
        vallabels = [v for v in vallabeldict]
    else:
        vallabels = [int(v) for v in vallabeldict]
    if sort == 'values':
        values = sorted(vallabels, reverse= order=='D')
    else:
        values = sorted(vallabels, key= lambda k: vallabeldict[unistr(k)], reverse=order=='D')
 
    for v in values:
        if isstr:
            addt(_smartquote(v))
        else:
            addt(unistr(v))
        catcount = catcount + 1
        if v in subtotallist:
            if catcount == 1:
                addt('HSUBTOTAL="%s"' % vallabeldict[unistr(v)])
                catcount = 0
            else:
                stlabel = _smartquote(specificlabels.get(v, subtotallabel))
                if stlabel != '""':
                    stlabel = "=" + stlabel
                else:
                    stlabel = ""
                addt("SUBTOTAL" + stlabel)
                catcount = 0
    spss.SetMacroValue(macroname, " ".join(catlist))
    return catlist
  
def copyValueSubsets(fromvar, tovars, duplelist, vardict=None, createVars=True):
    """Copy value labels and optionally values from fromvar to tovars according to partition in duplelist.
    
    This function is useful in adding flexibility to Ctables.
    It maps the values and value labels from one variable into a set of variables with each variable receiving the value
    labels, and optionally the values, in a selected range.  It can create the set of variables or it can just apply the
    value labels.
    
    fromvar is the source variable.
    tovars is a sequence of one or more variables or a simple, blank-separated string listing the variables.
    Variables in tovars are assumed to have the same variable type as fromvar.
    duplelist is a list of pairs of values, one pair per variable in tovars, specifying the range of values whose labels
    and optionally values should be copied.  Values in duplelist must match the type of fromvar.
    Both endpoints are included.
    Existing value labels for tovars are replaced.
    If vardict is not None, it is a VariableDict object containing fromvar.  If not supplied, one is created.
    if createVars is true, the variables listed in tovars are created according to the specifications in duplelist.  They must
    not already exist, and the measurement level is copied from fromvar.  Cases where the values are outside the
    selected range for a variable will have sysmis values.
    
    Examples:
    copy values and value labels from variable educ into educ1, educ2, educ3.  educ1 will contain values and labels
    in the inclusive range 0, 10, educ2 will include the range 0,14, and educ3 will have 12,16
    Usually the ranges will partition the values, but overlaps and omissions are permitted.
    copyValueSubsets("educ", "educ1 educ2 educ3", [(0,12), (13,16), (17,99)])
    
    copy values and labels and create overlapping totals in Ctables:
    The table will tabulate educ with jobcat.  It will have totals for each educ range and an overlapping total for the range 0,16
    and a grand total.
    
    copyValueSubsets("educ", "educ1 educ2 educ3", [(0,12), (13,16), (17,99)])
    spss.Submit("IF NVALID(educ1, educ2) > 0 educ12 = 1")
    spss.Submit("COMPUTE grand = 1")
    spss.Submit("ctables /table (educ1+educ2 + educ12 + educ3 + grand)[C] BY jobcat/categories variables=educ1 educ2 educ3 total=yes.")
    """
    
    tovars = spssaux._buildvarlist(tovars)
    if not len(tovars) == len(duplelist):
        raise ValueError("The number of range duples is different from the number of target variables")
    if not vardict:
        vardict = spssaux.VariableDict(namelist=fromvar)
    isstrvar = vardict[0].VariableType > 0
    fromvarvl = vardict[fromvar].ValueLabels
    if createVars and isstrvar:
        spss.Submit("STRING %s (%s)" % (" ".join(tovars), vardict[fromvar].VariableFormat))

    for i, v in enumerate(tovars):
        lolim, hilim = duplelist[i]
        vn = tovars[i]
        if isstrvar:
            lowfmt, hifmt = _smartquote(lolim), _smartquote(hilim)
            values = [v for v in fromvarvl if lolim <= v <= hilim]
            vlspec = [_smartquote(v) + " " + _smartquote(fromvarvl[v]) for v in values]
        else:
            lowfmt, hifmt = lolim, hilim
            values = [v for v in fromvarvl if lolim <= float(v) <= hilim]
            vlspec = [v + " " + _smartquote(fromvarvl[v]) for v in values]
        if createVars:
            spss.Submit("IF %(fromvar)s  >= %(lowfmt)s AND %(fromvar)s <= %(hifmt)s  %(vn)s = %(fromvar)s." % locals())
        spss.Submit("VALUE LABELS %s " % vn + " ".join(vlspec))
    if createVars:
        spss.Submit("VARIABLE LEVEL %s (%s)" % (" ".join(tovars), vardict[fromvar].VariableLevel))


def rankvarsincase(varlist, suffix="_rank"):
    """create a set of new variables with values matching the rank of variables in varlist.
    
    This function requires SPSS 15 or later.
    
    varlist is a list, string or variable dictionary of the variables to sort.
    suffix is a string to append to the names in varlist for the new variables.  If the new names
    match an existing variable, an exception will be raised.  Default value is "_rank" 
    
    Missing values are ranked low."""
    
    varlist = spssaux._buildvarlist(varlist)
    indexes = range(len(varlist))
    curs = spssdata.Spssdata(indexes=varlist, accessType='w', names=False, maxaddbuffer = 8 * len(varlist))
    try:
        for v in varlist:
            curs.append(spssdata.vdef(v + suffix, vlabel="Rank for " + v, vfmt=("F", 4, 0)))
        curs.commitdict()
        
        for case in curs:
            curs.casevalues([i for (val, i) in sorted(zip(case, indexes))])
    finally:
        curs.CClose()


# match files based on variable labels

import spss, spssaux    
def mergeByLabel(firstds, secondds):
    """Merge cases from two open datasets renaming the variables in secondds according to
    the variable labels in firstds to have the firstds names.

    Unlabeled variables are not renamed.
    If secondds has a duplicate label and firstds contains that label, the renaming would be ambiguous, so the variable is not renamed.
    No check is made for variable type compatibility.
    
    If renaming would create duplicate variable names, a ValueError exception is raised.  
    This could be caused by ambiguity or partial labelling."""
    
    spss.Submit("DATASET ACTIVATE %s" % secondds)
    vardict2 = spssaux.VariableDict()
    labeldict2 = {}
    for v in vardict2:
        vl = v.VariableLabel
        if vl != '':
            if not vl in labeldict2:
                labeldict2[vl] = [v.VariableName, 1]
            else:
                labeldict2[vl][1] = labeldict2[vl][1]+1

    spss.Submit("DATASET ACTIVATE %s" % firstds)
    labeldict1 = dict([(item.VariableLabel, item.VariableName) for item in spssaux.VariableDict()])
    try:
        del labeldict1[""]
    except:
        pass
    for item in labeldict1:
        varcount = labeldict2.get(item, ['',1])[1]
        if  varcount > 1:  #multiple variables share same label
            print "label assigned to %d variables in second dataset.  Renaming will not occur: '%s'" % (varcount, item)
            del labeldict2[item]
    
    renamein = []
    renameout = []
    for (label, name) in labeldict1.items():
        if not label in labeldict2:
            print "Variable label not found in second dataset or duplicate label.  Variable will not be renamed:", name, label
        elif name in renameout:
            print "Variable label not unique in second file:", name, label
        elif name != labeldict2[label][0]:
            renamein.append(labeldict2[label][0])
            renameout.append(name)

    # check for duplicate names and fail if any found
    unrenamed = set(vardict2.variables) - set(renamein)
    dups = unrenamed.intersection(set(renameout))
    if len(dups) > 0:
        print "Merge stopped: Renaming would create the following duplicate names:\n", "\n".join(sorted(dups))
        raise ValueError, "Duplicate Names"

    if len(renamein) > 0:
        renamesubcmd = "/RENAME=(" + " ".join(renamein) + "=" + " ".join(renameout) + ")"
        print "\nRename mapping for dataset %s:" % secondds
        for inname, outname in zip(renamein, renameout):
            print inname, "-->", outname
    else:
        renamesubcmd = ""

    cmd = r"""ADD FILES /FILE=*
    /FILE='%(secondds)s'
    %(renamesubcmd)s.""" % locals()
    spss.Submit([cmd, "EXECUTE."])


def dupVarnameCheck(vardict, vlist):
    """Check the variable list in vlist for duplicates against the VariableDict object vardict.
    Return a duple of a list of duplicates and the expanded list.
    
    TO constructs are resolved against the variable dictionary.
    Case is ignored in these checks.
    
    The expanded list is a list containing individual items and lists where TO was used.
    Duplicates are not removed from the expanded list in order to facilitate finding the source.
    
    vardict is a VariableDict object to be used for expanding TO constructs.
    vlist is the variable list to be checked as a sequence or a string.
    
    If a name is not found in the dictionary, an exception is raised.
    """
    
    vlist = spssaux._buildvarlist(vlist)
    varset = set()
    size = len(vlist)
    dups = []
    variables = vardict.variables
    variablesUC = [v.upper() for v in variables]
    expandedlist = []
    
    def fixcase(vname):
        """closure to correct case of variable vname against a dictionary variable list variables.  Return the corrected name"""

        if vname in variables:
            return vname
        else:
            for i, vv in enumerate(variablesUC):
                if vname.upper() == vv:
                    return variables[i]
            raise ValueError("No such variable: " + vname) 
    
    for i, v in enumerate(vlist):
        if i < size - 1 and vlist[i+1].upper() == "TO":
            varlist = vardict.range(fixcase(v), fixcase(vlist[i+2]))
            expandedlist.append("[" + ", ".join(varlist) + "]")
            for vv in varlist:
                if vv.upper()  in varset:
                    dups.append([vv, [v, vlist[i+1], vlist[i+2]]])
                else:
                    varset.add(vv.upper())
            vlist[i+1] = ""
            vlist[i+2] = ""
        elif not v == "":
            expandedlist.append(fixcase(v))
            if v.upper() in varset:
                dups.append(v)
            else:
                varset.add(v.upper())
    return (dups, expandedlist)

def getVarValues(varname, vartype=None, missing='exclude', labels=False):
    """Return a list of the values of variable varname and optionally a value labels dictionary.
    
    varname is the variable to tabulate.  The name must match the case of the name in SPSS.
    vartype is the variable type: 0 for numeric and >0 for string. If not supplied, it will be determined by this function.
    By default, user missing values are excluded.  Specify missing="include" to include them.
    System-missing values are never included
    
    If labels is True, the return is a frequencies list and a value labels dictionary with string values as keys
    followed by the variable label."""
    

    if not missing in ["include", "exclude"]:
        raise ValueError, "Missing-value specification must be include or exclude"
    if vartype is None:
        vartype = spssaux.VariableDict(namelist=varname)[varname].VariableType
    xptail, quot = vartype == 0 and ("@number", " ") or ("@string", "\"")
    xpath ="//pivotTable[@subType='Frequencies']/dimension/group[1]//category/" + xptail
    labelspath = "//pivotTable[@subType='Frequencies']/dimension/group[1]//category[@label]/@*"
    cmd = "FREQUENCIES " + varname  +"/statistics none"
    if missing == "include":
        cmd += "/MISSING=INCLUDE"
    tag, ignore = spssaux.CreateXMLOutput(cmd)
    freqvalues = spss.EvaluateXPath(tag, '/outputTree',    xpath)
    if labels:
        varlabel = spss.EvaluateXPath(tag, 'outputTree', "//pivotTable[@subType='Frequencies']/@label")
        if len(varlabel) > 0:
            varlabel = varlabel[0]
        else:
            varlabel = ""
        lbv = spss.EvaluateXPath(tag, 'outputTree', labelspath)
    spss.DeleteXPathHandle(tag)
    if not labels:
        return freqvalues
    else:
        lbv = dict([(lbv[i], lbv[i-1]) for i in range(1, len(lbv), 4)])
        
        return freqvalues, lbv, varlabel

def generalizedSplit(splitvar, cmd, vartype=None, missing="exclude", errorContinue=True):
    """Execute cmd for cases having each value of splitvar and return error count.
    
    splitvar is a string or numeric SPSS variable.  For each value of splitvar, the SPSS command in cmd
    is executed for those cases matching that value.  Although any variable can be specified, the nature
    of floating point processing means that numeric variables should have only integer values.
    It is not necessary that the file be sorted by splitvar.
    The variable named as splitvar must match the name of an SPSS variable including its letter case.
    
    cmd is the SPSS command to execute.  Within that command, the current value of splitvar can be
    used by including %(splitvalue)format-code in the string.  The command can also use %(count)format-code
    to refer to a counter with value of the current iteration.  count is zero-based.
    
    For example, cmd could be
    SAVE OUTFILE="c:/temp/output%(splitvalue)d.sav"
    to include the current integer-valued value of the numeric split variable in the filename or
    SAVE OUTFILE="c:/temp/output%(count)d.sav"
    to number the output files starting from zero.
    Any format codes can be used, but d for a numeric variable and s for a string variable are likely to be the most useful.
    
    vartype is optional but can be used to specify the type of the SPSS variable.  0 indicates a numeric variable, and values
    greater than 0 indicate a string.  If not specified, the type will be determined automatically.
    
    By default, user and system missing values are excluded from the iterations.  Specify
    missing='include' to include user missing values.  System-missing values are always excluded.
    
    errorContinue indicates whether the iterations through the values of splitvar should continue or stop if an error
    occurs.  By default, iterations continue.  Specify errorContinue=False to stop on error.
    
    The function returns a count of the errors.  If errorContinue=False, this value will always be 0 or 1.
    
    While this function is more general than the built-in split files mechanism, when split files can be used, that mechanism
    may be faster.
    split files requires a sort (n log n time) but then only one data pass for a command, and the sort may be amortized over 
    many commands.
    This function does not require a sort but makes K+1 data passes, where K is the number of distinct values of the
    splitting variable.
    """
    
    if vartype is None:
        vartype = spssaux.VariableDict(namelist=splitvar)[splitvar].VariableType
    varvalues, valuelabels, varlabel = getVarValues(splitvar, vartype, missing, labels=True)
    if varlabel == "":
        varlabel = splitvar
    cmdprefix="""TEMPORARY.
SELECT IF %(splitvar)s = %(splitvalue)s.
    """
    errcount = 0
    count = -1
    
    for splitvaluestr in varvalues:
        count += 1
        try:
            splitvalue = float(splitvaluestr)
        except:
            splitvalue = spssaux._smartquote(splitvaluestr)
        try:
            print "SPLIT: %s = %s" % (varlabel, valuelabels.get(splitvaluestr, splitvaluestr))
            spss.Submit((cmdprefix + cmd) % {"splitvar": splitvar, 
                "splitvalue": splitvalue,  
                "count":count})
        except:
            errcount += 1
            if errorContinue:
                continue
            else:
                return errcount
    return errcount
    
    
def genValueLabels(targetvar, labelvar, vardict=None):
    """Generate value labels for targetvar from contents of labelvar.  Return conflict state.
    
    targetvar is any existing variable.
    labelvar is a variable whose values should be used to label the values of targetvar.
    vardict is an optional spssaux.VariableDict object containing at least targetvar.
    If there are conflicting values, the last one encountered wins.
    If there are no conflicts, return value is True; if any conflicts, value is False
    System missing values are not labeled."""
    
    labels = {}
    noConflicts = True
    if vardict is None:
        vardict = spssaux.VariableDict(targetvar)
    curs = spssdata.Spssdata([targetvar, labelvar])
    for case in curs:
        val = u(case[0])
        label = u(case[1]).strip()
        if not val is None:
            if val in labels and not label == labels[val]:
                noConflicts = False
            labels[val] = label
    curs.CClose()
    vardict[targetvar].ValueLabels = labels
    return noConflicts

def tallydates(startvar, endvar, startdate, enddate, dsname, interval=86400, initial=0, 
        startmissing="exclude", othervars=None, otherfuncs=None):
    """Construct a dataset whose cases are counts for each date in an interval at specified frequency
    
    startvar and endvar are variable names for the start and end of a date/time interval
    startdate and end date are SPSS date values for the beginning and end of the interval to tabulate
    interval is the frequency at which the date is tabulated, defaulting to one day (=86400 seconds)
    initial is the initial count at startdate.
    
    If startvar is missing, it is assumed to be before the beginning of the period,
    so the count will not be incremented unless startmissing = "include".  Include might be needed with
    the extra functions.
    If endvar is missing, it is assumed to be after the end of the period, so the count will not exclude the case.
    dsname is the name for a new dataset not currently defined.
    Note that if the active dataset is unnamed, creating the new dataset will close it.
    
    othervars is an optional list or string of other variables in the dataset that should be made available for
    calculation.  It is only useful if using otherfuncs.
    
    otherfuncs is an optional list of functions that will be called for each case and date if the date is within the
    start and end dates for teh case.  Each function will be
    passed a list of the case values.  Items 0 and 1 will be the start and end dates.  Other items will be the
    variables in othervars.  The return values for each function are summed, and results in a variable
    in the output dataset with the same name as the function, so function names must be legal as SPSS variable
    names.  Do not use "tallydate" or "count", as these variables will be created from the basic information.
    
    Functions must return numeric values.  Strings or missing codes will cause a failure.  To calculate, say,
    an average when there are missing data on the variable being accumulated, count the nonmissing values
    with another function and use that count for the final result.
    
    Each date between startdate and enddate will appear in the new dataset.
    
    Example.  The input dataset has variables indate, outdate, age, and income.
        # starting Jan 1, 1990, ending Dec 31, 2008
    def ages(case):         # age has no missing data
        return case[2]
        
    def incomes(case):
        if case[3] is None:   #missing value
            return 0
        else:
            return case[3]
            
    def nmincomes(case):  # count nonmissing values
        if case[3] is None:
            return 0
        else:
            return 1

    tallydates(startvar="indate", endvar="outdate", startdate=12850531200, enddate=13450060800, dsname="tally",
        othervars="age income", otherfuncs=[ages, incomes, nmincomes])
    spss.Submit(r'''COMPUTE averageAge = ages/count.
    COMPUTE averageIncome = incomes/nmincomes.''')
"""
    
    if othervars is None:
        othervars = []
    othervars = spssaux._buildvarlist(othervars)
    if otherfuncs is None:
        otherfuncs = []
    varlist = [startvar, endvar] + othervars
    curs = spssdata.Spssdata(indexes=varlist, names=False)
    datecounts = {}
    funcoutputs = {}
    numfuncs = len(otherfuncs)
    for f in otherfuncs:
        if not callable(f):
            raise ValueError("A value for otherfuncs is not a callable function: %s" % f.func_name)
    if not startmissing in ["include", "exclude"]:
        raise ValueError("""startmissing must be "include" or "exclude".""")
    includestartmissing = startmissing == "include"
    
    for case in curs:
        case = list(case)
        for d in range(startdate, enddate, interval):
            if case[0] is None:
                if includestartmissing:
                    case[0] = startdate
                else:
                    case[0] = enddate+1
            if case[1] is None:
                case[1] = enddate+1
            if case[0] <= d <= case[1]:
                datecounts[d] = datecounts.get(d, initial) + 1
                # if there are supplementary functions
                #  get the values for the current date
                #  call each function passing in the current case
                #  add the result to each component
                #  store back in the date value
                if numfuncs:
                    funcvalues = funcoutputs.get(d, numfuncs * [0])
                    for i, f in enumerate(otherfuncs):
                        funcvalues[i] += otherfuncs[i](case)
                    funcoutputs[d] = funcvalues
    curs.CClose()
    
    curs = spssdata.Spssdata(accessType="n")
    curs.append(spssdata.vdef("tallydate", vfmt=("DATE", 20)))
    curs.append("count")
    for f in otherfuncs:
        curs.append(f.func_name)
    curs.commitdict()
    for date, count in datecounts.items():
        curs.appendvalue("tallydate", date)
        curs.appendvalue("count", count)
        if numfuncs:
            fvalues = funcoutputs[date]
            for i, f in enumerate(otherfuncs):
                curs.appendvalue(f.func_name, fvalues[i])
        curs.CommitCase()
    curs.CClose()
    spss.Submit(r"""DATASET NAME %s.
    SORT CASES BY tallydate.""" % dsname)

def getMRSetNames(tag):
    """Return a possibly empty list of names of multiple response sets.
    
    tag is the xmlworkspace tag for an object created by spss.CreateXPathDictionary"""
    
    return spss.EvaluateXPath(tag, "/dictionary", r"""//multipleResponseSet/@name""")


def getMRSetInfo(tag, setname):
    """Return information about a multiple response set.
    
    tag is the xmlworkspace tag for an object created by spss.CreateXPathDictionary
    setname is the case-matching name of the MR set to query.
    If tag or setname is not found, an exception is raised.
    
    The return value is a list with these elements
    0: label of the set
    1: the dichotomy value.  ="" if not an multiple dichotomy set.
    2: a list of the elementary variables in the set."""
    
    xpathbase = r"""//multipleResponseSet[@name = "%s"]""" % setname
    xpath = r"""/multipleResponseSetVariable/@name"""
    ret = []
    ret.extend(spss.EvaluateXPath(tag, "/dictionary", xpathbase + "/multipleResponseSetLabel/@value"))
    ret.extend(spss.EvaluateXPath(tag, "/dictionary", xpathbase + "/multipleResponseSetDichotomy/@value"))
    ret.extend(spss.EvaluateXPath(tag, "/dictionary", xpathbase + "/multipleResponseSetVariable/@name"""))
    return ret


def ntiler(varname,  bandname, dsname, n=10, labeldecimals=0, aggregatename=None):
    """Calculate and carry out a recode dividing the sums of a variable into approximately equal ntiles
    
    varname is the variable to analyze.  Must be numeric.  Values are expected to be nonnegative.
    bandname is the name of the variable to create.  Its values will be integers 1,...n
    representing the ntile.  The sum of the case values of varname for each value of
    bandname will be approximately equal.  The interval for each band is left open, right closed.
    n, default 10, is the number of intervals to create.
    labeldecimals, default 0, specifies the number of decimal places for the value labels.
    aggregatename can be specified as a dataset name.  If given, the aggregated dataset, which
    hold the sum of values for each distinct value, is retained.  Otherwise it is closed.
    
    The algorithm allocates all occurences of a value to a single band rather than splitting equal values
    across bands in order to smooth out the sums.  When the cumulative sum crosses a boundary, that value
    is placed in the next bin if it exceeds the bound by more than half; otherwise it is placed in the previous bin.
    
    The sum in each band will not always be the same, and it can cause fewer bands than requested with certain data.  
    Consider the following data.
    1
    1
    2
    2
    3
    3
    4
    4
    5
    5
    and a request for five bands.  With a sum of 30, each band should sum to 6, which is not possible.  In this case,
    the resulting sums will be 6, 6, 8, and 10, and there will be only four bands.
    """
    
    if aggregatename:
        work=aggregatename
    else:
        work = "A" + str(random.random())
    spss.Submit(r"""DATASET DECLARE %(work)s.
    AGGREGATE
      /OUTFILE='%(work)s'
      /BREAK=%(varname)s
      /sum=SUM(%(varname)s).
    dataset activate %(work)s.""" % locals())
    
    curs = spssdata.Spssdata(omitmissing=True, names=False)
    data = curs.fetchall()
    curs.CClose()
    if not aggregatename:
        spss.Submit("DATASET CLOSE " + work)
    band = sum([item[1] for item in data])/n
    b = band
    cumsum = 0.
    breakvalue = []
    prevvalue = 0
    for case in data:
        cumsum += case[1]
        if cumsum >= b:
            if (cumsum - b) > case[1]/2.:
                breakvalue.append(prevvalue)
                cumsum = case[1]
            else:
                breakvalue.append(case[0])
                cumsum = 0.
        prevvalue = case[0]
    
    if len(breakvalue) < n and cumsum > 0.:
        breakvalue.append(case[0])
    lastvalue = breakvalue[-1]
    breakvalue[-1] = "HI"
    
    segments = ["(LO THRU " + str(x) + "=" + str(i+1)+")" 
        for i, x in enumerate(breakvalue)]
    cmd = "recode " + varname + " " + " ".join(segments) + " INTO %(bandname)s" % locals()
    breakvalue[-1] = lastvalue
    
    spss.Submit("DATASET ACTIVATE " + dsname)
    spss.Submit(cmd)
    spss.Submit("VARIABLE LEVEL %(bandname)s (ORDINAL)" % locals())
    labels = [("Low   ", "%.*f" % (labeldecimals, breakvalue[0]))]
    for i in range(1, len(breakvalue)):
        labels.append(("%.*f" % (labeldecimals, breakvalue[i-1]), "%.*f" % (labeldecimals, breakvalue[i])))
    
    valuelabels = [str(i+1) + ' "' + item[0] + " - " + item[1] + '"' for (i, item) in enumerate(labels)]
    spss.Submit("VALUE LABELS " + bandname + " " + " ".join(valuelabels))
    return breakvalue

# macrosFromData creates one or more macro definitions from a dataset

def setMacrosFromData(key, value, select=None, omit=None, printdef=False):
    """Create macros from variables in the active dataset
    
    key is a string variable name that defines the name of the macro. 
    ! will be prefixed to the name.
    value is a string or numeric value that defines the value of the macro.
    If select is given, it is a value or sequence of values that specify which key[s]
    should be used to define macros.  If a key is listed in select but not found
    in the dataset, an exception is raised.
    If omit is given, it is a value or sequence of values that should be omitted when
    defining macros.
    if printdef, keys are values are printed.
    
    Blank keys are always ignored, but an invalid name in the key field will raise an exception.
    A missing value in the value will cause the macro not to be defined.
    Keys are not case sensitive."""
    
    data = spssdata.Spssdata([key, value]).fetchall()
    if not select is None:
        select = set((item.lower() for item in spssaux._listify(select)))
        selecting = True
    else:
        select = set()
        selecting = False
    if not omit is None:
        omit = set((item.lower() for item in spssaux._listify(omit)))
    else:
        omit = set()
    select = select - omit        # omit dominates select
    for k, v in data:
        try:
            k = k.strip()
            k1 = k.lower()
            if k1 == "" or k1 in omit or v is None:
                continue
            if selecting and not k1 in select:
                continue
        except:
            pass
        try:
            if k.find(" ") > 0:
                raise ValueError("macro names cannot contain blanks: " + k)
            if printdef:
                print k, ": ", v
            spss.SetMacroValue("!" + k, v)
            select.discard(k1)
        except spss.SpssError:
            raise ValueError("Could not define macro: " + k)
    if len(select) > 0:
        raise ValueError("Selected name(s) were not found in the dataset:\n" + ", ".join(select)) 
    
def getRole(varlist=""):
    """Return a dictionary of role settings for varlist
    
    varlist is a list of variables.  If not specified, roles for all variables are returned.
    
    The dictionary keys are the variable names lower cased.  They will be in 
    code page or Unicode depending on the Statistics mode.
    Role values are in lower case and in English.
    
    If the Statistics version is prior to 18, an exception will be raised."""
    
    if not ok1800:
        raise AttributeError("getRole api is not available prior to version 18")
    
    if varlist:
        varlist = "/VARIABLES=" + " ".join(varlist)
    spss.Submit(["PRESERVE.", "SET OLANG=ENGLISH."])
    tag, errlevel = spssaux.CreateXMLOutput("DISPLAY DICTIONARY " + varlist, 
        omsid='File Information')
    spss.Submit("RESTORE")
    if errlevel:
        raise ValueError("Invalid variable specification in getRole")
    
    variables =spss.EvaluateXPath(tag, "/",
        """//pivotTable[@subType="Variable Information"]/dimension/category/@varName""")
    rolelist = spss.EvaluateXPath(tag, "/",
        """//pivotTable[@subType="Variable Information"]/dimension/category/dimension/category[position() = 4]/cell/@text""")
    spss.DeleteXPathHandle(tag)
    variables = [v.lower() for v in variables]
    rolelist = [v.lower() for v in rolelist]
    return dict(zip(variables, rolelist))
    

# generate data for the variable dictionary in the active dataset

def generateData(cases=1000):
    """Generate and append cases for the current active dataset
    
    cases is the number of cases to append.  Default is 1000
    Values are random.  If numeric with zero decimals, small integers
    are generated.  Other numeric are random normals.  Dates are
    centered around 1/1/2000.  Strings are random characters."""
    
    vardict = spssaux.VariableDict()
    numvar = vardict.VariableCount()
    if numvar == 0:
        raise ValueError("The active dataset has no variables")
    vartype = []
    varformat = []
    for i in range(numvar):
        vartype.append(vardict[i].VariableType)  # numeric type code
        varformat.append(vardict[i].VariableFormat) # e.g., F8.2, A10, F4
    vgen = Vgenerator(vartype, varformat)
    curs = spssdata.Spssdata(names=False, accessType="a")
    for c in range(cases):
        for v in range(numvar):
            curs.appendvalue(v, vgen.getvalue(v))
        curs.CommitCase()
    curs.CClose()
    
# data generator for generateData function
class Vgenerator(object):
    """Generator for values appropriate for current variable dictionary"""
    s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345678 9 /.,<>[]{}|!@#$%^&*()_+"
    def __init__(self, vartype, varformat):
        """Save variable dictionary information needed for each variable
        vartype is the type code
        varformat is the format"""
        
        self.vartype = vartype
        self.varformat = varformat
        self.funcs = []
        
        for vtype, vformat in zip(self.vartype, self.varformat):
            if vtype == 0:   #numeric, including dates and times
                vs = vformat.split(".")
                if len(vs) > 1:    # has a decimal spec
                    decimals = int(vs[-1])
                else:
                    decimals = 0
                if len(re.findall(r"DATE", vformat)) > 0:   # some date format
                    self.funcs.append((Vgenerator.date, 0))
                else:
                    self.funcs.append((Vgenerator.gnumeric, decimals))
            else:  #string
                vl = re.search(r"\d+$", vformat).group()  #format must end with digit(s)
                self.funcs.append((Vgenerator.gstr, int(vl)))
                
    @staticmethod
    def gnumeric(decimals):
        "Return random numeric truncated to integer if zero decimals"

        if decimals == 0:
            v = float(int(random.normalvariate(5,10)))
        else:
            v = random.normalvariate(1000,25)
        return v
    
    @staticmethod
    def gstr(len):
        "return string of length n drawn from ascii letters and some other characters"
        
        return "".join([random.choice(Vgenerator.s) for i in range(len)])
    
    @staticmethod
    def date(ignore):
        """return a random date"""
        return  random.normalvariate(13166064000,25000)  # mean is 1/1/2000
    
    def getvalue(self, i):
        """Return a value for variable i
        
        i is the index of the variable in the current dictionary"""
        
        return self.funcs[i][0](self.funcs[i][1])