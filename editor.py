from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import utils
import getpass
from bson.objectid import ObjectId

# Register an Editor
# The editor ID will be handled in the database
# in createEditor will need to return the unique ID
def createEditor(name,db):
    try:
        newid = db.editors.insert_one({"name":name}).inserted_id
        print("Your unique id is " + str(newid))
        loginEditor(newid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerEditor(n,db):
    name = n
    if(name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
    createEditor(name,db)

def loginEditor(edid,db):

    try:
        result = db.editors.find_one({"_id":ObjectId(edid)})
        if(result["name"]==None):
            print('not a valid id')
            return;
        print('Welcome Back!')
        print(result["name"])
        statusCommand(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def assign(manNum,revId,edid,db):
    try:
        db.manuscript.find_one_and_update({"_id":ObjectId(manNum)},{"$push":{"reviewers":ObjectId(revId) }})
        statusCommand(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def reject(manNum,edid,db):
    try:
        result=db.manuscript.find_one_and_update({"_id":ObjectId(manNum)}, {"$set":{"status":"rejected","dateupdated":time.strftime("%x")}})
        print('Rejected ManuscriptNum ' + manNum)
        statusCommand(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def accept(manNum,edid,db):
    try:
        result=db.manuscript.find_one_and_update({"_id":ObjectId(manNum)}, {"$set":{"status":"accepted","dateupdated":time.strftime("%x")}})
        print('Accepted ManuscriptNum ' + manNum)
        statusCommand(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))


def typeset(manNum,pp,edid,db):
    try:
        result=db.manuscript.find_one_and_update({"_id":ObjectId(manNum)}, {"$set":{"status":"typeset","dateupdated":time.strftime("%x"),"numpages":pp}})
        print('Typeset ManuscriptNum ' + manNum)
        statusCommand(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def schedule(manNum,issueID,edid,db):
    try:
        print("finding one")
        result = db.manuscript.find_one({"_id":ObjectId(manNum)})
        print("found one")
        if(result["_id"]):
            print("checking status")
            if(result["status"]=="accepted"):
                print("before")
                pipeline = [
                    {"$match":{"idissue":ObjectId(issueID)}

                    },
                    { "$group":
                        {
                            "_id": "$idissue",
                            "numpages": {"$sum": "$numpages"}
                        }
                    }
                ]
                issue = list(db.manuscript.aggregate(pipeline))
                issue = issue[0]
                print("after")
                print(issue)
                if(result["numpages"]+issue["numpages"]>100):
                    print("too many pages to schedule\n")
                    statusCommand(edid,db)
                else:
                    result=db.manuscript.find_one_and_update({"_id":ObjectId(manNum)}, {"$set":{"status":"scheduled","dateupdated":time.strftime("%x"),"idissue":issueID}})
                    print('Scheduled ManuscriptNum ' + manNum)
                    statusCommand(edid,db)

            else:
                print("Manuscript was not previously accepted")
                statusCommand(edid,db)

        else:
            print("Manuscript not found")

    except pymongo.errors.ServerSelectionTimeoutError as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))


def publish(issueID,edid,db):
    try:
        result = list(db.manuscript.find({"idissue":issueID,"status":"scheduled"}))
        if(len(result)==0):
            print('No Manuscripts for this issue that are scheduled to be published!')
            statusCommand(edid,db)
        else:
            for item in result:
                db.manuscript.find_one_and_update({"idissue":issueID},{"$set":{"status":"published","dateupdated":time.strftime("%x")}})
        db.issues.find_one_and_update({"_id":issueID},{"$set":{"printDate":time.strftime("%x")}})
        statusCommand(edid,db)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def optionsEditor(edid,db):
    print("Enter 'STATUS' to view all manuscripts in the system")
    print("Enter 'ASSIGN <manu#> <reviewer id>' to assign a manuscript to be reviewed by a reviewer with timestamp")
    print("Enter 'REJECT <manu#>' to set the manuscript to rejected with timestamp")
    print("Enter 'ACCEPT <manu#>' to set the manuscript to accepted with timestamp")
    print("Enter 'TYPESET <manu#> <pp>' to set the manuscript to typeset and enter the page numbers")
    print("Enter 'SCHEDULE <manu#> <issueID>' to schedule an appearance in an issue that has less than 100 pages")
    print("Enter 'PUBLISH' <issueID> and set all manuscripts in the issue to Pulished")
    user_input = raw_input("\nEnter: ")
    user_input_words = user_input.split(' ')
    if(user_input == 'STATUS'):
        statusCommand(edid,db)
    elif(user_input_words[0] == 'ASSIGN'):
        assign(user_input_words[1],user_input_words[2],edid,db)
    elif(user_input_words[0] == 'REJECT'):
        reject(user_input_words[1],edid,db)
    elif(user_input_words[0] == 'ACCEPT'):
        accept(user_input_words[1],edid,db)
    elif(user_input_words[0] == 'TYPESET'):
        typeset(user_input_words[1],user_input_words[2],edid,db)
    elif(user_input_words[0] == 'SCHEDULE'):
        schedule(user_input_words[1],user_input_words[2],edid,db)
    elif(user_input_words[0] == 'PUBLISH'):
        publish(user_input_words[1],edid,db)
    else:
        print('EXITING PROGRAM')


def statusCommand(edid,db):
    try:
        result = db.manuscript.find({"editorid":ObjectId(edid)}).sort([("status",1), ("_id",1)])
        # cursor.execute("SELECT ManuscriptNum,Title,status,DateReceived FROM Manuscript WHERE EditorID=%s ORDER BY status, DateReceived",(edid,))
        print("\n")
        print('| %30s |||| %30s |||| %30s |' % ("Manuscript Title","Status","Manuscript Number"))
        for post in result:
            print('| %30s |||| %30s |||| %30s |' % (post["title"],post["status"],post["_id"]))
        print("\n")
        if(result == None):
            print("You currently have no manuscripts for which you are the editor.")
        optionsEditor(edid,db)
    except pymongo.errors.ServerSelectionTimeoutError as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))
