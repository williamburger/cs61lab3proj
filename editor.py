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

def assign(manNum,revId,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("INSERT INTO `Review` (`ManuscriptNum`,`ReviewerNum`,`DateReceived`) VALUES(%s,%s,STR_TO_DATE(%s,'%m/%d/%Y'))",(manNum,revId,time.strftime("%x")))
        con.commit()
        print('%s',time.strftime("%x"))
        print('INSERT COMPLETE')
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def reject(manNum,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("UPDATE `Manuscript` SET `Status` = 'rejected', `DateSent` = STR_TO_DATE(%s,'%m/%d/%Y') WHERE `ManuscriptNum`=%s",(time.strftime("%x"),manNum))
        con.commit()
        print('%s',time.strftime("%x"))
        print('Rejected ManuscriptNum ' + manNum)
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def accept(manNum,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("UPDATE `Manuscript` SET `Status` = 'accepted', `DateSent` = STR_TO_DATE(%s,'%m/%d/%Y') WHERE `ManuscriptNum`=%s",(time.strftime("%x"),manNum))
        con.commit()
        print('%s',time.strftime("%x"))
        print('Accepted ManuscriptNum ' + manNum)
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def typeset(manNum,pp,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("UPDATE `Manuscript` SET `Status` = 'typeset', `NumPages` = %s WHERE `ManuscriptNum`=%s",(pp,manNum))
        con.commit()
        print('%s',time.strftime("%x"))
        print('Rejected ManuscriptNum ' + manNum)
        cursor.close()
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def schedule(manNum,issueID,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT Status,NumPages FROM Manuscript WHERE ManuscriptNum=%s",(manNum,))
        row = cursor.fetchone()
        cursor.close()
        if(row[0] == 'accepted'):
            numPage = row[1]
            cursor = con.cursor()
            cursor.execute("SELECT NumPages FROM Issue WHERE idIssue=%s",(issueID,))
            row = cursor.fetchone()
            if(row!=None):
                if( (row[0]+numPage)<100):
                    cursor.execute("UPDATE Manuscript SET `Status`='scheduled',idIssue=%s,BeginningPageNum=%s WHERE ManuscriptNum=%s",(issueID,row[0],manNum,))
                    cursor.execute("UPDATE Issue SET NumPages = %s WHERE idIssue=%s",(row[0]+numPage,issueID,))
                    con.commit()
                else:
                    print('Manuscript has too many pages')
            else:
                print('could not find issue in system')
            cursor.close()
        else:
            print('status of manuscript is not accepted, cannot schedule at this time')
        statusCommand(edid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def publish(issueID,edid,con):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Manuscript WHERE idIssue=%s AND `Status`='scheduled' LIMIT 1",(issueID,))
        row = cursor.fetchone()
        print('here')
        if(row!=None):
            cursor.execute("UPDATE Manuscript SET `Status`='published' WHERE idIssue=%s",(issueID,))
            print('here')
            cursor.execute("UPDATE Issue SET PrintDate=STR_TO_DATE(%s,'%m/%d/%Y') WHERE idIssue=%s",(time.strftime("%x"),issueID,))
            con.commit()
        else:
            print('No Manuscripts for this issue that are scheduled to be published!')
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
    print("Enter 'SCHEDULE <manu#> <issueID>' to schedule an appearance in an issue that has less than 100 pages")
    print("Enter 'PUBLISH' <issueID> and set all manuscripts in the issue to Pulished")
    user_input = raw_input("\nEnter: ")
    user_input_words = user_input.split(' ')
    if(user_input == 'STATUS'):
        statusCommand(edid,con)
    elif(user_input_words[0] == 'ASSIGN'):
        assign(user_input_words[1],user_input_words[2],edid,con)
    elif(user_input_words[0] == 'REJECT'):
        reject(user_input_words[1],edid,con)
    elif(user_input_words[0] == 'ACCEPT'):
        accept(user_input_words[1],edid,con)
    elif(user_input_words[0] == 'TYPESET'):
        typeset(user_input_words[1],user_input_words[2],edid,con)
    elif(user_input_words[0] == 'SCHEDULE'):
        schedule(user_input_words[1],user_input_words[2],edid,con)
    elif(user_input_words[0] == 'PUBLISH'):
        publish(user_input_words[1],edid,con)
    else:
        print('EXITING PROGRAM')


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
