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
relations = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getRelationshipList")
# print(relations)
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

def checkIn(user, location, companions, method):
    # keep a list of unused policies for this place
    policy_not_used = ['1','2','3','4']
    request = "http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=setCheckIn&userId="+ user +"&placeId="+ location +"&companions="+companions+"&policy="
    # get all the checkins for this place
    allCheckIns = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getAllCheckInByPlace&userId="+user+"&placeId=" + location)
    allCheckIns = allCheckIns["check-ins"]
    # print("allCheckIns:")
    # print(allCheckIns)
    X = []
    Y = []
    feedbacks = {}
    for checkIn in allCheckIns:
        check_in_info = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckIn&checkinId=" + checkIn["checkinId"])
        policyId = check_in_info["check-in"]["policyId"]
        placeId = check_in_info["check-in"]["placeId"]
        # print("policyId:\t" + check_in_info["check-in"]["policyId"])
        # print("placeId:\t" + check_in_info["check-in"]["placeId"])
        # get the feedbacks for all of the past the checkins of this place
        curr_feedbacks = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + checkIn["checkinId"])
        curr_feedbacks = curr_feedbacks["feedbacks"]
        # print("curr_feedbacks: \t")
        # print(curr_feedbacks)
        '''
        make a list of feedbacks for a particular policy id.
        load a feedback value and the person who gave it in X and policy used in Y for use in Naive Bayes classification
        '''
        for feedback in curr_feedbacks:
            if policyId not in feedbacks:
                feedbacks[policyId] = []
                if policyId in policy_not_used:
                    policy_not_used.remove(policyId)
            if feedback_to_id[feedback["feedback"]]>=3:
                value_for_X = 1
            else:
                value_for_X = -1
            X.append([value_for_X, int(feedback["userId"])])
            Y.append(int(policyId))
            feedbacks[policyId].append(feedback_to_id[feedback["feedback"]])

    # print("Feedbacks:")
    # print(feedbacks)
    policy_to_num_of_good_feedbacks = {}
    # Get the value from all feedbacks that we will use for our policy decision
    count=0
    for policy in feedbacks:
        if feedbacks[policy] != []:
            count+=1
        # find the number of neutral and positive feedbacks
        sum_of_good_feedbacks = sum(i > 2 for i in feedbacks[policy])
        # difference between the number of desirable feedbacks and undesirable feedbacks
        policy_to_num_of_good_feedbacks[policy] = sum_of_good_feedbacks - (len(feedbacks[policy]) - sum_of_good_feedbacks)

    # print("Good Feedbacks: ")
    # print(policy_to_num_of_good_feedbacks)
    # if there are no feedbacks for this place
    if count == 0:
        print("Default check-in\n"+default_checkIn_policy[location]+"\n")
        print(request+default_checkIn_policy[location])
        id_of_this_checkin = getResponse(request+default_checkIn_policy[location])["check-in"]["checkinId"]
        print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))
        return

    temp_max = 0
    for policy in policy_to_num_of_good_feedbacks:
        if temp_max == policy_to_num_of_good_feedbacks[policy] and temp_max != 0:
            if len(feedbacks[policy]) > len(feedbacks[temp_policy]):
                temp_max = policy_to_num_of_good_feedbacks[policy]
                temp_policy = policy
        elif temp_max < policy_to_num_of_good_feedbacks[policy]:
            temp_max = policy_to_num_of_good_feedbacks[policy]
            temp_policy = policy
    # there are good values
    if temp_max > 0:
        if method == '1':
            print("Using the Max-Best policy")
            print("select best from feedback\n\n")
            print(request+temp_policy)
            id_of_this_checkin = getResponse(request+temp_policy)["check-in"]["checkinId"]
            print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))
        # If the user wants to use the Naive Bayes policy
        elif method == "2":
            print("Using the Naive Bayes policy:\n")
            X = np.array(X)
            Y = np.array(Y)
            from sklearn.naive_bayes import GaussianNB
            clf = GaussianNB()
            clf.fit(X, Y)
            companions = companions.split('|')
            if companions == ['']:
                companions = ["1"]
            to_predict = []
            # print(companions)
            for companion in companions:
                to_predict.append([1,int(companion)])
            # print(to_predict)
            # use the minimum of the policies. i.e the least sharing one
            print(request+str(min(clf.predict(to_predict))))
            id_of_this_checkin = getResponse(request+str(min(clf.predict(to_predict))))["check-in"]["checkinId"]
            print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))
    #  there are no good values
    else:
        print("Random checkin\n\n")
        import random
        if len(policy_not_used) == 0:
            random_number = random.randint(1, 4)
            print(request+str(random_number))
            id_of_this_checkin = getResponse(request+str(random_number))["check-in"]["checkinId"]
            print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))
        else:
            print(request+random.choice(policy_not_used))
            id_of_this_checkin = getResponse(request+random.choice(policy_not_used))["check-in"]["checkinId"]
            print(getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckinFeedbacks&checkinId=" + id_of_this_checkin))
    return



def getAllUnTaggedCheckIns(user):
    unTaggedCheckins = getResponse("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getUnattendedCheckins&userId=" + user)
    # print("\n\nList of all unattended checkins\n\n",unTaggedCheckins["check-ins"])
    return unTaggedCheckins["check-ins"]
def giveSanctions(user, checkIn):
    # checkInData = requests.get("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=getCheckIn&checkinId=" + checkInID)
    # checkInData = json.loads(checkInData.text)
    checkInID = checkIn["checkinId"]
    place = checkIn["placeId"]
    policy = checkIn["policyId"]
    sanctionID = sanctions[place][policy]
    print("\nSanction:\t",sanctionID)
    responseFromSanction = requests.get("http://yangtze.csc.ncsu.edu:9090/csc555checkinf18-sandbox/services.jsp?query=respondToCheckin&checkinId="+checkInID+"&companionId="+user+"&sanctionId="+sanctionID)
    responseFromSanction = json.loads(responseFromSanction.text)
    print("\nSanction Response:\n",responseFromSanction)


while(True):
    try:
        print("\n-------------------Select task--------------------\n")
        option = input("- CheckIn Policy by learning(1)\n- Give Sanction(2)\n")
        if(option==1):
            # user = input("Enter the username or userID:\t")
            location = input("Enter the location:\t")
            companions = raw_input("Enter companions(names or IDs separated by a '|'):\t")
            method = raw_input("Enter the method number you want to use to learn: 1(Max Best)\t2(Naive Bayes)")
            checkIn(user,str(location),companions,method);
        elif(option==2):
            # get array of checkin objects that are yet to be tagged
            unTaggedCheckins = getAllUnTaggedCheckIns(user)
            for checkIn in unTaggedCheckins:
                giveSanctions(user,checkIn)
        # elif(option==3):
        #     learn()
        else:
            print("\nWrong Input\nPlease enter 1,2 or 3\n")
    except KeyboardInterrupt:
        print("\n\nProcess stopped\n\n")
        break
