from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import utils
import getpass

def resign(revid,con):
    try:
        cursor=con.cursor()
        cursor.execute("UPDATE Reviewer SET `Status`='inactive' WHERE ReviewerNum=%s",(revid,))
        con.commit()
        cursor.close()
        print('Thank you for your Service')
        print('EXITING PROGRAM')
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def optionsReviewer(revid,con):
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
        cursor=con.cursor()
        cursor.execute("SELECT * FROM Review WHERE ManuscriptNum=%s AND ReviewerNum=%s",(manNum,revid,))
        row = cursor.fetchone()

        if(row!=None):
            cursor.close()
            cursor = con.cursor()
            cursor.execute("SELECT * FROM Manuscript WHERE ManuscriptNum=%s AND `Status`='under review'",(manNum,))
            row = cursor.fetchone()
            if(row!=None):
                cursor.close()
                cursor = con.cursor()
                cursor.execute("UPDATE Review SET `Clarity`=%s,Appropriateness=%s,Contribution=%s,Methodology=%s,Recommendation=%s WHERE ManuscriptNum=%s AND ReviewerNum=%s",(Clarity,Appropriateness,Contribution,Methodology,Recommendation,manNum,revid))
                con.commit()
                print("Manuscript "+manNum+" updated")
            else:
                print("Manuscript not under review")
        else:
            print('Manuscript did not belong to this reviewer\n')
        cursor.close()
        statusCommand(revid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def statusCommand(revid,db):
    try:
        pipeline = [
            {"$unwind": "$reviews"},
            { "$match": {"reviewerid":revid}}
        ]
        reviews = db.manuscript.aggregate(pipeline)
        print(reviews)
        print(list(reviews))
        # reviews = db.manuscript.find({ "reviews": { "$elemMatch": { "reviewerid": ObjectId(revid) }}})
        # print('sup')
        # print(list(reviews))
        numReviews = len(list(reviews))
        print('herio')
        i = 0
        while i < numReviews:
            print('hi')
            # print("""\nReviewerNum: %s\nDateSent: %s\nManuscript Number: %s\nManuscript Title: %s\nAppropriateness: %s\nClarity: %s\nMethodology: %s\nContribution: %s\nRecommendation: %s\n""" %
            # (reviews[i]["reviewerid"],reviews[i]["datereceived"],reviews[i]["_id"],reviews[i]["title"],reviews[i]["reviews"],))
            # i+=1
        if (numReviews == 0):
            print("You currently have no manuscripts for which you are the reviewer.")
        # while row is not None:
        #     print("""ReviewerNum: %s\nDateSent: %s\nManuscript Number: %s\nManuscript Title: %s\nAppropriateness: %s\nClarity: %s\nMethodology: %s\nContribution: %s\nRecommendation: %s\n""" %
        #     (str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7]),str(row[8])))
        #     numManuscripts+=1
        #     row = cursor.fetchone()
        # if (numManuscripts == 0):
        #     print("You currently have no manuscripts for which you are the reviewer.")
        # cursor.close()
        # optionsReviewer(revid,con)
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
