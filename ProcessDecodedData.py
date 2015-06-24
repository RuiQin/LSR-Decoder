from Dictionary import month

# find the substring before '\n'
def findSubStringBeforeNewLine(rest):
    pos = rest.find('\n')
    if pos != -1:
        return rest[0:pos]
    else:
        return ""

#from mm/dd/yyyy to yyyy-mm-dd
def changeDateFormat(date):
    newDate = date[6:] + "-" +date[0:2]+"-"+date[3:5]
    return newDate

#check whether a character is a number
def isNum(ch):
    if(ch >= '0' and ch <= '9'):
        return True
    else:
        return False

#check whether a string is a number
def isANumber(s):
    i = 0
    while i < len(s):
        if isNum(s[i]) == True:
            i = i + 1
        else:
            break
    if i < len(s) and s[i] == '.':
        i = i + 1
    while i < len(s):
        if isNum(s[i]) == True:
            i = i + 1
        else:
            return False
    return i == len(s)
    
#check whether a character is A-Z
def isAlph(ch):
    if (ch >= 'A' and ch <= 'Z'):
        return True
    else:
        return False

# find the issuing office
def findIssuingOffice(s):
    pos = s.find('NATIONAL WEATHER SERVICE')
    if pos != -1:
        return s[pos+len('NATIONAL WEATHER SERVICE'):].strip()
    else:
        return ''
        
# given month, day, year return yyyy-mm-dd
def generateDate(mon, day, year):
    mm = month[mon]
    return year + '-' + mm + '-' + day
        
#from hhmm AM/PM to hh:mm:ss
def changeTimeFormat(time):
    newTime = ""
    apm = time[-2:]
    if apm == "AM":
        if time[:-5]=="12":
            newTime = "00"+":"+time[2:4]+":00"
        else:
            newTime = time[:-5]+":"+time[-5:-3]+":00"
    elif apm == "PM":
        if time[:-5]=="12":
            newTime = "12"+":"+time[2:4]+":00"
        else:
            newTime = str((int)(time[:-5])+12)+":"+time[-5:-3]+":00"
    return newTime

# give a string ddhhmm return hh:mm:ss
def generateTime(dayHourMin):
    return dayHourMin[2:4] + ':' + dayHourMin[4:] + ':00'
    
#generate remarks
def generateRemarks(event,remark):
    if len(remark) == 0:
        return event
    else:
        return event+": "+remark

#remove one character prefix in Magnitude
def processMagnitude(m):
    if len(m) == 0:
        return m
    if isAlph(m[1]) == True or m[1] == '-':  # EF0 or M-11 F 
        return m
    elif isNum(m[0]) == True:  # 0 MPH
        return m
    else:
        return m[1:]

#split latotude and longitude
def splitLatLon(latLon):
    if len(latLon) == 0:
        return [0,0]
    ao = latLon.split()
    lat = ao[0]
    lon = ao[1]
    lat = lat[0:len(lat)-1]
    lon = "-"+lon[0:len(lon)-1]
    return [lat,lon]
        
#Given a remark (Event: Text), return it's event
def getEvent(remarks):
    for j in range(len(remarks)):
        if remarks[j] == ":":
            return remarks[:j]
    return remarks.strip()

#Given a remark (Event: Text), return it's Text, if there is only Event then return Event
def getText(remarks):
    for j in range(len(remarks)):
        if remarks[j] == ':':
            return remarks[j+1:].strip()
    return remarks
