# Functions to identify and extract URLs and email addresses

import re, fileinput, string

pat_url = re.compile(  r'''
                 (?x)( # verbose identify URLs within text
     (http|ftp|gopher) # make sure we find a resource type
                   :// # ...needs to be followed by colon-slash-slash
        (\w+[:.]?){2,} # at least two domain groups, e.g. (gnosis.)(cx)
                  (/?| # could be just the domain name (maybe w/ slash)
            [^ \n\r"]+ # or stuff then space, newline, tab, quote
                [\w/]) # resource name ends in alphanumeric or slash
     (?=[\s\.,>)'"\]]) # assert: followed by white or clause ending
                     ) # end of match group
                       ''')
pat_email = re.compile(r'''
                (?xm)  # verbose identify URLs in text (and multiline)
             (?=^.{11} # Mail header matcher
     (?<!Message-ID:|  # rule out Message-ID's as best possible
        In-Reply-To))  # ...and also In-Reply-To
               (.*?)(  # must grab to email to allow prior lookbehind
   ([A-Za-z0-9-]+\.)?  # maybe an initial part: DAVID.mertz@gnosis.cx
        [A-Za-z0-9-]+  # definitely some local user: MERTZ@gnosis.cx
                    @  # ...needs an at sign in the middle
         (\w+\.?){2,}  # at least two domain groups, e.g. (gnosis.)(cx)
    (?=[\s\.,>)'"\]])  # assert: followed by white or clause ending
                     ) # end of match group
                       ''')

pat_spss_if_assignment = re.compile( r'''
			       (?xi)( # allow comments, case insensitive
			        if\s* # begins with an if statement
		     (.*(and|or)\s*)* # predicates are possible
		       keycode\s*=\s* # keycode assignment
	        (?P<keycode>\w{5})\s* # 
	  (?P<assign_name>\w+)\s*=\s* #
(?P<assign_value>[0-9](.[0-9]+)?)\s*) #
				      ''')

#extract_phrase = lambda s: [u[0] for u in re.findall(pat_spss_if_assignment, s)]
#extract_phrase = lambda s: re.match(pat_spss_if_assignment, s)
extract_phrase = lambda s: re.match(pat_spss_if_assignment, s)
# extract_email = lambda s: [(e[1]) for e in re.findall(pat_email, s)]

output_template=string.Template(r'''$keycode,$assign_value''')
selected_field=r'''Etpre'''

if __name__ == '__main__':
	assignments=[]
	for line in fileinput.input():
		u = extract_phrase(line)
		if u:
			assignments.append(u.groupdict())
	assignments=filter(lambda d: 'keycode' in d, assignments)
	variables=set([x['assign_name'] for x in assignments])
	
	print "The following variables are defined:"
	print variables
	
	for field_name in variables:
		selection=filter(lambda d: 'assign_name' in d and d['assign_name']==field_name, assignments)
		print "%s\t%s" % (len(selection), field_name)