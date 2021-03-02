import tkinter as tK
import mysql.connector
import hashlib
import urllib.request


class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Passenger Vessel Management System")  # the window title
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen
        self.root.configure(bg="sky blue")
        self.firstName = self.surName = self.phoneNum = self.DOB = self.NOK = ""

    def dbConnection(self, statement): # function to connect to the database, execute a statement and return the result
        try:
            self.conn = mysql.connector.connect(option_files="DBCredentials.conf") # opens file and reads database credentials from it
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
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 24), bg="sky blue").pack(side="top")
        tK.Label(self.root, text="Error: Could not connect to the database\nPlease ensure XAMPP is running.\n\n", font=("Calibri", 21)).pack(side="top")
        tK.Label(self.root, text="Error: %s" % (error),font=("Calibri", 21)).pack(side="top")

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
            tK.Label(self.root, text="Username or Password was incorrect - Please try again.\n\n\n\n\n\n", font=("Calibri", 20)).pack(side="bottom") # if user credentials incorrect, shows this at the bottom of window
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 28), bg="sky blue").pack(side="top")  # window heading text centered at the top available space
        tK.Label(self.root, text="Staff ID", font=("Calibri", 22), bg="sky blue").pack(side="top")  # text left of entry box
        self.sidbox = tK.Entry(self.root, width=35) # text entry box for staff id
        self.sidbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\nPassword", font=("Calibri", 22), bg="sky blue").pack(side="top")  # text left of entry box
        self.pwbox = tK.Entry(self.root, width=35)  # text entry box for password
        self.pwbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\n\n\n", bg="sky blue").pack(side="top")
        tK.Button(self.root, text="Log In", command=lambda : self.loginBackend(), width=20, height=2).pack(side="top") # login button - when clicked runs loginBackend function

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
            h = homePage(self.root) # home page object passing the root so everything is presented on same window
            h.homeScreen() # show home screen


class homePage(VesselManSys): # home screen - menu for the different program functionalities
    def __init__(self, parent):
        self.root = parent # inherit root window from VesselManSys

    def homeScreen(self):
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 28), bg="sky blue").pack(side="top")  # window heading text centered at the top available space
        if self.networkCheck(): # check if network connection is present
            tK.Button(self.root, text="AIS", command=lambda : self.aisScreen(), width=45, height=10).place(relx=0.3, rely=0.3,anchor="center")  # AIS button - relx/rely are relative screen positions - 0.5 is central
        else:
            tK.Button(self.root, text="AIS\n(unavailable - offline)", width=45, height=10).place(relx=0.3, rely=0.3,anchor="center")  # AIS button
        if self.networkCheck():
            tK.Button(self.root, text="Weather", command=lambda : self.weatherScreen(), width=45, height=10).place(relx=0.5, rely=0.3, anchor="center") # Weather button
        else:
            tK.Button(self.root, text="Weather\n(unavailable - offline)", width=45, height=10).place(relx=0.5, rely=0.3,anchor="center")  # Weather button
        if self.networkCheck():
            tK.Button(self.root, text="Tides", command=lambda : self.tidesScreen(), width=45, height=10).place(relx=0.7, rely=0.3, anchor="center") # Tides button
        else:
            tK.Button(self.root, text="Tides", width=45, height=10).place(relx=0.7, rely=0.3,anchor="center")  # Tides button

        tK.Button(self.root, text="Logs", command=lambda : self.logsScreen(), width=45, height=10).place(relx=0.3, rely=0.5, anchor="center") # Logs screen button
        tK.Button(self.root, text="Emergency", command=lambda : self.emergencyScreen(), width=45, height=10).place(relx=0.5, rely=0.5, anchor="center") # Emergency screen button
        tK.Button(self.root, text="Checklists", command=lambda : self.checklistsScreen(), width=45, height=10).place(relx=0.7, rely=0.5, anchor="center") # Checklist screen button
        tK.Button(self.root, text="Calendar", command=lambda : self.calendarScreen(), width=45, height=10).place(relx=0.3, rely=0.7, anchor="center") # Calendar screen button
        tK.Button(self.root, text="Crew Info Lookup", command=lambda : self.crewInfoScreen(), width=45, height=10).place(relx=0.5, rely=0.7, anchor="center") # Crew Info Lookup Screen
        tK.Button(self.root, text="User Account Management", command=lambda : self.UAManagementScreen(), width=45, height=10).place(relx=0.7, rely=0.7, anchor="center") # User Account Management Screen


    def networkCheck(self, host="http://google.com"): #checks if google.com is accessible, host must be perameter!
        try:
            urllib.request.urlopen(host) # opens host (google.com)
            return True # if connection is successful
        except:
            return False # if connection is unsuccessful

def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    a = VesselManSys(root)
    log = homePage(a)
    vms = userLoginScreen(a)
    root.mainloop()


runApp()
