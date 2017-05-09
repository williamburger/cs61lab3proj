from __future__ import print_function        # make print a function
import mysql.connector                       # mysql functionality
import sys                                   # for misc errors

SERVER   = "sunapee.cs.dartmouth.edu"        # db server to connect to
USERNAME = "aogren"                            # user to connect as
PASSWORD = "Kellyo1995"                            # user's password
DATABASE = "aogren_db"                              # db to user

def checkLength(strang, length):
    if (len(strang) > length):
        print("Error: Cannot exceed %d characters. Please try again." % (length))
        return True

def loginAuthor(authorId):
    print(type(authorId))
    try:
        cursor = con.cursor()
        print('about to query')
        cursor.execute("""SELECT FirstName, MiddleName, LastName, Address FROM Author WHERE AuthorID=%s""", (authorId,))
        row = cursor.fetchone()
        while row is not None:
            print('Welcome Back!\n')
            print ("Name: %s %s %s" % (str(row[0]),str(row[1]),str(row[2])))
            print("Address: %s" % (str(row[3])))
            row = cursor.fetchone()
        cursor.close()
    except mysql.connector.Error as e:        # catch SQL errors
        print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
        print("Unexpected error: {0}".format(sys.exc_info()[0]))

def createAuthor(name, email, address):
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
         print("Your unique id is %s", str(newid))
         cursor.close()
         loginAuthor(str(newid))
     except mysql.connector.Error as e:        # catch SQL errors
         print("SQL Error: {0}".format(e.msg))
     except:                                   # anything else
         print("Unexpected error: {0}".format(sys.exc_info()[0]))

def registerAuthor(n, e, a):
    name = n
    email = e
    address = a
    nameArr = None
    if (name is None):
        user_input = raw_input("Please enter your full name.\n")
        name = user_input
        nameArr = name.split(' ')
        if (checkLength(name, 135)):
            name = None
            registerAuthor(name, email, address)
        elif (len(nameArr) < 2 or len(nameArr) > 3):
            name = None
            print('Your name must be 2 to 3 words in length. Sorry for any inconvenience. Try again.\n')
            registerAuthor(name, email, address)
    if (email is None):
        user_input = raw_input("Please enter your email address.\n")
        email = user_input
        if checkLength(email, 100):
            email = None
            registerAuthor(name, email, address)
    if (address is None):
        user_input = raw_input("Please enter your home address.\n")
        address = user_input
        if checkLength(address, 100):
            address = None
            registerAuthor(name, email, address)
    createAuthor(nameArr, email, address)

if __name__ == "__main__":
    try:
      # initialize db connection
      con = mysql.connector.connect(host=SERVER,user=USERNAME,password=PASSWORD,
                                    database=DATABASE)

      print("Connection established. Welcome.")

      user_input = raw_input("If You're an Author, Enter 'Author' \n"
                             "If You're an Editor, Enter 'Editor' \n"
                             "If You're a Reviewer, Enter 'Reviewer'\n")
      if (user_input == 'Author'):
         user_input = raw_input("If you have previously signed up, login by typing in your unique id.\n"
                "Otherwise, type 'Register'\n")
         if (user_input == 'Register'):
             registerAuthor(None, None, None)
         else:
             loginAuthor(user_input)
      elif (user_input == 'Editor'):
          print('yahoo')
      elif (user_input == 'Reviewer'):
          print('wasup')
      else:
          print('Oh no')

    except mysql.connector.Error as e:        # catch SQL errors
     print("SQL Error: {0}".format(e.msg))
    except:                                   # anything else
     print("Unexpected error: {0}".format(sys.exc_info()[0]))
    con.close()
