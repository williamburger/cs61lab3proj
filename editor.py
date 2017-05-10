from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import utils

# Register an Editor
# The editor ID will be handled in the database
# in createEditor will need to return the unique ID
def createEditor(name,con):
    POST = ""
    PARAMS = None
    try:
        cursor=con.cursor()
        if(len(name)==2):
            POST = "INSERT INTO Editor (FirstName,MiddleName,LastName) VALUES (%s,%s,%s)"
            PARAMS = (name[0],None,name[1])
        else:
            POST = "INSERT INTO Editor (FirstName,MiddleName,LastName) VALUES (%s,%s,%s)"
            PARAMS = (name[0],name[1],name[2])
        cursor.execute(POST,PARAMS)
        con.commit()
        newid = cursor.lastrowid
        print("Your unique id is " + str(newid))
        cursor.close()
        loginEditor(newid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerEditor(n,con):
    name = n
    if(name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
        name = user_input
        nameArr = name.split(' ')
        if (utils.checkLength(name, 135)):
            name = None
            registerEditor(name)
        elif (len(nameArr) < 2 or len(nameArr) > 3):
            name = None
            print('Your name must be 2 to 3 words in length. Sorry for any inconvenience. Try again.\n')
            registerEditor(name)
    nameArr = name.split(' ')
    createEditor(nameArr,con)

def loginEditor(edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT FirstName, MiddleName, LastName FROM Editor WHERE EditorID=%s",(edid,))
        row = cursor.fetchone()
        while row is not None:
            print('Welcome Back!\n')
            print("Name: %s %s %s" % (str(row[0]),str(row[1]),str(row[2])))
            row = cursor.fetchone()
        cursor.close()
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def optionsEditor(edid,con):
    print("Enter 'STATUS' to view all manuscripts in the system")
    print("Enter 'ASSIGN <manu#> <reviewer id>' to assign a manuscript to be reviewed by a reviewer with timestamp")
    print("Enter 'REJECT <manu#>' to set the manuscript to rejected with timestamp")
    print("Enter 'ACCEPT <manu#>' to set the manuscript to accepted with timestamp")
    print("Enter 'TYPESET <manu#> <pp>' to set the manuscript to typeset and enter the page numbers")
    print("Enter 'SCHEDULE <manu#> <issue>' to schedule an appearance in an issue that has less than 100 pages")
    print("Enter 'PUBLISH' <issue> and set all manuscripts in the issue to Pulished")
    user_input = raw_input("\nEnter: ")
    user_input_words = user_input.split(' ')
    if(user_input == 'STATUS'):
        statusCommand(edid,con)


def statusCommand(edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT ManuscriptNum,Title,status,DateReceived FROM Manuscript WHERE EditorID=%s ORDER BY status, DateReceived",(edid,))
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
