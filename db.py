from __future__ import print_function        # make print a function
import pymongo                  # mysql functionality
from pymongo import MongoClient
from bson.objectid import ObjectId
import sys                                   # for misc errors
import time
import getpass
import editor
import utils
import reviewer
import random


def AuthorStatus(authorId,db):
    try:
        manuscripts = db.manuscript.find({ "authors.0": ObjectId(authorId)})
        numManuscripts = manuscripts.count()
        i = 0
        while i < numManuscripts:
            print("""\nManuscript Number: %s\nManuscript Title: %s\nStatus: %s\nDate Received: %s\n""" %
            ((manuscripts[i]["_id"]),(manuscripts[i]["title"]),(manuscripts[i]["status"]),(manuscripts[i]["datereceived"]),))
            i+=1
        if (numManuscripts == 0):
            print("You currently have no manuscripts for which you are the lead author.")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def AuthorSubmit(authorId,db):
    print("Enter:\n"
        "<title>\n"
        "<Affiliation>\n"
        "<RICode>\n"
        "<author2> ... <authorN>\n"
        "<filename>\n")
    print("Where <title> is the title of your ManuscriptID\n"
    "<RICode> is the subject area of the Manuscript.\n"
    "<author2> ... <authorN> are the contributing authors\n"
    "<filename> is the your uploaded manuscript\n")
    user_input = raw_input("Enter Title: ")
    title = user_input
    user_input = raw_input("Enter Affiliation: ")
    try:
        Affiliation = int(user_input)
        if (Affiliation < 1 or Affiliation > 123):
            print("RICode must be between 1 and 123")
            AuthorSubmit(authorId,db)
    except:
        print('Affiliation must be an integer between 1 and 123')
        AuthorSubmit(authorId,db)
    user_input = raw_input("Enter Number of Contributing Authors: ")
    try:
        numAuthors = int(user_input)
    except:
        print('Number of Contributing Authors must be an integer.')
        AuthorSubmit(authorId,db)
    i = 0
    extraAuthors = []
    while (i<numAuthors):
        user_input = raw_input("Enter Author %d's id: " % (i+1))
        extraAuthors.append(ObjectId(user_input))
        i=i+1

    user_input = raw_input("Enter fileName: ")
    fileName = user_input
    try:
        i=0
        alreadyRegistered = True
        offendingAuthor = None
        while (i<numAuthors):
            a = db.authors.find({ "_id":extraAuthors[i] }).count()
            if (a == 0):
                alreadyRegistered = False
                offendingAuthor = extraAuthors[i]
                break;
            i+=1
        if (alreadyRegistered == False):
            print("Author with id %s is not in our database. Please have them register and try again.\n" % (offendingAuthor))
            return
        anEditor = db.editors.find_one()["_id"]

        datereceived = time.strftime('%m/%d/%Y')
        print(datereceived)
        authors = [ObjectId(authorId)] + extraAuthors

        newManuscriptId = db.manuscript.insert_one({ "title":title, "datereceived":datereceived, "authors":authors, "reviews": [], "status": "submitted", "dateupdated":datereceived, "numpages": 3, "ricode":Affiliation, "editorid":anEditor, "document":fileName}).inserted_id
        print("Your Manuscript was added to our system with the system-wide unique id: %s\n" % newManuscriptId)

    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def ManuscriptRetract(authorId,manuscriptNum,db):
    print("Are you sure you want to delete manuscript %s?" % manuscriptNum)
    user_input = raw_input("y/n: " )
    if (user_input == "y"):
        try:
            manCount  = db.manuscript.find({ "_id":ObjectId(manuscriptNum), "authors.0":ObjectId(authorId) }).count()
            if (manCount > 0):
                db.manuscript.delete_one({ "_id":ObjectId(manuscriptNum)})
                print("Manuscript %s successfully deleted." % (str(manuscriptNum)))
            else:
                print("You are either not the primary author on that manuscript or it does not exist, so you can't delete it.\n")
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print("Connection Failure")
            print(err)
        except:                                   # anything else
            print("Unexpected error: {0}".format(sys.exc_info()[0]))
    elif (user_input == "n"):
        print("Cancelling...\n")
    else:
        print("Not Sure what that means. Try again.\n")
        ManuscriptRetract(authorId,manuscriptNum,db)

def GiveAuthorOptions(authorId,db):
    print("Enter 'STATUS' to review all of your manuscripts in the system for which you are the primary author.")
    print("Enter 'SUBMIT' to begin the process of submitting a manuscript for review.")
    print("Enter 'RETRACT ManuscriptID' to remove one of your manuscripts with its given ID.")
    user_input = raw_input("\nEnter: ")
    user_input_words = user_input.split(' ')
    if (len(user_input_words) > 2 or len(user_input_words) < 1):
        print("That's not a properly formed command. Please Try Again.")
    if (user_input == "STATUS"):
        AuthorStatus(authorId,db)
    elif (user_input == "SUBMIT"):
        AuthorSubmit(authorId,db)
    elif (user_input_words[0] == "RETRACT"):
        if (len(user_input_words)==2):
            manId = user_input_words[1]
            ManuscriptRetract(authorId,user_input_words[1],db)
    else:
        print("Uh Oh. That's not a properly formed command. Please Try again.")
        GiveAuthorOptions(authorId,db)
    GiveAuthorOptions(authorId,db)

def loginAuthor(authorId,db):
    try:
        author = db.authors.find_one({"_id": ObjectId(authorId)})
        print('Welcome Back!\n')
        print ("Name: %s" % (author["name"]))
        print("Address: %s" % (author["address"]))
        AuthorStatus(authorId,db)
        GiveAuthorOptions(authorId,db)
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def createAuthor(name, email, address, affiliation,db):

     try:
         newid = db.authors.insert_one({ "name": name, "email": email, "address": address, "affiliation": affiliation }).inserted_id
         print("Your unique id is %s" % str(newid))
         loginAuthor(str(newid),db)
     except pymongo.errors.ServerSelectionTimeoutError as err:
         print("Connection Failure")
         print(err)
     except:                                   # anything else
         print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerAuthor(n, e, a,aff,db):
    name = n
    email = e
    address = a
    affiliation = aff

    if (name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
    if (address is None):
        user_input = raw_input("Please enter your home address.\n")
        address = user_input
    if (affiliation is None):
        user_input = raw_input("Please enter your affiliation.\n")
        affiliation = user_input

    createAuthor(name, email, address, affiliation,db)

if __name__ == "__main__":
    try:
        HOST = "mongodb://Team23:Muv58mTtDaweFhrU@cluster0-shard-00-00-ppp7l.mongodb.net:27017,cluster0-shard-00-01-ppp7l.mongodb.net:27017,cluster0-shard-00-02-ppp7l.mongodb.net:27017/Team23DB?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin"
        client = MongoClient(HOST);
        db = client.Team23DB

        print("Connection established. Welcome.\n")

        user_input = raw_input("If You're an Author, Enter 'Author' \n"
        "If You're an Editor, Enter 'Editor' \n"
        "If You're a Reviewer, Enter 'Reviewer'\n"
        "To Logout, Enter 'Logout'\n")
        if (user_input == 'Author'):
            user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
            "Otherwise, type 'Register'\n")
            if (user_input == 'Register'):
                registerAuthor(None, None, None, None, db)
            else:
                loginAuthor(user_input, db)
        elif (user_input == 'Editor'):
            user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
            "Otherwise, type 'Register'\n")
            if (user_input == 'Register'):
                editor.registerEditor(None,db)
            else:
                editor.loginEditor(user_input,db)
        elif (user_input == 'Reviewer'):
            user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
            "If You wish to resign, type 'RESIGN <id>'\n"
            "Otherwise, type 'Register'\n")
            inputArr = user_input.split(' ')
            if (user_input == 'Register'):
                reviewer.registerReviewer(None,None,None,None,None,db)
            elif(inputArr[0] =='RESIGN'):
                reviewer.resign(inputArr[1],db)
            else:
                reviewer.loginReviewer(user_input,db)
        elif (user_input == "Logout"):
            print("Ta ta for now!\n")
        else:
            print("Shutting down.\n")
    except pymongo.errors.ServerSelectionTimeoutError as err:        # catch errors
        print("Connection Failure")
        print(err)
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))
