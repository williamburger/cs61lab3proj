from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors
import time
import getpass
import editor
import utils
import reviewer
import random

SERVER   = "sunapee.cs.dartmouth.edu"        # db server to connect to
USERNAME = "aogren"                            # user to connect as
PASSWORD = "Kellyo1995"                            # user's password
DATABASE = "aogren_db"                              # db to user
MASTER_KEY = ''



def AuthorStatus(authorId):
    try:
        cursor = con.cursor()
        cursor.execute("SELECT `ManuscriptNum`,`Title`,`status`,`DateReceived` FROM LeadAuthorManuscripts WHERE AuthorID=%s",(authorId,))
        row = cursor.fetchone()
        numManuscripts = 0
        while row is not None:
            print("""\nManuscript Number: %s\nManuscript Title: %s\nStatus: %s\nDate Received: %s\n""" %
            (str(row[0]),str(row[1]),str(row[2]),str(row[3])))
            numManuscripts+=1
            row = cursor.fetchone()
        if (numManuscripts == 0):
            print("You currently have no manuscripts for which you are the lead author.")
        cursor.close()
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def AuthorSubmit(authorId):
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
    Affiliation = int(user_input)
    if (Affiliation < 1 or Affiliation > 123):
        print("RICode must be between 1 and 123")
        AuthorSubmit(authorId)
    user_input = raw_input("Enter Number of Contributing Authors: ")
    numAuthors = int(user_input)
    i = 0
    extraAuthors = []
    while (i<numAuthors):
        user_input = raw_input("Enter Author %d's id: " % (i+1))
        try:
            int(user_input)
        except ValueError:
            print("\nThat is an invalid id\n")
            return
        extraAuthors.append(user_input)
        i=i+1

    user_input = raw_input("Enter fileName: ")
    fileName = user_input
    try:
        cursor = con.cursor()
        i=0
        alreadyRegistered = True
        offendingAuthor = None
        while (i<numAuthors):
            cursor.execute("""SELECT COUNT(*) FROM Author WHERE AuthorID=%s""",(extraAuthors[i],))
            result = cursor.fetchone()
            if (int(result[0]) == 0):
                alreadyRegistered = False
                offendingAuthor = extraAuthors[i]
                break;
            i+=1

        if (alreadyRegistered == False):
            print("Author with id %d is not in our database. Please have them register and try again.\n" % int(offendingAuthor))
            return
        print('here\n')
        cursor.execute("""SELECT MAX(EditorID) AS EditorID FROM Editor""")
        row = cursor.fetchone()
        print(row[0])
        editor = random.randint(1,int(row[0]))
        print(type(editor))
        cursor.execute("INSERT INTO Manuscript (`Title`,`DateReceived`,`Status`,`DateSent`,`NumPages`,`Order`,`BeginningPageNum`,`idIssue`,`RICode`,`EditorID`) VALUES (%s,STR_TO_DATE(%s,'%m/%d/%Y'),%s,%s,%s,%s,%s,%s,%s,%s)",(title,time.strftime("%x"),"submitted",None,None,None,None,None,Affiliation,str(editor),))
        con.commit()
        manuscriptNum = cursor.lastrowid
        print("Your Manuscript was added to our system with the system-wide unique id: %d\n" % manuscriptNum)
        #insert into Authored here
        cursor.execute("""INSERT INTO Authored (`AuthorID`,`ManuscriptNum`,`AuthorOrder`) VALUES (%s,%s,%s)""",(int(authorId),int(manuscriptNum),1,))
        con.commit()
        i = 0
        while (i<numAuthors):
            cursor.execute("""INSERT INTO Authored (`AuthorID`,`ManuscriptNum`,`AuthorOrder`) VALUES (%s,%s,%s)""",(int(extraAuthors[i]),int(manuscriptNum),i+2))
            con.commit()
            i+=1
        cursor.execute("""INSERT INTO blob_table (`ManuscriptNum`,`paper`) VALUES (%s,%s)""",(int(manuscriptNum),fileName))
        con.commit()

        cursor.close()

    except mysql.connector.Error as e:
        print("SQL Error: {0}".format(e.msg))
    except:
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def ManuscriptRetract(authorId,manuscriptNum):
    manuscriptNum = int(manuscriptNum)
    print("Are you sure you want to delete manuscript %d?" % manuscriptNum)
    user_input = raw_input("y/n: " )
    if (user_input == "y"):
        try:
            cursor = con.cursor()
            cursor.execute("""SELECT * FROM Authored WHERE AuthorID=%s AND ManuscriptNum=%s""",(authorId,manuscriptNum,))
            result = cursor.fetchone()
            numResults = 0
            while result is not None:
                numResults=numResults+1
                result=cursor.fetchone()
            if (numResults > 0):
                cursor.execute("""DELETE FROM Manuscript WHERE ManuscriptNum=%s """,(manuscriptNum,))
                con.commit()
            else:
                print("You are either not the primary author on that manuscript or it does not exist, so you can't delete it.\n")
            cursor.close()
        except mysql.connector.Error as e:
            print("SQL Error: {0}".format(e.msg))
        except:
            print("Unexpected error: {0}".format(sys.exc_info()[0]))
    elif (user_input == "n"):
        print("Cancelling...\n")
    else:
        print("Not Sure what that means. Try again.\n")
        ManuscriptRetract(authorId,manuscriptNum)

def GiveAuthorOptions(authorId):
    print("Enter 'STATUS' to review all of your manuscripts in the system for which you are the primary author.")
    print("Enter 'SUBMIT' to begin the process of submitting a manuscript for review.")
    print("Enter 'RETRACT ManuscriptID' to remove one of your manuscripts with its given ID.")
    user_input = raw_input("\nEnter: ")
    user_input_words = user_input.split(' ')
    if (len(user_input_words) > 2 or len(user_input_words) < 1):
        print("That's not a properly formed command. Please Try Again.")
    if (user_input == "STATUS"):
        AuthorStatus(authorId)
    elif (user_input == "SUBMIT"):
        AuthorSubmit(authorId)
    elif (user_input_words[0] == "RETRACT"):
        if (len(user_input_words)==2):
            manId = user_input_words[1]
            try:
                int(manId)
                ManuscriptRetract(authorId,user_input_words[1])
            except ValueError:
                print("That's not a proper manuscript id. Try again.")
    else:
        print("Uh Oh. That's not a properly formed command. Please Try again.")
        GiveAuthorOptions(authorId)
    GiveAuthorOptions(authorId)

def loginAuthor(authorId, password):
    try:
        cursor = con.cursor()
        cursor.execute("""SELECT * FROM authorCredentials WHERE `password`=AES_ENCRYPT(%s,%s) AND `AuthorID`=%s""",(password,MASTER_KEY,authorId,))
        row = cursor.fetchone()
        if (row == None):
            print("Sorry, that's an invalid ID and Password combination.\n")
        else:
            cursor.execute("""SELECT FirstName, MiddleName, LastName, Address FROM Author WHERE AuthorID=%s""", (authorId,))
            row = cursor.fetchone()
            while row is not None:
                print('Welcome Back!\n')
                print ("Name: %s %s %s" % (str(row[0]),str(row[1]),str(row[2])))
                print("Address: %s" % (str(row[3])))
                row = cursor.fetchone()
            cursor.close()

            AuthorStatus(authorId)
            GiveAuthorOptions(authorId)

    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def createAuthor(name, email, address, password):
     POST = ""
     PARAMS = None
     try:
         cursor = con.cursor()
         if (len(name) == 2):
              POST = "INSERT INTO Author (FirstName,MiddleName,LastName,AuthorEmail,Address,Affiliation) VALUES (%s,%s,%s,%s,%s,%s)"
              PARAMS = (name[0],None,name[1],email,address,None)
         else:
              POST = "INSERT INTO Author (FirstName,MiddleName,LastName,AuthorEmail,Address,Affiliation) VALUES (%s,%s,%s,%s,%s,%s)"
              PARAMS = (name[0],name[1],name[2],email,address,None)

         cursor.execute(POST,PARAMS)
         con.commit()
         newid = cursor.lastrowid
         print("Your unique id is %s" % str(newid))

         #Enter password
         cursor.execute("""INSERT INTO authorCredentials (`password`,`AuthorID`) VALUES (AES_ENCRYPT(%s,%s),%s)""",(password,MASTER_KEY,int(newid),))
         con.commit()
         cursor.close()
         loginAuthor(str(newid), password)
     except mysql.connector.Error as e:        # catch SQL errors
         print("SQL Error: {0}".format(e.msg))
     except:                                   # anything else
         print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerAuthor(n, e, a,p,p2):
    name = n
    email = e
    address = a
    password = p
    passwordConfirm = p2
    nameArr = None
    if (name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
        nameArr = name.split(' ')
        if (utils.checkLength(name, 135)):
            name = None
            registerAuthor(name, email, address, password,passwordConfirm)
        elif (len(nameArr) < 2 or len(nameArr) > 3):
            name = None
            print('Your name must be 2 to 3 words in length. Sorry for any inconvenience. Try again.\n')
            registerAuthor(name, email, address, password, passwordConfirm)
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
        if utils.checkLength(email, 100):
            email = None
            registerAuthor(name, email, address, password, passwordConfirm)
    if (address is None):
        user_input = raw_input("Please enter your home address.\n")
        address = user_input
        if utils.checkLength(address, 100):
            address = None
            registerAuthor(name, email, address, password, passwordConfirm)
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
        registerAuthor(None,None,None,None,None)


    createAuthor(nameArr, email, address, password)

if __name__ == "__main__":
    try:
      # initialize db connection
      con = mysql.connector.connect(host=SERVER,user=USERNAME,password=PASSWORD,
                                    database=DATABASE)

      print("Connection established. Welcome.\n")
      user_input = raw_input("First, please enter the master key for encrypting passwords: ")
      MASTER_KEY = user_input

      user_input = raw_input("If You're an Author, Enter 'Author' \n"
                             "If You're an Editor, Enter 'Editor' \n"
                             "If You're a Reviewer, Enter 'Reviewer'\n"
                             "To Logout, Enter 'Logout'\n")
      if (user_input == 'Author'):
         user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
                "Otherwise, type 'Register'\n")
         if (user_input == 'Register'):
             registerAuthor(None, None, None,None, None)
         else:
             password = getpass.getpass("Please enter your password: ")
             loginAuthor(user_input, password)
      elif (user_input == 'Editor'):
          user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
                 "Otherwise, type 'Register'\n")
          if (user_input == 'Register'):
                editor.registerEditor(None,None,None,MASTER_KEY,con)
          else:
                password = getpass.getpass("Please enter your password: ")
                editor.loginEditor(user_input,password,MASTER_KEY,con)
      elif (user_input == 'Reviewer'):
          user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
                 "If You wish to resign, type 'RESIGN <id>'\n"
                 "Otherwise, type 'Register'\n")
          inputArr = user_input.split(' ')
          if (user_input == 'Register'):
                reviewer.registerReviewer(None,None,None,None,None,MASTER_KEY,con)
          elif(inputArr[0] =='RESIGN'):
                reviewer.resign(inputArr[1],con)
          else:
                password = getpass.getpass("Please enter your password: ")
                reviewer.loginReviewer(user_input,password,MASTER_KEY,con)
      elif (user_input == "Logout"):
          print("Ta ta for now!\n")
          con.close()
      else:
          print("Shutting down.\n")
    except mysql.connector.Error as e:        # catch SQL errors
     print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
     print("Unexpected error: {0}".format(sys.exc_info()[0]))
    con.close()
