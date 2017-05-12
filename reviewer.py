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

####THIS IS NOT DONE YET, STILL TRYING TO FIGURE IT OUT
def statusCommand(revid,con):
    try:
        cursor = con.cursor()
        args = (1)
        cursor.execute("SELECT * FROM ReviewStatusAll WHERE ReviewerNum=%s",(revid,))

        row = cursor.fetchone()

        numManuscripts = 0
        while row is not None:
            print("""ReviewerNum: %s\nDateSent: %s\nManuscript Number: %s\nManuscript Title: %s\nAppropriateness: %s\nClarity: %s\nMethodology: %s\nContribution: %s\nRecommendation: %s\n""" %
            (str(row[0]),str(row[1]),str(row[2]),str(row[3]),str(row[4]),str(row[5]),str(row[6]),str(row[7]),str(row[8])))
            numManuscripts+=1
            row = cursor.fetchone()
        if (numManuscripts == 0):
            print("You currently have no manuscripts for which you are the reviewer.")
        cursor.close()
        optionsReviewer(revid,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def loginReviewer(revid,password,master,con):
    try:
        cursor = con.cursor()
        cursor.execute("""SELECT * FROM reviewerCredentials WHERE `password`=AES_ENCRYPT(%s,%s) AND `ReviewerNum`=%s """,(password,master,revid,))
        row = cursor.fetchone()
        if (row == None):
            print("Sorry, that's an invalid ID and Password combination.\n")
        else:
            cursor.execute("SELECT FirstName, MiddleName, LastName FROM Reviewer WHERE ReviewerNum=%s AND `Status`='active'",(revid,))
            row = cursor.fetchone()
            if(row==None):
                print('No longer an active reviewer')
                return
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

def createReviewer(name,email,affiliation,password,master,con):
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
        cursor.execute("""INSERT INTO reviewerCredentials (`password`,`ReviewerNum`) VALUES (AES_ENCRYPT(%s,%s),%s)""",(str(password),str(master),int(newid),))
        con.commit()
        cursor.close()
        loginReviewer(newid,password,master,con)
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerReviewer(n,e,a,p,p2,master,con):
    name = n
    email = e
    affiliation = a
    password = p
    passwordConfirm = p2
    if(name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
        nameArr = name.split(' ')
        if (utils.checkLength(name, 135)):
            name = None
            registerReviewer(name,email,affiliation,password,passwordConfirm,master,con)
        elif (len(nameArr) < 2 or len(nameArr) > 3):
            name = None
            print('Your name must be 2 to 3 words in length. Sorry for any inconvenience. Try again.\n')
            registerReviewer(name,email,affiliation,password,passwordConfirm,master,con)
    nameArr = name.split(' ')
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
        if utils.checkLength(email, 100):
            email = None
            registerReviewer(name,email,affiliation,password,passwordConfirm,master,con)
    if (affiliation is None):
        user_input = raw_input("Please enter your affiliation.\n")
        affiliation = user_input
        if utils.checkLength(affiliation, 100):
            affiliation = None
            registerReviewer(name,email,affiliation,password,passwordConfirm,master,con)
    if (password is None):
        # user_input = raw_input("Please enter a password: \n")
        user_input = getpass.getpass("Password: ")
        password = user_input
    if (passwordConfirm is None):
        # user_input = raw_input("Please confirm password: \n")
        user_input = getpass.getpass("Please confirm password: ")
        passwordConfirm = user_input
    if (password != passwordConfirm):
        print("Sorry, those passwords did not match. Try registering again.")
        registerReviewer(None,None,None,None,None,master,con)
    createReviewer(nameArr,email,affiliation,password,master,con)
