import argparse, sys
try:
	from _winreg import *
except ImportError:
	print >>sys.stderr, "Windows-only _winreg module required"
#
def GetOfficeUserNameInfo(versions = (None, "14.0", "12.0", "11.0", "10.0", "9.0", "8.0")):
	"""
	Note that version 14 uses string values, whereas previous versions use binary values
	"""
	names = set()
	initials = set()
	companies = set()
	#
	for v in versions:
		try:
			key = OpenKey(HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Office\\%s\\Common\\UserInfo" % v if v else "SOFTWARE\\Microsoft\\Office\\Common\\UserInfo")
			if key:
				try:
					UserName, UserNameType = QueryValueEx(key, "UserName")
					UserName = UserName.strip().title()
					if UserName:
						names.add(UserName)
				except WindowsError:
					pass
				try:
					UserInitials, UserInitialsType = QueryValueEx(key, "UserInitials")
					UserInitials = UserInitials.strip().upper()
					if UserInitials:
						initials.add(UserInitials)
				except WindowsError:
					pass
				try:
					Company, CompanyType = QueryValueEx(key, "Company")
					Company = Company.strip()
					if Company:
						companies.add(Company)
				except WindowsError:
					pass
		except WindowsError:
			pass
	return (names, initials, companies)
#
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Retrieve the name Microsoft Office uses for revisions')
	parser.add_argument('--UserName', '-n', action='store_true')
	parser.add_argument('--UserInitials', '-i', action='store_true')
	parser.add_argument('--Company', '-c', action='store_true')
	args = parser.parse_args()
	#
	names, initials, companies = GetOfficeUserNameInfo()
	#
	if len(sys.argv) <= 1:
		args.UserName = True
		args.UserInitials = True
		args.Company = True
	if args.UserName: print ", ".join(names)
	if args.UserInitials: print ", ".join(initials)
	if args.Company:	print ", ".join(companies)