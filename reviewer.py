from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import utils
import getpass
from bson.objectid import ObjectId

def resign(revid,db):
    try:
        db.reviewers.find_one_and_update({"_id":ObjectId(revid)},{"$set":{"status":"inactive"}})
        print('Thank you for your Service')
        print('EXITING PROGRAM')
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def optionsReviewer(revid,db):
    manNum = raw_input('PLEASE ENTER A MANUSCRIPT NUMBER YOU WANT TO REVIEW <ManNum> or EXIT to exit:')
    if(manNum == 'EXIT'):
        return
    Clarity = raw_input('Please enter score from 1-10 for Clarity:')
    Appropriateness = raw_input('Please enter score from 1-10 for Appropriateness:')
    Contribution = raw_input('Please enter score from 1-10 for Contribution:')
    Methodology = raw_input('Please enter score from 1-10 for Methodology:')
    Recommendation = raw_input('Type ACCEPT to recommend accepting the manuscript, or REJECT if not:')
    Recommendation = Recommendation.lower()
    try:
        print('here1')
        pipeline = [
            {"$match":{"_id":ObjectId(manNum)}},
            {"$unwind": "$reviewers"},
            {"$match": {"reviewers":revid}}
        ]
        print('here2')
        reviews = list(db.manuscript.aggregate(pipeline))
        print('here3')
        numReviews = len(reviews)
        print(reviews)
        if(numReviews==0):
            print("Manuscript not found or does not belong to this Reviewer")
            statusCommand(revid,db)
        for item in reviews:
            if(item["status"]!="under review"):
                print('manuscript is not under review')
                statusCommand(revid,db)
            print('here4')
            if(numReviews != 0):
                for review in item["reviews"]:
                    if(review["reviewerid"]==revid):
                        print('reviewer has already reviewed this manuscript')
                        statusCommand(revid,db)
                db.manuscript.find_one_and_update({"_id":manNum},{"$push":{"reviews":{
                    "reviewerid":revid,
                    "appropriateness":Appropriateness,
                    "clarity":Clarity,
                    "methodology":Methodology,
                    "contribution":contribution,
                    "recommendation":recommendation
                    }}})

        else:
            print('Manuscript not assigned to this reviewer')
        statusCommand(revid,db)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def statusCommand(revid,db):
    try:
        pipeline = [
            {"$unwind": "$reviewers"},
            {"$match": {"reviewers":revid}}
        ]
        reviews = list(db.manuscript.aggregate(pipeline))
        numReviews = len(reviews)


        for item in (list(reviews)):

            for review in item["reviews"]:

                if(review["reviewerid"] == revid):
                    print(item["title"])
                    print("     appropriateness: %s" % (review["appropriateness"] ))
                    print("     clarity: %s" % (review["clarity"]) )
                    print("     methodology: %s" % (review["methodology"]) )
                    print("     contribution: %s" % (review["contribution"]) )
                    print("     recommendation: %s" % (review["recommendation"]) )

        if (numReviews == 0):
            print("You currently have no manuscripts for which you are the reviewer.")
        optionsReviewer(revid,db)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))


def loginReviewer(revid,db):
    try:
        reviewer = db.reviewers.find({"_id":revid,"status":"active"})
        revList = list(reviewer)
        if (len(revList)==0):
            print("That is not an active reviewer.")
            return
        print('Welcome Back!\n')
        print("Name: %s\n" % (revList[0]["name"]))
        statusCommand(revid,db)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def createReviewer(name,email,affiliation,interestArr,db):
    print('got here')
    try:
        newid = db.reviewers.insert_one({ "name": name, "email": email, "affiliation": affiliation,"status":"active", "interests":interestArr }).inserted_id
        print("Your unique id is %s" % str(newid))
        loginReviewer(newid,db)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerReviewer(n,e,a,i,db):
    name = n
    email = e
    affiliation = a
    interests = i
    interestArr = []
    if(name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
    if (affiliation is None):
        user_input = raw_input("Please enter your affiliation.\n")
        affiliation = user_input
    if (interests is None):
        interests = db.interests.find_one()
        ricodes = interests["ricodes"]
        i=1
        for ricode in ricodes:
            print("%d:%s\n" % (i,ricode))
            i+=1
        print("Please enter the number of interests that you have out of this list:\n")
        user_input = raw_input("Enter: ")
        i = 0
        while i < int(user_input):
            k = raw_input("Enter the corresponding id of interest %d: " % (i+1))
            interestArr.append(k)
            i+=1
    print('got to before createReviewer')
    createReviewer(name,email,affiliation,interestArr,db)
