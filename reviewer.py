from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import utils

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

####THIS IS NOT DONE YET, STILL TRYING TO FIGURE IT OUT
def statusCommand(revid,conn):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT ManuscriptNum,Title,status,DateReceived FROM Manuscript WHERE ReviewerNum=%s ORDER BY status, DateReceived",(revid,))
        row = cursor.fetchone()
        numManuscripts = 0
        while row is not None:
            print("""\nManuscript Number: %s\nManuscript Title: %s\nStatus: %s\nDate Received: %s\n""" %
            (str(row[0]),str(row[1]),str(row[2]),str(row[3])))
            numManuscripts+=1
            row = cursor.fetchone()
        if (numManuscripts == 0):
            print("You currently have no manuscripts for which you are the editor.")
        cursor.close()
        optionsEditor(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def loginReviewer(revid,con):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT FirstName, MiddleName, LastName FROM Editor WHERE EditorID=%s",(revid,))
        row = cursor.fetchone()
        while row is not None:
            print('Welcome Back!\n')
            print("Name: %s %s %s" % (str(row[0]),str(row[1]),str(row[2])))
            row = cursor.fetchone()
        cursor.close()
        statusCommand(revid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def createReviewer(name,email,affiliation,con):
    POST = ""
    PARAMS = None
    try:
        cursor=con.cursor()
        if(len(name)==2):
            POST = "INSERT INTO Reviewer (FirstName,MiddleName,LastName,ReviewerEmail,Affiliation) VALUES (%s,%s,%s,%s,%s)"
            PARAMS = (name[0],None,name[1],email,affiliation)
        else:
            POST = "INSERT INTO Reviewer (FirstName,MiddleName,LastName,ReviewerEmail,Affiliation) VALUES (%s,%s,%s,%s,%s)"
            PARAMS = (name[0],name[1],name[2],email,affiliation)
        cursor.execute(POST,PARAMS)
        con.commit()
        newid = cursor.lastrowid
        print("Your unique id is " + str(newid))
        cursor.close()
        loginReviewer(newid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerReviewer(n,e,a,con):
    name = n
    email = e
    affiliation = a
    if(name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
        nameArr = name.split(' ')
        if (utils.checkLength(name, 135)):
            name = None
            registerReviewer(name)
        elif (len(nameArr) < 2 or len(nameArr) > 3):
            name = None
            print('Your name must be 2 to 3 words in length. Sorry for any inconvenience. Try again.\n')
            registerReviewer(name)
    nameArr = name.split(' ')
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
        if utils.checkLength(email, 100):
            email = None
            registerReviewer(name, email, affiliation)
    if (affiliation is None):
        user_input = raw_input("Please enter your affiliation.\n")
        affiliation = user_input
        if utils.checkLength(affiliation, 100):
            affiliation = None
            registerReviewer(name, email, affiliation)
    createReviewer(nameArr,email,affiliation,con)
