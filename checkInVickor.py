import random

"""
DEPENDENCIES:
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python-pip
pip install requests
pip install numpy
pip install sklearn
"""

"""
Assuming that the user remains the same for my program
Group: 1
User ID: 16
Username: jeangray

-----------------------------------------------------------------------------------
"""
# rules -
import numpy as np
import requests
import json
user = "16"
group = "1"
username = "jeangray"

def getResponse(URL):
    request = requests.get(URL)
    return json.loads(request.text)
# get all the social relations of all people in the study
relations = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getRelationshipList")
# print(relations)
allCheckIns = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getAllCheckInByPlace&userId=1&placeId=1")
# allCheckIns = allCheckIns["check-ins"]
print(allCheckIns)
'''
        Place IDs (LIDs):
Graduation ceremony                     1
Library during the day                  2
Hurricane during the day                3
Airport at night                        4
Hiking on a mountain                    5
Presenting a paper at a conference      6
Bar with a fake ID                      7

        Policy IDs (PIDs):
Share with no one                       1
Share with companions                   2
Share with common friends               3
Share with all                          4
'''
feedback_to_id = {"very negative":1,  "negative":2, "neutral":3,  "positive":4, "very positive":5}
'''
        Sanction (feedback) IDs (SIDs):
Very negative                           1
Negative                                2
Neutral                                 3
Positive                                4
Very positive                           5

    sanctions = {place:{policy: sanction}}
'''
sanctions = {
                "1":{"1":"3",   "2":"4",    "3":"5",    "4":"5"},
                "2":{"1":"5",   "2":"4",    "3":"1",    "4":"1"},
                "3":{"1":"2",   "2":"3",    "3":"4",    "4":"5"},
                "4":{"1":"2",   "2":"3",    "3":"5",    "4":"4"},
                "5":{"1":"1",   "2":"3",    "3":"5",    "4":"4"},
                "6":{"1":"3",   "2":"3",    "3":"4",    "4":"5"},
                "7":{"1":"5",   "2":"4",    "3":"1",    "4":"1"}
            }

default_checkIn_policy = {"1":"4",  "2":"1",    "3":"4",    "4":"3",    "5":"3",    "6":"4",    "7":"1"}

commonIdentityType = "1"

def getVikorPolicy(user, location, companions):
    print("\nPlease wait while policy is being calculated")
    classifierSuggested = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getPolicy&userId="+user+"&placeId="+location+"&companionId="+companions+"&type=" + commonIdentityType)
    classifierSuggested = classifierSuggested["policyId"]
    request = "http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=setCheckIn&userId=" + user + "&placeId=" + location +"&companions=" + companions + "&classfierSuggested="+str(classifierSuggested)+"&policy="
    # get all the checkins for this place for all companions
    companionsList = companions.split('|')
    companionsList.append(user)
    policyPerson = {}
    f_star = {}
    f_minus = {}
    f = {}
    Sj = {"1":0,"2":0,"3":0,"4":0}
    Rj = {"1":0,"2":0,"3":0,"4":0}
    Qj = {"1":0,"2":0,"3":0,"4":0}
    # get default checkin policy for the person
    policyPerson[user] = {}
    for i in range(1,5):
        if default_checkIn_policy[location] == str(i):
            policyPerson[user][str(i)] = 10
        else:
            policyPerson[user][str(i)] = 5
    for companion in companionsList:
        allCheckIns = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getAllCheckInByPlace&userId="+companion+"&placeId=" + location)
        if "check-ins" in allCheckIns:
            allCheckIns = allCheckIns["check-ins"]
            # print("ALL CHECKINS for ",companion,":  ", allCheckIns)
            for checkIn in allCheckIns:
                check_in_info = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getCheckIn&checkinId=" + checkIn["checkinId"])
                policyId = check_in_info["check-in"]["policyId"]
                if companion in policyPerson:
                    if policyId in policyPerson[companion]:
                        policyPerson[companion][policyId] += 1
                    else:
                        policyPerson[companion][policyId] = 1
                else:
                    policyPerson[companion] = {}
                    policyPerson[companion][policyId] = 1

        if companion not in policyPerson:
            policyPerson[companion] = {}
        for index in range(1,5):
            if str(index) not in policyPerson[companion]:
                policyPerson[companion][str(index)] = random.randint(1, 100)/float(10)


    # print("Values of policyPerson: ", policyPerson)
    # normalize all the values
    for userId in policyPerson:
        sum = 0
        for policyId in policyPerson[userId]:
            sum += policyPerson[userId][policyId]
        for policyId in policyPerson[userId]:
            policyPerson[userId][policyId] /= float(sum)

    # print("Values of policyPerson after norm: ", policyPerson)
    # get f_star and f_minus
    for userId in policyPerson:
        fmax = 0
        fmin = 99999999
        for policyId in policyPerson[userId]:
            if policyPerson[userId][policyId] > fmax:
                fmax = policyPerson[userId][policyId]
            if policyPerson[userId][policyId] < fmin:
                fmin = policyPerson[userId][policyId]
        f_star[userId] = fmax
        f_minus[userId] = fmin
        #  populate f = (fi_star - fij)/(fi_star - fi_minus)
        f[userId] = {}
        for policyId in policyPerson[userId]:
            f[userId][policyId] = (f_star[userId] - policyPerson[userId][policyId])/float(f_star[userId] - f_minus[userId])

        # print("f: ", f)
        # get values for S,R and Q
        for policyId in policyPerson[userId]:
            Sj[policyId] += f[userId][policyId]
            if Rj[policyId] < f[userId][policyId]:
                Rj[policyId] = f[userId][policyId]
    # print("f_star: ", f_star, "\nf_minus: ", f_minus)
    # print("S: ", Sj, "\nR: ", Rj)

    # assume v = 0.5
    Sj["1"] += 0.0001
    Rj["1"] += 0.0001
    for policyId in f[user]:
        Qj[policyId] = 0.5*(Sj[policyId] - Sj[min(Sj.keys(), key=(lambda k: Sj[k]))])/(Sj[max(Sj.keys(), key=(lambda k: Sj[k]))] - Sj[min(Sj.keys(), key=(lambda k: Sj[k]))])
        Qj[policyId] += 0.5*(Rj[policyId] - Rj[min(Rj.keys(), key=(lambda k: Rj[k]))])/(Rj[max(Rj.keys(), key=(lambda k: Rj[k]))] - Rj[min(Rj.keys(), key=(lambda k: Rj[k]))])
    # print("Q: ", Qj)

    return min(Qj.keys(), key=(lambda k: Qj[k]))

def checkIn(user, location, companions):
    # commonIdentityType = "0"
    # while commonIdentityType != "1" and commonIdentityType != "4":
    #     commonIdentityType = raw_input("Enter:\n1 -> if you want to imitate what people generally do at the place OR\n4 -> if you want to act based on your past experience of that place\n")
    policy = getVikorPolicy(user, location, companions)
    classifierSuggested = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getPolicy&userId="+user+"&placeId="+location+"&companionId="+companions+"&type=" + commonIdentityType)
    classifierSuggested = classifierSuggested["policyId"]
    request = "http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=setCheckIn&userId=" + user + "&placeId=" + location +"&companions=" + companions + "&classfierSuggested="+str(classifierSuggested)+"&policy="
    id_of_this_checkin = getResponse(request+str(policy))["check-in"]["checkinId"]
    print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))


def getAllUnTaggedCheckIns(user):
    unTaggedCheckins = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getUnattendedCheckins&userId="+user)
    # print("\n\nList of all unattended checkins\n\n",unTaggedCheckins["check-ins"])
    return unTaggedCheckins["check-ins"]
def giveSanctions(user, checkIn):
    # checkInData = requests.get("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckIn&checkinId=" + checkInID)
    # checkInData = json.loads(checkInData.text)
    checkInID = checkIn["checkinId"]
    place = checkIn["placeId"]
    policy = checkIn["policyId"]
    companionsList = checkIn["companions"]
    companions = []
    for companion in companionsList:
        companions.append(companion["userId"])
    companions.remove(user)
    companions = "|".join(companions)
    classifierAction = requests.get("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=getPolicy&userId=" + user + "&placeId=" + place +"&companionId=" + companions + "&type=" + commonIdentityType)
    classifierAction = json.loads(classifierAction.text)
    # print("--------------",classifierAction)
    classifierPolicy = str(classifierAction["policyId"])
    sanctionID = sanctions[place][classifierPolicy]
    VigorPolicy = getVikorPolicy(user, place, companions)
    vigorSanctionID = sanctions[place][VigorPolicy]

    print("sanctionid: ",sanctionID, "vikor sanction id: ", vigorSanctionID)
    responseFromSanction = requests.get("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox-sd/services.jsp?query=respondToCheckin&checkinId="+checkInID+"&companionId="+user+"&classfierSanctionId="+sanctionID+"&sanctionId=" + vigorSanctionID)
    responseFromSanction = json.loads(responseFromSanction.text)
    print("\nSanction Response:\n",responseFromSanction)


while(True):
    try:
        print("\n-------------------Select task--------------------\n")
        option = raw_input("- CheckIn Policy by learning(1)\n- Give Sanction(2)\n")
        if(option=="1"):
            location = input("Enter the location:\t")
            companions = raw_input("Enter companions(names or IDs separated by a '|'):\t")
            checkIn(user,str(location),companions);
        elif(option=="2"):
            # get array of checkin objects that are yet to be tagged
            unTaggedCheckins = getAllUnTaggedCheckIns(user)
            for checkIn in unTaggedCheckins:
                giveSanctions(user,checkIn)
        else:
            print("\nWrong Input\nPlease enter 1,2 or 3\n")
    except KeyboardInterrupt:
        print("\n\nProcess stopped\n\n")
        break
