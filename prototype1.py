import tkinter as tK
import mysql.connector
import hashlib


class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Passenger Vessel Management System")  # the window title
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen
        self.firstName = self.surName = self.phoneNum = self.DOB = self.NOK = ""

    def dbConnection(self, statement): # function to connect to the database, execute a statement and return the result
        try:
            self.conn = mysql.connector.connect(option_files="DBCredentials.conf")
            #self.conn = mysql.connector.connect(user=file.readline(), password=file.readline(), host=file.readline(), database=file.readline()) #connect to the database
            self.cur = self.conn.cursor() # database cursor
            self.cur.execute(statement) # executes the SQL statement in the database
            try:
                allResults = self.cur.fetchall() # returns all returned rows from executed statement
                self.conn.commit() # commit any changes to the database
                self.conn.close() # close the connection
                return allResults
            except Exception: # if it is a SELECT statement, there will be nothing to fetch = error
                self.conn.commit() # commit any changes to the database
                self.conn.close() # close the connection
                return 0

        except Exception as error: # catches any errors from the database connection and execution
            self.dbError(error) # generic database error, i.e. connection, login credentials or non-existant DB

    def dbError(self, error):
        self.forgetAllWidgets()
        header = tK.Label(text="Passenger Vessel Management System\n\n", font=("Calibri", 24)).pack(side="top")
        text1 = tK.Label(text="Error: Could not connect to the database\nPlease ensure XAMPP is running.\n\n", font=("Calibri", 21)).pack(side="top")
        text2 = tK.Label(text="Error: %s" % (error),font=("Calibri", 21)).pack(side="top")

    def forgetAllWidgets(self):    # hides a list of shown widgets
        widgetList = self.root.winfo_children() # all widgets (items) shown on the window
        for item in widgetList:
            if item.winfo_children():
                widgetList.extend(item.winfo_children())    # any sub-widgets
        for item in widgetList:
            item.pack_forget()  # hide all widgets / remove everything from the list of packed widgets

class userLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent): # constructor
        self.root = parent.root # inherit the root tkinter window from VesselManSys class
        self.credentialFailFlag = False # shows if user login credentials were correct or not - True if incorrect
        self.loginScreen()

    def loginScreen(self):
        if self.credentialFailFlag == True:
            failtext = tK.Label(text="Username or Password was incorrect - Please try again.\n\n\n\n\n\n", font=("Calibri", 20)).pack(side="bottom") # if user credentials incorrect, shows this at the bottom of window
        h1text = tK.Label(text="Passenger Vessel Management System\n\n", font=("Calibri", 28)).pack(side="top")  # window heading text centered at the top available space
        sidtext = tK.Label(text="Staff ID", font=("Calibri", 22)).pack(side="top")  # text left of entry box
        self.sidbox = tK.Entry(self.root, width=35) # text entry box for staff id
        sidboxpack = self.sidbox.pack(side="top") # place the text entry box on the screen
        pwtext = tK.Label(text="\nPassword", font=("Calibri", 22)).pack(side="top")  # text left of entry box
        self.pwbox = tK.Entry(self.root, width=35)  # text entry box for password
        pwboxpack = self.pwbox.pack(side="top") # place the text entry box on the screen
        loginBut = tK.Button(text="Log In", command=lambda : self.loginBackend()).pack(side="top") # login button - when clicked runs loginBackend function

    def loginBackend(self): # linked to the submit button on login page
        tempSID = self.sidbox.get() # gets the user input from staff id text box on login page
        if tempSID.isnumeric(): # validation to check if it is a number
            tempSID = int(tempSID)
            if tempSID > 0:
                self.staffID = tempSID
                self.password = self.pwbox.get() # gets the user input from password box on login screen
                statement = "SELECT * FROM Users WHERE StaffID = '%s' AND Password = '%s';" % (self.staffID, self.sha256hash(self.password)) # paramaterised StaffID & Password to avoid SQL injection
                resultTup = self.dbConnection(statement) # execute the above statement in the database
                if len(resultTup) == 1: # should only return maximum of 1 row
                    resultTup = resultTup[0]
                    self.firstName = str(resultTup[3])
                    self.surName = str(resultTup[4])
                    self.phoneNum = str(resultTup[5])   # String as could have hashtags or +
                    self.DOB = str(resultTup[6]) # Date Of Birth
                    self.NOK = str(resultTup[7]) # Name of Next Of Kin
                    self.credentialFailFlag = False
                    self.loginComplete()
                else:   # if no rows are returned, user login credentials were incorrect
                    self.credentialFailFlag = True
                    self.forgetAllWidgets() # clear screen of widgets
                    self.loginScreen()  # prompt user for login details again

    def sha256hash(self, string):   # hashes a string with SHA-256
        string = string.encode("utf-8") # encodes the string in utf-8
        hashobject = hashlib.sha256(string) # hashobject = location in memory of hash
        hashedstring = hashobject.hexdigest() # sets hashedstring as the hash from the hashobject
        return hashedstring # returns hash of original string

    def loginComplete(self):    # if user login credentials are valid
        if self.credentialFailFlag == False:
            self.forgetAllWidgets() # clear the screen
            print("Logged In")


class homePage(VesselManSys): # home screen - menu for the different program functionalities
    def __init__(self, parent):
        self.root = parent.root # inherit root from VesselManSys


class userAccountManager(VesselManSys): # screen for managing user accounts
    def __init__(self, parent):
        self.root = parent.root  # inherit the root tkinter window from VesselManSys class


def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    a = VesselManSys(root)
    vms = userLoginScreen(a)
    root.mainloop()


runApp()
