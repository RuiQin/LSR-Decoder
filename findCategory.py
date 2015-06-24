from Dictionary import uniqueEvent
from ProcessDecodedData import getEvent, getText
from sklearn.externals import joblib

#read trained model
classifier = joblib.load('prediction_model.pkl')
target_names = ['Coastal Hazards', 'Dense Fog', 'Snow', 'Ice', 'Thunderstorm', 'Landslide', 'Tornado', 'Blowing Dust', 'Heat', 'Storm Damage', 'High Winds', 'Lightning', 'Heavy Rain', 'Volcanic Ash', 'Flooding', 'Cold', 'Funnel Cloud', 'Hail', 'Sleet', 'Fire', 'Avalanche', 'Waterspout']
    
# calculate edit distance bewteen two strings
def editDistance(str1,str2):
    len1 = len(str1)
    len2 = len(str2)
    dp = [[0 for x in range(len2+1)] for x in range(len1+1)]

    for j in range(1,len2+1):
        dp[0][j] = j

    for i in range(1,len1+1):
        dp[i][0] = i

    for i in range(1,len1+1):
        for j in range(1,len2+1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j-1],dp[i-1][j],dp[i][j-1])+1
    return dp[len1][len2]
    
# given an event, and find its category
# 1. if the event is unique, then return its category in the dictionary
# 2. try to find a category which their edit distance is less or equal to 2
# 3. find a category in the dictionary that is a substring of the LSR event
# if still can't find, return ""
def findCategoryFromDict(event): 
    event = event.upper().strip()  
    # find the exact matching
    if uniqueEvent.has_key(event):
        return uniqueEvent[event]

    events = list(uniqueEvent.keys())
    # find with edit distance <= 2
    for e in events:
        if editDistance(e, event) <= 2:
            return uniqueEvent[e]
    # find with substring
    for e in events:
        if event.find(e) != -1:
            return uniqueEvent[e]
    return ""
        
def findCategoryWithEvent(remarks):
    event = getEvent(remarks)
    pred_cat = findCategoryFromDict(event)
    if pred_cat != "":  # find an exact matching or edit distance <= 2 or substring
        return pred_cat
    else:
        #store commom event remarks and their predicted event index
        common_events_remarks = []
        common_events_pred_index = []    
    
        common_events_remarks.append(remarks)
        common_events_pred_index = classifier.predict(common_events_remarks)
        return target_names[common_events_pred_index[0]]

def findCategoryWithoutEvent(remarks):
    event = getEvent(remarks)
    pred_cat = findCategoryFromDict(event)
    
    if pred_cat != "":  # find an exact matching or edit distance <= 2 or substring
        return pred_cat
    else:  
        text = getText(remarks)
        #store commom event remarks and their predicted event index
        common_events_text = []
        common_events_pred_index = []
        
        common_events_text.append(text)
        common_events_pred_index = classifier.predict(common_events_text)
        return target_names[common_events_pred_index[0]]
      

    