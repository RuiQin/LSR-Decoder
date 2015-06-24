import sys
import re
from ProcessDecodedData import *
from findCategory import findCategoryWithEvent
from connectDatabase import insert

# find the position of header. header:
# 671 
# NWAK58 PAFC 092325
# LSRAFC
def findheader(s):
    m = re.search('\d{3} \n\w{4}\d{1,2} \w{4} (\d{2})(\d{2})(\d{2}).*\n\w{6}',s)
    if m != None:
        return m.span()
    else:
        return [-1,-1]

# find the position of a new record, ex:
# 1100 AM or 0830 AM     
def findNewRecordStart(s):
    m = re.search('\n\d{3,4} (AM|PM)\s{4,5}',s)
    if m != None:
        return m.start()
    else:
        return -1
    
def findAllRecordsEnd(s):
    end1 = s.find('&&')
    end2 = s.find('$$')
    if end1 < end2:   # normal case: group records end with && \n $$
        return end1
    else:               # group records end with only $$
        return end2

# check whether has next record which share the same header   
def whetherHasNextRecord(records):
    nextStart = findNewRecordStart(records)      # find the next record which share the same header, begin with XXXX AM|PM
    allRecordsEnd = findAllRecordsEnd(records)   # find the end '&&' of all records have the same header          
    hasNextRecord = True
    if nextStart == -1:
        hasNextRecord = False
    elif nextStart < allRecordsEnd:
        hasNextRecord = True
    else:
        hasNextRecord = False
    return hasNextRecord

# add record to a list, if it doesn't exist, then we add it, if not, we don't add   
def removeDuplicates(records):
    found = set()
    newList = []
    for item in records:
        t = tuple(item)
        found.add(t)
    return list(found) 
                          
def readLSRFile(fileLocation):
    print '****** read file:', fileLocation
    file = open(fileLocation, 'r')
    records = file.read().strip()
    recordsInOneFile = []
        
    hasNextGroupRecords = True    # indicates whether it has next group of records share the same header  
    while hasNextGroupRecords:
        # read the first three lines header
        headerPos = findheader(records)
        header = records[headerPos[0]:headerPos[1]]
        nextHeaderPos  = findheader(records[headerPos[1]:])
        if nextHeaderPos != [-1,-1]:
            hasNextGroupRecords = True
        else:
            hasNextGroupRecords = False    
        #print '** header:'
        #print header
        headerSecondLine = header.split('\n')[1]   # 'NWAK58 PAFC 092325'
        issuingTimeInfo = headerSecondLine.split()
        issuingDayHourMin = issuingTimeInfo[2]  # 092325
        
        # read the second three lines, including the issuing information
        records = records[headerPos[1]:]
        issuingInfoEnd = records.find('\n..')
        issuingInfo = records[:issuingInfoEnd].strip()
        if issuingInfo.find('PRELIMINARY LOCAL STORM REPORT') != 0:   # if it doesn't begin with PRELIMINARY LOCAL STORM REPORT, then skip
            continue
        issuingList = issuingInfo.split('\n')
        issuingLocInfo = issuingList[1]      # NATIONAL WEATHER SERVICE PADUCAH KY
        issuingOffice = findIssuingOffice(issuingLocInfo)  
        
        issuingTimeInfo = issuingList[len(issuingList)-1].split()   # 110 PM MDT FRI MAR 13 2015
        issuingTimeZone = issuingTimeInfo[2]
        issuingDate = generateDate(issuingTimeInfo[4],issuingTimeInfo[5],issuingTimeInfo[6][0:4]) # (mon, day, year)
        issuingTime = generateTime(issuingDayHourMin)
        issuingDateTime = issuingDate + ' ' + issuingTime
        originaltext = issuingInfo
        
        # including all the titles
        records = records[issuingInfoEnd:]
        titleEnd = records.find('..REMARKS..')
        title = records[:titleEnd+11].strip()
        originaltext = originaltext + '\n\n' + title    
        
        hasNextRecord = whetherHasNextRecord(records)   # has next record that share the same header       
        records = records[titleEnd+11:].strip()   # start from time, ex: 0155 PM
         
        # ------ find each event information ------
        while hasNextRecord:
            oneRecord = []                     
            text = originaltext                # make a copy of the original text including the header, issuingInfo and title
            #event time
            while (len(records) > 0 and isNum(records[0]) == False):
                records = records[1:]
            timeEnd = 0
            while timeEnd < len(records) and timeEnd < 7:
                if records[timeEnd] == 'M':
                    timeEnd = timeEnd + 1
                    break
                timeEnd = timeEnd + 1
            time = changeTimeFormat(records[0:timeEnd])  # from HHMM A/PM to HH:MM:SS 
            
            # check whether has next record
            nextStart = findNewRecordStart(records)      # find the next record which share the same header, begin with XXXX AM|PM
            allRecordsEnd = findAllRecordsEnd(records)   # find the end '&&' of all records have the same header          
            if nextStart == -1:
                hasNextRecord = False
                text = text + '\n\n' + records[:allRecordsEnd]
            elif nextStart < allRecordsEnd:
                hasNextRecord = True
                text = text + '\n\n' + records[:nextStart]
            else:
                hasNextRecord = False
                text = text + '\n\n' + records[:allRecordsEnd]
                
            #event
            records = records[timeEnd:].strip()  # start from event    
            eventLocStart = 10   # special case SNOW_24, start from 10 characters
            while (eventLocStart < len(records) and eventLocStart < 17):  
                if isNum(records[eventLocStart]) == True:
                    break
                eventLocStart = eventLocStart + 1      
            event = records[0:eventLocStart].strip()
            
            #event city, latitude, longitude 
            records = records[eventLocStart:].strip()  # start from city
            dateStart = records.find('\n')       
            city_latLon = records[0: dateStart]
            LatLonStart = 17  #escapse the number in city 
            while LatLonStart+2 < len(city_latLon):
                if city_latLon[LatLonStart+2] == '.' and isNum(city_latLon[LatLonStart]) == True:
                    break  
                else:
                    LatLonStart = LatLonStart + 1     
            city = city_latLon[0:LatLonStart].strip()
            latLon = city_latLon[LatLonStart:].strip()
            
            #date
            records = records[dateStart:].strip()  # start with date   
            date = records[0:10]
            if len(date.strip()) == 10:
                date = changeDateFormat(date)
            else:
                date = issuingDate # if the date doesn't exist, use the issuing date
            
            #magnitude(if it has)
            magnitude = records[10:29].strip()
        
            # check whether it has county, state
            records = records[29:]    # start from county
            county = records[0:19].strip()  
            state = records[19:21].strip()    
       
            #source
            records = records[24:]
            source = findSubStringBeforeNewLine(records).strip()
            
            #remarks
            remark = ''
            if hasNextRecord:
                nextNewRecordStart = findNewRecordStart(records)
                remark = records[len(source):nextNewRecordStart].strip()
                records = records[nextNewRecordStart:]
            else:
                nextAllRecordsStart = findAllRecordsEnd(records)
                remark = records[len(source):nextAllRecordsStart].strip()
                records = records[nextAllRecordsStart:]
  
            #----------------- process parsed data to get standard parsed data----------------    
            #magnitude = processMagnitude(magnitude)
            remarks = generateRemarks(event,remark)
            eventType = findCategoryWithEvent(remarks)
            ao = splitLatLon(latLon)
            latitude = ao[0]
            longitude = ao[1]

            oneRecord.append(date+" "+time)
            oneRecord.append(issuingTimeZone)
            oneRecord.append(city)
            oneRecord.append(county)
            oneRecord.append(state)
            oneRecord.append(latitude)
            oneRecord.append(longitude)    
            oneRecord.append(eventType)
            oneRecord.append(magnitude)
            oneRecord.append(source)
            oneRecord.append(remarks)
            oneRecord.append(issuingOffice)
            oneRecord.append(issuingDateTime)
            oneRecord.append(issuingTimeZone)
            oneRecord.append(text.strip())           
            recordsInOneFile.append(oneRecord) 
    
    beforeRemoved = len(recordsInOneFile)        
    recordsInOneFile = removeDuplicates(recordsInOneFile)
    removeNo =  beforeRemoved - len(recordsInOneFile)
    if removeNo > 0:
        print 'removed', removeNo, 'duplicate records'
    # insert data into table lsr in database
    query = "INSERT INTO lsr2 (date_time, time_zone, city, county, state, latitude, longitude, event_type, magnitude, source, remarks, issuing_nws_office, issuing_date_time, issuing_time_zone, original_report_text) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insert(recordsInOneFile, query)
        
if __name__=="__main__":
    fileLocation = sys.argv[1]
    readLSRFile(fileLocation)
