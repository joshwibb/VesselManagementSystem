import tkinter as tK
import mysql.connector
import hashlib
import urllib.request
import tkcalendar
import datetime
import textwrap
import requests
import sys
from cefpython3 import cefpython

class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Passenger Vessel Management System")  # the window title
        self.root.state("zoomed") # maximises the screen on execution
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

        tK.Label(self.root, text="Error: %s" % (error),font=("Calibri", 21)).pack(side="top")
        a = UserLoginScreen(self)

    def forgetAllWidgets(self):    # hides a list of shown widgets
        widgetList = self.root.winfo_children() # all widgets (items) shown on the window
        for item in widgetList:
            if item.winfo_children():
                widgetList.extend(item.winfo_children())    # any sub-widgets
        for item in widgetList:
            if type(item) == tkcalendar.tooltip.Tooltip:
                pass
            else:
                item.pack_forget()
        for item in widgetList:
            if type(item) == tkcalendar.tooltip.Tooltip:
                pass
            else:
                item.place_forget()

    def loggedOut(self):
        self.forgetAllWidgets()
        a = UserLoginScreen(self)

    def commonStyles(self):
        tK.Label(self.root, text="Passenger Vessel Management System", font=("Calibri", 28), fg="white", bg="#114F69").place(relx=0.5, rely=0.02, anchor="center")  # window heading text centered at the top available space
        logoutImg = tK.PhotoImage(file="ImageResources/logout.png")  # opens image
        logoutImg = logoutImg.subsample(8, 8)  # changes image size
        logoutBut = tK.Button(self.root, text="  Logout", command=lambda: self.loggedOut(), image=logoutImg,compound="left")  # logs button - compound = justify the image
        logoutBut.photo = logoutImg  # must store the variable as a property of the button
        logoutBut.place(relx=0.95, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

class UserLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent): # constructor
        self.root = parent.root # inherit the root tkinter window from VesselManSys class
        self.credentialFailFlag = False # shows if user login credentials were correct or not - True if incorrect
        self.loginScreen()

    def loginScreen(self):
        if self.credentialFailFlag == True:
            tK.Label(self.root, text="Username or Password was incorrect - Please try again.\n\n\n\n\n\n", font=("Calibri", 20), bg="#114F69").pack(side="bottom") # if user credentials incorrect, shows this at the bottom of window
        tK.Label(self.root, text="\nPassenger Vessel Management System\n\n", font=("Calibri", 28), fg="white", bg="#114F69").pack(side="top")  # window heading text centered at the top available space
        tK.Label(self.root, text="Staff ID", font=("Calibri", 22), bg="#114F69", fg="white").pack(side="top")  # text left of entry box
        self.sidbox = tK.Entry(self.root, width=35) # text entry box for staff id
        self.sidbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\nPassword", font=("Calibri", 22), bg="#114F69", fg="white").pack(side="top")  # text left of entry box
        self.pwbox = tK.Entry(self.root, show="⚫", width=35)  # text entry box for password
        self.pwbox.pack(side="top") # place the text entry box on the screen
        tK.Label(self.root, text="\n\n\n", bg="#114F69").pack(side="top")
        tK.Button(self.root, text="Log In", command=self.loginBackend, width=20, height=2).pack(side="top") # login button - when clicked runs loginBackend function

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
                    self.firstName = str(resultTup[2])
                    self.surName = str(resultTup[3])
                    self.phoneNum = str(resultTup[4])   # String as could have hashtags or +
                    self.DOB = str(resultTup[5]) # Date Of Birth
                    self.NOK = str(resultTup[6]) # Name of Next Of Kin
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
        tK.Label(self.root, text="Passenger Vessel Management System", font=("Calibri", 28), fg="white",bg="#114F69").place(relx=0.5, rely=0.02,anchor="center")  # window heading text centered at the top available space
        logoutImg = tK.PhotoImage(file="ImageResources/logout.png")  # opens image
        logoutImg = logoutImg.subsample(8, 8)  # changes image size
        logoutBut = tK.Button(self.root, text="  Logout", command=lambda: self.logout(), image=logoutImg,compound="left")  # logs button - compound = justify the image
        logoutBut.photo = logoutImg  # must store the variable as a property of the button
        logoutBut.place(relx=0.95, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

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
        if self.networkCheck(): # check if network connection is present
            weatherImg = tK.PhotoImage(file="ImageResources/cloudy.png") #opens image
            weatherImg = weatherImg.subsample(3, 3) # changes image size
            weatherBut = tK.Button(self.root, text="Weather", command=lambda : self.weatherLink(), image=weatherImg, compound="top")  # Weather button
            weatherBut.photo = weatherImg # must store the variable as a property of the button
            weatherBut.place(relx=0.3, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="Weather\n(unavailable - offline)", width=45, height=10).place(relx=0.3, rely=0.3,anchor="center")  # Weather button

        if self.networkCheck():
            aisImg = tK.PhotoImage(file="ImageResources/radar.png") #opens image
            aisImg = aisImg.subsample(3, 3) # changes image size
            aisBut = tK.Button(self.root, text="AIS\n(Provided in external window)", command=lambda : self.aisLink(), image=aisImg, compound="top")  # AIS button
            aisBut.photo = aisImg # must store the variable as a property of the button
            aisBut.place(relx=0.5, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="AIS\n(unavailable - offline)", width=45, height=10).place(relx=0.5, rely=0.3,anchor="center")  # AIS button

        if self.networkCheck():
            tideImg = tK.PhotoImage(file="ImageResources/high-tide.png") #opens image
            tideImg = tideImg.subsample(3, 3) # changes image size
            tideBut = tK.Button(self.root, text="Tides", command=lambda : self.tideLink(), image=tideImg, compound="top")  # tide button
            tideBut.photo = tideImg # must store the variable as a property of the button
            tideBut.place(relx=0.7, rely=0.3, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        else:
            tK.Button(self.root, text="Tides", width=45, height=10).place(relx=0.7, rely=0.3,anchor="center")  # Tides button

        logsImg = tK.PhotoImage(file="ImageResources/open-book.png") #opens image
        logsImg = logsImg.subsample(3, 3) # changes image size
        logsBut = tK.Button(self.root, text="Logs", command=lambda : self.logLink(), image=logsImg, compound="top")  # logs button
        logsBut.photo = logsImg # must store the variable as a property of the button
        logsBut.place(relx=0.3, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        emergencyImg = tK.PhotoImage(file="ImageResources/alarm.png") #opens image
        emergencyImg = emergencyImg.subsample(3, 3) # changes image size
        emergencyBut = tK.Button(self.root, text="Emergency", command=lambda : self.emergencyLink(), image=emergencyImg, compound="top")  # emergency button
        emergencyBut.photo = emergencyImg # must store the variable as a property of the button
        emergencyBut.place(relx=0.5, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        checklistImg = tK.PhotoImage(file="ImageResources/clipboard.png") #opens image
        checklistImg = checklistImg.subsample(3, 3) # changes image size
        checklistBut = tK.Button(self.root, text="Checklists", command=lambda : self.checklistLink(), image=checklistImg, compound="top")  # checklist button
        checklistBut.photo = checklistImg # must store the variable as a property of the button
        checklistBut.place(relx=0.7, rely=0.5, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        calendarImg = tK.PhotoImage(file="ImageResources/calendar.png") #opens image
        calendarImg = calendarImg.subsample(3, 3) # changes image size
        calendarBut = tK.Button(self.root, text="Calendar", command=lambda : self.calendarLink(), image=calendarImg, compound="top")  # calendar button
        calendarBut.photo = calendarImg # must store the variable as a property of the button
        calendarBut.place(relx=0.3, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        crewLookupImg = tK.PhotoImage(file="ImageResources/search.png") #opens image
        crewLookupImg = crewLookupImg.subsample(3, 3) # changes image size
        crewLookupBut = tK.Button(self.root, text="Crew Information Lookup", command=lambda : self.crewLookupLink(), image=crewLookupImg, compound="top")  # crewLookup button
        crewLookupBut.photo = crewLookupImg # must store the variable as a property of the button
        crewLookupBut.place(relx=0.5, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        accountManagerImg = tK.PhotoImage(file="ImageResources/account.png") #opens image
        accountManagerImg = accountManagerImg.subsample(3, 3) # changes image size
        accountManagerBut = tK.Button(self.root, text="User Account Mangement", command=lambda : self.accManagerLink(), image=accountManagerImg, compound="top")  # accountManager button
        accountManagerBut.photo = accountManagerImg # must store the variable as a property of the button
        accountManagerBut.place(relx=0.7, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def calendarLink(self):
        c = CalendarScreen(self.root)
        c.showCalendar()

    def weatherLink(self):
        w = WeatherScreen(self.root)
        w.showWeatherFinder()

    def aisLink(self):
        a = AISScreen(self.root)

    def networkCheck(self, host="http://google.com"): #checks if google.com is accessible, host must be perameter!
        try:
            urllib.request.urlopen(host) # opens host (google.com)
            return True # if connection is successful
        except:
            return False # if connection is unsuccessful

class CalendarScreen(VesselManSys): # For showing and using the calendar feature
    def __init__(self, parent):
        self.root = parent #inherit root window from parent (vesselManSys)
        self.commonStyles()
        self.calendarCursor = ""    # define class member variables
        self.tree = tK.ttk.Treeview(self.root, columns=("one"))  # create the Treeview (list) object with 2 columns, #0 and "one - does not show without pack()
        self.treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        self.treeStyle.theme_use("default")  # use the default theme until some specifics are modified below

    def goHome(self): # called from Back button on showCalendar()
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root) # create home screen object
        h.homeScreen() # show home screen

    def showCalendar(self):  # show the calendar on screen
        self.forgetAllWidgets()
        self.commonStyles()
        todaydate = datetime.date.today()   # get today date and time
        yearnow = int(todaydate.strftime("%Y")) # get the year from that date/time
        monthnow = int(todaydate.strftime("%m")) # get the month
        datenow = int(todaydate.strftime("%d")) # get the day
        self.mainCal = tkcalendar.Calendar(self.root, font=("Calibri", 20), selectmode="day", locale="en_GB", year=yearnow, month=monthnow, day=datenow) # make a calendar, selectable by day, default to today date
        self.mainCal.place(relx=0.5, rely=0.3, anchor="center", relheight=0.5, relwidth=0.5) # show calendar on screen
        tK.Label(self.root, text="\n", bg="#114F69").pack() # for spacing, blank new line

        self.mainCal.bind("<<CalendarSelected>>",self.dateSelect) # bind the mouse click of a date in calendar to dateSelect function
        self.viewEventsOnDay()

        addImg = tK.PhotoImage(file="ImageResources/plus.png")  # opens image
        addImg = addImg.subsample(6, 6)  # changes image size
        addBut = tK.Button(self.root, text="Add Event", command=lambda: self.addEvent(), image=addImg,compound="top")  # add event button
        addBut.photo = addImg  # must store the variable as a property of the button
        addBut.place(relx=0.25, rely=0.65,anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        addImg = tK.PhotoImage(file="ImageResources/minus.png")  # opens image
        addImg = addImg.subsample(6, 6)  # changes image size
        addBut = tK.Button(self.root, text="Remove Event", command=lambda: self.removeEvent(), image=addImg,compound="top")  # remove event button
        addBut.photo = addImg  # must store the variable as a property of the button
        addBut.place(relx=0.25, rely=0.8,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def viewEventsOnDay(self): # shows a list of events happening ona particular day
        self.tree.delete(*self.tree.get_children()) # removes all items in list
        self.treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 18), foreground="black")  # this is the heading fields for the list
        self.treeStyle.configure("Treeview", font=("Calibri", 12))   # the entry fields for the list
        dateParameter = self.calendarCursor
        if self.calendarCursor == "":
            self.calendarCursor = datetime.datetime.today().strftime("%Y-%m-%d")
        statement = "SELECT CONVERT(timeStarts,CHAR), CONVERT(timeEnds,CHAR), eventTitle, eventDetails FROM calendar WHERE Date = '%s' ORDER BY timeStarts ASC;" % (self.calendarCursor) # return the time and event details for the specified date
        results = self.dbConnection(statement) # execute the SQL statement in the database
        if self.tree.winfo_exists() == 1: # if a Treeview (list object) already exists - destroy it
            self.tree.pack_forget() # remove the widget from screen
        scrollbar = tK.ttk.Scrollbar(self.root, command=self.tree.yview, orient="vertical") # vertical scrollbar for the list box
        scrollbar.place(relx=0.66, rely=0.612, relheight=0.268, relwidth=0.010) # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set) # relate the created scrollbar to the list
        self.tree["columns"] = ("zero","one","two")
        self.tree.heading("zero", text="Time")    # first column header
        self.tree.heading("one", text="Event")  # second column header
        self.tree.heading("two", text="details") # third hidden column
        self.tree.column("zero", minwidth=150, width=150, anchor=tK.CENTER) # set the default and minimum width for each column
        self.tree.column("one", minwidth=500, width=500, anchor="w")
        self.tree.column("two", width=0, stretch=0)

        for num in range(0, len(results)): # adding entries to the list from the results of the SQL execution
            resultEventTimeStart = results[num][0]  # time value from the results
            resultEventTimeEnd = results[num][1]  # time value from the results
            if resultEventTimeStart == None or resultEventTimeEnd == None: # for an all day event
                resultEventTimeString = "All Day"
            else:
                resultEventTimeString = (resultEventTimeStart[0:5]+" - "+resultEventTimeEnd[0:5]) # how it will appear in the list
            resultEventTitle = results[num][2]  # event details text value from the results
            resultDetails = results[num][3]
            if len(resultEventTitle) > 65:  # 65 to fit in the width of the event column
                resultEventTitle = resultEventTitle + "..."   # everything before the 65th character + ...
                if num < len(results):  # stops out of range error
                    print(resultEventTimeString)
                    row = self.tree.insert("", index=num+1, iid=num+1, text="", values=(resultEventTimeString,resultEventTitle,resultDetails))  # insert the values at the end of the current list
            else: # show the whole string if it fits in the column
                if num < len(results): # stops out of range error
                    row = self.tree.insert("", index="end", iid=num, text="", values=(resultEventTimeString,resultEventTitle,resultDetails))  # insert the values at the end of the current list

        if len(results) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.tree["show"] = "headings" # hide the ID column
        self.tree.bind("<Double-1>", self.viewEventDetails) # bind a double-click event to the viewEventDetails member function
        self.tree.place(relx=0.5, rely=0.73, anchor="center", relheight=0.3)   # show the list on screen

    def viewEventDetails(self, *args):  # view the full description of an event on a full screen
        self.forgetAllWidgets() # clear the screen
        self.commonStyles()
        eventDict = self.tree.item(self.tree.selection())["values"] # retrieve values relating to the row picked from the list (inc. times,title,details)
        if len(eventDict) == 0:
            self.showCalendar()
            return
        times = eventDict[0] # string in format: Start time - end time
        title = eventDict[1] # title of event, was shown as 'Event' on full list
        details = str(eventDict[2]) # description of event, anything upto 2000 characters
        if len(details) >= 140:
            detailsWrapped = "\n".join(textwrap.wrap(details, 140)) # wrap text at 140 characters
        else:
            detailsWrapped = details
        if type(self.calendarCursor) == str:
            date = datetime.datetime.strptime(self.calendarCursor,"%Y-%m-%d")  # the date the user selected on the calender, converted from string into datetime format
        else:
            date = self.calendarCursor
        dateString = (datetime.datetime.strftime(date,"%A"),datetime.datetime.strftime(date,"%d"),datetime.datetime.strftime(date,"%B"),datetime.datetime.strftime(date,"%Y")) # convert the selected date into day of week,date in month,month,year
        dateString = ' '.join(dateString) # join together the tuple created above and leave a space between each item
        tK.Label(self.root, text=title, font=("Calibri bold", 28), fg="white", bg="#114F69").place(relx=0.1, rely=0.2, anchor="w") # title text, top of screen, bold
        tK.Label(self.root, text=dateString, font=("Calibri", 22), fg="white", bg="#114F69").place(relx=0.1, rely=0.3, anchor="w") # date text
        tK.Label(self.root, text=times, font=("Calibri", 22), fg="white", bg="#114F69").place(relx=0.1, rely=0.4, anchor="w") # time beginning and end or All Day
        tK.Label(self.root, text=detailsWrapped, font=("Calibri", 18), justify="left", fg="white", bg="#114F69").place(relx=0.1, rely=0.62, anchor="w") # full description of event

        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.showCalendar(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def addEvent(self): # create a new event and add to the DB
        def switchTimeMode(): # switch between All Day event and timed
            if timeCheckboxVar.get() == 1: # if checkbox is activated
                entryDefaultTextStart.set("All Day") # set textbox text to "All Day"
                entryDefaultTextEnd.set("All Day") # set textbox text to "All Day"
                startBox.configure(state=tK.DISABLED) # grey out / deactivate the start time textbox
                endBox.configure(state=tK.DISABLED) # grey out / deactivate the end time textbox
            else: # if checkbutton is deactivated
                entryDefaultTextStart.set("") # empty both start/end time textboxes
                entryDefaultTextEnd.set("") # empty both start/end time textboxes
                startBox.configure(state=tK.NORMAL) # activate the start time box
                endBox.configure(state=tK.NORMAL) # activate the end time box
        
        self.forgetAllWidgets() # clear the screen
        self.commonStyles() # add title, logout button etc.

        if type(self.calendarCursor) == str:
            date = datetime.datetime.strptime(self.calendarCursor,"%Y-%m-%d")  # the date the user selected on the calender, converted from string into datetime format
        else:
            date = self.calendarCursor
        dateString = (datetime.datetime.strftime(date, "%A"), datetime.datetime.strftime(date, "%d"),datetime.datetime.strftime(date, "%B"), datetime.datetime.strftime(date,"%Y"))  # convert the selected date into day of week,date in month,month,year
        dateString = ' '.join(dateString)  # join together the tuple created above and leave a space between each item
        tK.Label(self.root, text=dateString, fg="white", bg="#114F69", font=("Calibri 25 bold")).place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(self.root, text="Event Title: ", font=("Calibri 25"), fg="white", bg="#114F69").place(relx=0.495, rely=0.2, anchor="e")
        titleBox = tK.Entry(self.root, width=50) # entry box for event title
        titleBox.place(relx=0.505, rely=0.2, anchor="w")
        tK.Label(self.root, text="All Day ", font=("Calibri", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="e")
        timeCheckboxVar = tK.IntVar() # changes between 0 & 1 on checkbox click
        timeButton = tK.Checkbutton(self.root, bg="#114F69", activebackground="#114F69", variable=timeCheckboxVar, command=switchTimeMode) # checkbox for All Day events
        timeButton.place(relx=0.502, rely=0.3, anchor="w")
        entryDefaultTextStart = tK.StringVar() # used so when allday event, boxes can have default text
        entryDefaultTextEnd = tK.StringVar()
        entryDefaultTextStart.set("") # by default, text entry box set to blank values
        entryDefaultTextEnd.set("")
        tK.Label(self.root, text="Start Time (HH:MM):", font=("Calibri 20"), fg="white", bg="#114F69").place(relx=0.495, rely=0.4, anchor="e")
        startBox = tK.Entry(self.root, text=entryDefaultTextStart)
        startBox.place(relx=0.505, rely=0.4, anchor="w")
        tK.Label(self.root, text="End Time (HH:MM):", font=("Calibri 20"), fg="white", bg="#114F69").place(relx=0.495, rely=0.5, anchor="e")
        endBox = tK.Entry(self.root, text=entryDefaultTextEnd)
        endBox.place(relx=0.505, rely=0.5, anchor="w")
        tK.Label(self.root, text="Event Details / Notes:", fg="white", bg="#114F69").place(relx=0.5, rely=0.6, anchor="s")
        detailBox = tK.Text(self.root, width=100)
        detailBox.place(relx=0.5, rely=0.7, anchor="center", height=200)
        submitImg = tK.PhotoImage(file="ImageResources/submit.png")  # opens image
        submitImg = submitImg.subsample(8, 8)  # changes image size
        submitBut = tK.Button(self.root, text="  Submit", command=lambda: self.addEventBackend(titleBox,timeCheckboxVar,startBox,endBox,detailBox), image=submitImg, compound="left")  # submit button - compound = justify the image
        submitBut.photo = submitImg  # must store the variable as a property of the button
        submitBut.place(relx=0.5, rely=0.85,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.showCalendar, image=backImg,compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def addEventBackend(self, title, timeMode, startTime, endTime, details):
        title = title.get()
        timeMode = timeMode.get()
        startTime = startTime.get()
        endTime = endTime.get()
        if timeMode == 1:
            statement = "SELECT EVENTID FROM calendar WHERE DATE = '%s' AND TIMESTARTS = NULL AND EVENTTITLE  = '%s'" % (self.calendarCursor,title)
        else:
            statement = "SELECT EVENTID FROM calendar WHERE DATE = '%s' AND TIMESTARTS = '%s' AND EVENTTITLE  = '%s'" % (self.calendarCursor, startTime,title)

        results = self.dbConnection(statement)
        if len(results) > 0:
            self.addEvent()
            tK.Label(self.root, text="Event already exists.", font=("Calibri", 20), fg="red", bg="#114F69").place(relx=0.5, rely=0.55, anchor="center")
            return

        details = details.get("1.0","end-1c") # get value typed into details box - the last character as it would add an extra line otherwise
        if timeMode == 1: # if All Day event
            statement = "INSERT INTO calendar (DATE,EVENTTITLE,EVENTDETAILS) VALUES ('%s','%s','%s');" % (self.calendarCursor, title, details)
        else:
            try:
                startTime = datetime.datetime.strptime(startTime, "%H:%M") # ensure time values are valid HH:MM
                endTime = datetime.datetime.strptime(endTime, "%H:%M")
            except Exception:
                self.addEvent()
                tK.Label(self.root, text="Start and end times must be in format: MM:HH - Please Try Again", font=("Calibri", 20), fg="red", bg="#114F69").place(relx=0.5, rely=0.55, anchor="center")
                return
            statement = "INSERT INTO calendar (DATE,TIMESTARTS,TIMEENDS,EVENTTITLE,EVENTDETAILS) VALUES ('%s','%s','%s','%s','%s');" % (self.calendarCursor, startTime, endTime, title, details)
        self.dbConnection(statement) # execute statement in db
        self.showCalendar()

    def dateSelect(self, *args):   # gets the current user selection of date on calendar and shows events for it
        if self.calendarCursor != self.mainCal.selection_get():
            self.calendarCursor = self.mainCal.selection_get()   # gets user's selection of date from picker
            self.viewEventsOnDay()  # shows events on that day

    def removeEvent(self):
        self.forgetAllWidgets()  # clear the screen
        self.commonStyles()
        eventDict = self.tree.item(self.tree.selection())["values"]  # retrieve values relating to the row picked from the list (inc. times,title,details)
        if len(eventDict) == 0:
            self.showCalendar()
            return
        startTime = str(eventDict[0])  # string in format: Start time - end time
        if startTime == "All Day":
            startTime = 'IS NULL'
        else:
            startTime = startTime.split(" ")[0]
            startTime = "= '" + startTime + "'"
        title = eventDict[1]  # title of event, was shown as 'Event' on full list
        statement = "DELETE FROM calendar WHERE Date = '%s' AND EVENTTITLE = '%s' AND TIMESTARTS %s;" % (self.calendarCursor, title, startTime)
        self.dbConnection(statement)
        self.showCalendar()
        return

class WeatherScreen(VesselManSys):
    def __init__(self, parent):
        self.root = parent
        self.forgetAllWidgets() # clear window
        self.commonStyles()
        self.imgLinks = [] # will contain file paths to images used
        self.currWeatherIcon = str() # the file path for the weather icon at current time
        self.dayLabel = tK.Label(self.root, text="", fg="#B9CBCA", bg="#114F69", font=("Calibri 18")) # defined but not placed on screen, will be day/date of results
        self.weatherFrame = tK.Frame(self.root, width=1200, height=500, bg="#729796") # for upto 8 canvases/weather times to fit into

    def goHome(self): # called from Back button on showWeatherFinder()
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root) # create home screen object
        h.homeScreen() # show home screen

    def forgetFrameContents(self, frame): # works as vesselManSys.forgetAllWidgets() but for frame not window
        widgetList = frame.winfo_children()  # all widgets (items) shown on the window
        for item in widgetList:
            if item.winfo_children():
                widgetList.extend(item.winfo_children())
        for item in widgetList:
            item.place_forget()

    def showWeatherFinder(self): # location chooser for weather
        tK.Label(self.root, text="Weather Forecast Finder", font=("Calibri", 24), fg="white", bg="#114F69").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(self.root, text="UK Location:", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.466, rely=0.2, anchor="e")
        locationBox = tK.Entry(self.root, width=40) # text box for user entry of location
        locationBox.place(relx=0.468, rely=0.2, anchor="w")
        submit = tK.Button(self.root, text="Go!", command=lambda: self.apiConnect(locationBox.get()), width=50) # passes user input to apiConnect to retrieve weather
        submit.place(relx=0.5, rely=0.275, anchor="center")
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.goHome, image=backImg,compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text


    def apiConnect(self, location): # connects to openweathermap API and returns data from urls below
        currentString = "http://api.openweathermap.org/data/2.5/weather?q=%s,uk&APPID=ed1700ebb4e7bcdbedb1c921d7e197bf" % (location) # for current weather data
        returnedDict1 = requests.get(currentString).json() # returns data in json format in a dictionary
        dailyString = "http://api.openweathermap.org/data/2.5/forecast?q=%s,uk&APPID=ed1700ebb4e7bcdbedb1c921d7e197bf" % (location) # for every 3 hour/5 day forecast
        returnedDict2 = dict(requests.get(dailyString).json()) # as more than one day returned, dictionary of dictionary created
        self.showWeatherResults(returnedDict1, returnedDict2)


    def showWeatherResults(self, currDict, fiveDayDict):
        location = currDict['name']
        lat = str(currDict['coord']['lat'])
        lon = str(currDict['coord']['lon'])
        tomorrow = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days=1), "%Y-%m-%d")
        todayDict = []
        while datetime.datetime.strptime(fiveDayDict['list'][0]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") != tomorrow:
            todayDict.append(fiveDayDict['list'][0])
            del fiveDayDict['list'][0]

        def showToday():
            self.dayLabel.place_forget()
            self.imgLinks.clear()
            self.forgetFrameContents(self.weatherFrame)
            relxCount = 0
            dateText = str("Today - " + datetime.datetime.strptime(todayDict[0]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
            tK.Label(self.root, text=dateText, fg="#B9CBCA", bg="#114F69", font=("Calibri 18")).place(relx=0.5, rely=0.37, anchor="center")
            for each in range(0, len(todayDict)):
                time = datetime.datetime.strptime(todayDict[each]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                canvas = tK.Canvas(self.weatherFrame, width=150, height=500, bg="#B9CBCA", highlightthickness=1)
                canvas.create_text((75, 0), text=time, font=("Calibri 18"), justify="center", anchor="n", width=150)
                iconPathString = "ImageResources/%s@2x.png" % (todayDict[each]['weather'][0]['icon'])
                self.imgLinks.append(tK.PhotoImage(file=iconPathString))  # opens image
                canvas.create_image((75, 30), anchor="n", image=self.imgLinks[each])
                descText = str(todayDict[each]['weather'][0]['description']).title()
                canvas.create_text((75, 120), text=descText, font=("Calibri 16"), justify="center", anchor="n", width=150)#
                temperatureText = int(todayDict[each]['main']['temp'] - 273.15 )
                temperatureText = str(temperatureText)+"°C"
                canvas.create_text((75, 170), text=temperatureText, font=("Calibri 18"), justify="center", anchor="n", width=150)
                canvas.place(x=relxCount, y=0, anchor="nw")
                relxCount += 150

        def showDay(dayNum):
            self.dayLabel.place_forget()
            self.imgLinks.clear()
            self.forgetFrameContents(self.weatherFrame)
            lowerBound = 0
            upperBound = 0
            if dayNum == 0:
                lowerBound = 0
                upperBound = 8
                dateText = str("Tomorrow - " + datetime.datetime.strptime(fiveDayDict['list'][0]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
            elif dayNum == 1:
                lowerBound = 8
                upperBound = 16
                dayText = ((datetime.datetime.today() + datetime.timedelta(days=2)).strftime("%A") + " - ")
                dateText = str(dayText + datetime.datetime.strptime(fiveDayDict['list'][8]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
            elif dayNum == 2:
                lowerBound = 16
                upperBound = 24
                dayText = ((datetime.datetime.today() + datetime.timedelta(days=3)).strftime("%A") + " - ")
                dateText = str(dayText + datetime.datetime.strptime(fiveDayDict['list'][16]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
            elif dayNum == 3:
                lowerBound = 24
                upperBound = 32
                dayText = ((datetime.datetime.today() + datetime.timedelta(days=4)).strftime("%A") + " - ")
                dateText = str(dayText + datetime.datetime.strptime(fiveDayDict['list'][24]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))

            self.dayLabel = tK.Label(self.root, text=dateText, fg="#B9CBCA", bg="#114F69", font=("Calibri 18"))
            self.dayLabel.place(relx=0.5, rely=0.37, anchor="center")
            canvasArr = []

            for each in range(lowerBound, upperBound):
                time = datetime.datetime.strptime(fiveDayDict['list'][each]['dt_txt'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
                canvas = tK.Canvas(self.weatherFrame, width=150, height=500, bg="#B9CBCA", highlightthickness=1)
                canvas.create_text((75, 0), text=time, font=("Calibri 18"), justify="center", anchor="n", width=150)
                iconPathString = "ImageResources/%s@2x.png" % (fiveDayDict['list'][each]['weather'][0]['icon'])
                self.imgLinks.append(tK.PhotoImage(file=iconPathString))  # opens image
                canvasArr.append(canvas)

            relxCount = 0
            for each in range(0, len(canvasArr)):
                canvasArr[each].create_image((75, 30), anchor="n", image=self.imgLinks[each])
                descText = str(fiveDayDict['list'][each]['weather'][0]['description']).title()
                canvasArr[each].create_text((75, 120), text=descText, font=("Calibri 16"), justify="center", anchor="n", width=150)  #
                temperatureText = int(fiveDayDict['list'][each]['main']['temp'] - 273.15)
                temperatureText = str(temperatureText) + "°C"
                canvasArr[each].create_text((75, 170), text=temperatureText, font=("Calibri 18"), justify="center", anchor="n", width=150)
                canvasArr[each].place(x=relxCount, y=0, anchor="nw")
                relxCount += 150

        self.weatherFrame.place(relx=0.6, rely=0.7, anchor="center")
        locationText = location + " / " + lat + " / " + lon
        tK.Label(self.root, text=locationText, fg="#B9CBCA", bg="#114F69", width=100, font=("Calibri 18")).place(relx=0.5, rely=0.33, anchor="center")

        todayButton = tK.Button(self.root, text="Today", command=showToday, width=20)
        todayButton.place(relx=0.3, rely=0.42, anchor="center")
        tomorrowButton = tK.Button(self.root, text="Tomorrow", command=lambda: showDay(0), width=20)
        tomorrowButton.place(relx=0.4, rely=0.42, anchor="center")
        day1Button = tK.Button(self.root, text=(datetime.datetime.today() + datetime.timedelta(days=2)).strftime("%A"), command=lambda: showDay(1), width=20)
        day1Button.place(relx=0.5, rely=0.42, anchor="center")
        day2Button = tK.Button(self.root, text=(datetime.datetime.today() + datetime.timedelta(days=3)).strftime("%A"), command=lambda: showDay(2), width=20)
        day2Button.place(relx=0.6, rely=0.42, anchor="center")
        day3Button = tK.Button(self.root, text=(datetime.datetime.today() + datetime.timedelta(days=4)).strftime("%A"), command=lambda: showDay(3), width=20)
        day3Button.place(relx=0.7, rely=0.42, anchor="center")
        time = str(datetime.datetime.now().strftime("%H:%M")+" - Current")
        canvas = tK.Canvas(self.root, width=200, height=500, bg="#B9CBCA", highlightthickness=1)
        canvas.create_text((100, 0), text=time, font=("Calibri 18"), justify="center", anchor="n", width=200)
        iconPathString = "ImageResources/%s@2x.png" % (currDict['weather'][0]['icon'])
        self.currWeatherIcon = tK.PhotoImage(file=iconPathString)
        canvas.create_image((100, 30), anchor="n", image=self.currWeatherIcon)
        descText = str(currDict['weather'][0]['description']).title()
        canvas.create_text((100, 120), text=descText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        temperatureText = "Temperature: "+ str(int(currDict['main']['temp'] - 273.15)) + "°C"
        canvas.create_text((100, 170), text=temperatureText, font=("Calibri 16"), justify="center", anchor="n",width=200)
        feelsLikeText = "Feels Like: " + str(int(currDict['main']['feels_like'] - 273.15)) + "°C"
        canvas.create_text((100, 200), text=feelsLikeText, font=("Calibri 16"), justify="center", anchor="n",width=200)
        windText = "Wind: " + str(round(currDict['wind']['speed'] * 1.943845,1)) + "kn\n@ " + str(currDict['wind']['deg']) + "°"
        canvas.create_text((100, 230), text=windText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        pressureText = "Pressure: " + str(currDict['main']['pressure']) + "hPa"
        canvas.create_text((100, 290), text=pressureText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        humidityText = "Humidity: " + str(currDict['main']['humidity']) + "%"
        canvas.create_text((100, 320), text=humidityText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        visibilityText = "Visibility: " + str(round(currDict['visibility']*0.000539957,2)) + "nm"
        canvas.create_text((100, 350), text=visibilityText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        sunriseText = "Sunrise: " + datetime.datetime.utcfromtimestamp(currDict['sys']['sunrise']).strftime("%H:%M:%S")
        canvas.create_text((100, 380), text=sunriseText, font=("Calibri 16"), justify="center", anchor="n", width=200)
        sunsetText = "Sunrise: " + datetime.datetime.utcfromtimestamp(currDict['sys']['sunset']).strftime("%H:%M:%S")
        canvas.create_text((100, 410), text=sunsetText, font=("Calibri 16"), justify="center", anchor="n", width=200)

        canvas.place(relx=0.2, rely=0.7, anchor="center")


        self.weatherFrame.update()

class AISScreen(VesselManSys):
    def __init__(self, parent):
        self.root = parent
        self.apiConnect()

    def apiConnect(self):
        sys.excepthook = cefpython.ExceptHook  # To shutdown all CEF processes on error
        cefpython.Initialize()
        #cefpython.CreateBrowserSync(url="https://www.google.com/")
        cefpython.CreateBrowserSync(url="http://localhost/ais.html", window_title="Map of AIS enabled vessels - Provided by Marinetraffic.com")
        cefpython.MessageLoop()

class LogsScreen(VesselManSys):
    def __init__(self, parent):
        self.root = parent



def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    a = VesselManSys(root)
    vms = UserLoginScreen(a)
    root.mainloop()

runApp()