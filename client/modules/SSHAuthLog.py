import re

WORDS = []

# check for these patterns
patterns = ['.*Failed password for (.*) from\s([\d.]*)',
            '.*Invalid user\s(.*)\sfrom\s([\d.]*)']

def checkInvalidAuthentication(profile, last_pos):
    f = open(profile['ssh_auth_log'])
    
    ret = [];
    
    if last_pos:
        # start from the last position
        f.seek(last_pos, 0)
    else:
        # start from the end of the log
        f.seek(0, 2)
    
    while True:
        # return the current position in the log
        last_pos = f.tell()
        
        # read the line
        line = f.readline()

        if not line:
            return ret, last_pos
        else:
            matches = [re.match(p, line) for p in patterns]
            for match in matches:
                if match:
                    # make a dict like: {'ip': '213.96.119.230', 'user': 'guest'}
                    # and append it to an array
                    ret.append( dict( zip( ('user', 'ip'), match.groups() ) ) )
                    break
    f.close()
    
    # return a tuple like: ([{'ip': '213.96.119.230', 'user': 'guest'}], 777L)
    return ret, last_pos

def isValid(text):
    return False