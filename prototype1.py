import tkinter as tK
import mysql.connector
import hashlib
import urllib.request
import tkcalendar
import datetime
import textwrap

class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Passenger Vessel Management System")  # the window title
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen
        self.root.configure(bg="#114F69")
        self.firstName = self.surName = self.phoneNum = self.staffID = self.DOB = self.NOK = ""

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
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 24), bg="#114F69").pack(side="top")
        tK.Label(self.root, text="Error: Could not connect to the database - please ensure XAMPP is running.\n\n", font=("Calibri", 20), bg="#114F69").pack(side="top")
        #tK.Label(self.root, text="Error: %s" % (error),font=("Calibri", 21)).pack(side="top")
        a = UserLoginScreen(self)

    def forgetAllWidgets(self):    # hides a list of shown widgets
        widgetList = self.root.winfo_children() # all widgets (items) shown on the window
        for item in widgetList:
            if item.winfo_children():
                widgetList.extend(item.winfo_children())    # any sub-widgets
        for item in widgetList:
            item.pack_forget()  # hide all widgets / remove everything from the list of packed widgets
        for item in widgetList:
            item.place_forget()

    def loggedOut(self):
        a = UserLoginScreen(self)

class UserLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent): # constructor
        self.root = parent.root # inherit the root tkinter window from VesselManSys class
        self.credentialFailFlag = False # shows if user login credentials were correct or not - True if incorrect
        self.loginScreen()

    def loginScreen(self):
        if self.credentialFailFlag == True:
            tK.Label(self.root, text="Username or Password was incorrect - Please try again.\n\n\n\n\n\n", font=("Calibri", 20), bg="#114F69").pack(side="bottom") # if user credentials incorrect, shows this at the bottom of window
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 28), bg="#114F69").pack(side="top")  # window heading text centered at the top available space
        tK.Label(self.root, text="Staff ID", font=("Calibri", 22), bg="#114F69").pack(side="top")  # text left of entry box
        self.sidbox = tK.Entry(self.root, width=35) # text entry box for staff id
        self.sidbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\nPassword", font=("Calibri", 22), bg="#114F69").pack(side="top")  # text left of entry box
        self.pwbox = tK.Entry(self.root, show="⚫", width=35)  # text entry box for password
        self.pwbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\n\n\n", bg="#114F69").pack(side="top")
        tK.Button(self.root, text="Log In", command=lambda : self.loginBackend(), width=20, height=2).pack(side="top") # login button - when clicked runs loginBackend function

    def loginBackend(self): # linked to the submit button on login page
        tempSID = self.sidbox.get() # gets the user input from staff id text box on login page
        if tempSID.isnumeric(): # validation to check if it is a number
            tempSID = int(tempSID)
            if tempSID > 0:
                self.staffID = tempSID
                password = self.pwbox.get() # gets the user input from password box on login screen
                statement = "SELECT * FROM Users WHERE StaffID = '%s' AND Password = '%s';" % (self.staffID, self.sha256hash(password)) # paramaterised StaffID & Password to avoid SQL injection
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
            h = HomePage(self.root) # home page object passing the root so everything is presented on same window
            h.homeScreen() # show home screen


class HomePage(VesselManSys): # home screen - menu for the different program functionalities
    def __init__(self, parent):
        self.root = parent # inherit root window from VesselManSys
        self.Flag = False

    def logout(self):
        self.firstName = ""
        self.surName = ""
        self.phoneNum = ""
        self.NOK = ""
        self.DOB = ""
        self.staffID = None
        self.forgetAllWidgets()
        self.loggedOut()

    def homeScreen(self):   # shows the main menu screen
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 28), bg="#114F69").pack(side="top")  # window heading text centered at the top available space
        logoutImg = tK.PhotoImage(file="logout.png")    #opens image
        logoutImg = logoutImg.subsample(8, 8)   # changes image size
        logoutBut = tK.Button(self.root, text="  Logout", command=lambda: self.logout(), image=logoutImg,compound="left")  # logs button - compound = justify the image
        logoutBut.photo = logoutImg # must store the variable as a property of the button
        logoutBut.place(relx=0.95, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        if self.networkCheck(): # check if network connection is present
            weatherImg = tK.PhotoImage(file="cloudy.png") #opens image
            weatherImg = weatherImg.subsample(3, 3) # changes image size
            weatherBut = tK.Button(self.root, text="Weather", command=lambda : self.weatherLink(), image=weatherImg, compound="top")  # Weather button
            weatherBut.photo = weatherImg # must store the variable as a property of the button
            weatherBut.place(relx=0.3, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="Weather\n(unavailable - offline)", width=45, height=10).place(relx=0.3, rely=0.3,anchor="center")  # Weather button

        if self.networkCheck():
            aisImg = tK.PhotoImage(file="radar.png") #opens image
            aisImg = aisImg.subsample(3, 3) # changes image size
            aisBut = tK.Button(self.root, text="AIS", command=lambda : self.aisLink(), image=aisImg, compound="top")  # AIS button
            aisBut.photo = aisImg # must store the variable as a property of the button
            aisBut.place(relx=0.5, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="AIS\n(unavailable - offline)", width=45, height=10).place(relx=0.5, rely=0.3,anchor="center")  # AIS button

        if self.networkCheck():
            tideImg = tK.PhotoImage(file="high-tide.png") #opens image
            tideImg = tideImg.subsample(3, 3) # changes image size
            tideBut = tK.Button(self.root, text="Tides", command=lambda : self.tideLink(), image=tideImg, compound="top")  # tide button
            tideBut.photo = tideImg # must store the variable as a property of the button
            tideBut.place(relx=0.7, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="Tides", width=45, height=10).place(relx=0.7, rely=0.3,anchor="center")  # Tides button

        logsImg = tK.PhotoImage(file="open-book.png") #opens image
        logsImg = logsImg.subsample(3, 3) # changes image size
        logsBut = tK.Button(self.root, text="Logs", command=lambda : self.logLink(), image=logsImg, compound="top")  # logs button
        logsBut.photo = logsImg # must store the variable as a property of the button
        logsBut.place(relx=0.3, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        emergencyImg = tK.PhotoImage(file="alarm.png") #opens image
        emergencyImg = emergencyImg.subsample(3, 3) # changes image size
        emergencyBut = tK.Button(self.root, text="Emergency", command=lambda : self.emergencyLink(), image=emergencyImg, compound="top")  # emergency button
        emergencyBut.photo = emergencyImg # must store the variable as a property of the button
        emergencyBut.place(relx=0.5, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        checklistImg = tK.PhotoImage(file="clipboard.png") #opens image
        checklistImg = checklistImg.subsample(3, 3) # changes image size
        checklistBut = tK.Button(self.root, text="Checklists", command=lambda : self.checklistLink(), image=checklistImg, compound="top")  # checklist button
        checklistBut.photo = checklistImg # must store the variable as a property of the button
        checklistBut.place(relx=0.7, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        calendarImg = tK.PhotoImage(file="calendar.png") #opens image
        calendarImg = calendarImg.subsample(3, 3) # changes image size
        calendarBut = tK.Button(self.root, text="Calendar", command=lambda : self.calendarLink(), image=calendarImg, compound="top")  # calendar button
        calendarBut.photo = calendarImg # must store the variable as a property of the button
        calendarBut.place(relx=0.3, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        crewLookupImg = tK.PhotoImage(file="search.png") #opens image
        crewLookupImg = crewLookupImg.subsample(3, 3) # changes image size
        crewLookupBut = tK.Button(self.root, text="Crew Information Lookup", command=lambda : self.crewLookupLink(), image=crewLookupImg, compound="top")  # crewLookup button
        crewLookupBut.photo = crewLookupImg # must store the variable as a property of the button
        crewLookupBut.place(relx=0.5, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        accountManagerImg = tK.PhotoImage(file="account.png") #opens image
        accountManagerImg = accountManagerImg.subsample(3, 3) # changes image size
        accountManagerBut = tK.Button(self.root, text="User Account Mangement", command=lambda : self.accManagerLink(), image=accountManagerImg, compound="top")  # accountManager button
        accountManagerBut.photo = accountManagerImg # must store the variable as a property of the button
        accountManagerBut.place(relx=0.7, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text


    def networkCheck(self, host="http://google.com"): #checks if google.com is accessible, host must be perameter!
        try:
            urllib.request.urlopen(host) # opens host (google.com)
            return True # if connection is successful
        except:
            return False # if connection is unsuccessful


class CalendarScreen(VesselManSys): # For showing and using the calendar feature
    def __init__(self, parent):
        self.root = parent.root #inherit root window from parent (vesselManSys)
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen
        self.root.configure(bg="#114F69") # background colour navy blue
        self.calendarCursor = self.tree = ""    # define class member variables
        self.showCalendar()

    def showCalendar(self):
        def dateSelect():   # gets the current user selection of date on calendar and shows events for it
            self.calendarCursor = mainCal.selection_get()   # gets user's selection of date from picker
            self.viewEventsOnDay()  # shows events on that day

        todaydate = datetime.date.today()   # get today date and time
        yearnow = int(todaydate.strftime("%Y")) # get the year from that date/time
        monthnow = int(todaydate.strftime("%m")) # get the month
        datenow = int(todaydate.strftime("%d")) # get the day
        mainCal = tkcalendar.Calendar(self.root, font=("Calibri", 20), selectmode="day", locale="en_GB", year=yearnow, month=monthnow, day=datenow) # make a calendar, selectable by day, default to today date
        mainCal.pack() # show calendar on screen
        tK.Label(self.root, text="\n", bg="#114F69").pack() # for spacing, blank new line
        a = tK.Button(self.root, text="View Events", command=dateSelect).pack() # button to show events on particular day
        tK.Label(self.root, text="\n\n", bg="#114F69").pack() # for spacing, blank new line

    def viewEventsOnDay(self): # shows a list of events happening ona particular day
        treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        treeStyle.theme_use("default") # use the default theme until some specifics are modified below
        treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 18), foreground="black")  # this is the heading fields for the list
        treeStyle.configure("Treeview", font=("Calibri", 12))   # the entry fields for the list

        statement = "SELECT CONVERT(Time,CHAR), event FROM calendar WHERE Date = '%s';" % (self.calendarCursor) # return the time and event details for the specified date
        results = self.dbConnection(statement) # execute the SQL statement in the database
        try:
            if self.tree.winfo_exists() == 1: # if a Treeview (list object) already exists - destroy it
                self.tree.pack_forget() # remove the widget from screen
        except:
            pass
        self.tree = tK.ttk.Treeview(self.root, columns=("one")) # create the Treeview (list) object with 2 columns, #0 and "one"
        scrollbar = tK.ttk.Scrollbar(self.root, command=self.tree.yview, orient="vertical")
        scrollbar.place(relx=0.673, rely=0.4335, relheight=0.189, relwidth=0.010)

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("#0", text="Time")    # first column header
        self.tree.heading("one", text="Event")  # second column header

        self.tree.column("#0", minwidth=300, width=300, anchor="w") # set the default and minimum width for each column
        self.tree.column("#1", minwidth=400, width=400, anchor="w")

        for num in range(0, len(results)): # adding entries to the list from the results of the SQL execution
            temptime = results[num][0]  # time value from the results
            temptext = results[num][1]  # event details text value from the results
            temptext = "\n".join(textwrap.wrap(temptext, 56))
            row = self.tree.insert("", index="end", text=temptime, values=(temptext,)) # insert the values at the end of the current list

        self.tree.pack()   # show the list on screen



def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    a = VesselManSys(root)
    #vms = UserLoginScreen(a)

    c = CalendarScreen(a)

    root.mainloop()


runApp()
#c = CalendarScreen(root)
#c.showCalendar()
#example1()
