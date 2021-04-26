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
import json
import http.client, urllib.request, urllib.parse
import re

class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Passenger Vessel Management System")  # the window title
        self.root.state("zoomed") # maximises the screen on execution
        self.root.configure(bg="#114F69")

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
            if type(item) == tkcalendar.tooltip.Tooltip or type(item) == tK.Toplevel:
                pass
            else:
                item.pack_forget()
        for item in widgetList:
            if type(item) == tkcalendar.tooltip.Tooltip or type(item) == tK.Toplevel:
                pass
            else:
                item.place_forget()

    def sha256hash(self, string):   # hashes a string with SHA-256
        string = string.encode("utf-8") # encodes the string in utf-8
        hashobject = hashlib.sha256(string) # hashobject = location in memory of hash
        hashedstring = hashobject.hexdigest() # sets hashedstring as the hash from the hashobject
        return hashedstring # returns hash of original string

    def loggedOut(self):
        self.forgetAllWidgets()
        a = UserLoginScreen(self)

    def commonStyles(self):
        tK.Label(self.root, text="Passenger Vessel Management System", font=("Calibri", 28), fg="white", bg="#114F69").place(relx=0.5, rely=0.05, anchor="center")  # window heading text centered at the top available space
        logoutImg = tK.PhotoImage(file="ImageResources/logout.png")  # opens image
        logoutImg = logoutImg.subsample(8, 8)  # changes image size
        logoutBut = tK.Button(self.root, text="  Logout", command=lambda: self.loggedOut(), image=logoutImg,compound="left")  # logs button - compound = justify the image
        logoutBut.photo = logoutImg  # must store the variable as a property of the button
        logoutBut.place(relx=0.95, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

class UserLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent): # constructor
        self.root = parent.root # inherit the root tkinter window from VesselManSys class
        self.credentialFailFlag = False # shows if user login credentials were correct or not - True if incorrect
        self.loginScreen()

    def loginScreen(self):
        if self.credentialFailFlag == True:
            tK.Label(self.root, text="Username or Password as incorrect - Please try again.\n\n\n\n\n\n", font=("Calibri", 20), bg="#114F69").pack(side="bottom") # if user credentials incorrect, shows this at the bottom of window
        tK.Label(self.root, text="\n\nPassenger Vessel Management System\n\n", font=("Calibri", 28), fg="white", bg="#114F69").pack(side="top")  # window heading text centered at the top available space
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
                password = self.pwbox.get() # gets the user input from password box on login screen
                statement = "SELECT * FROM Users WHERE StaffID = '%s' AND Password = '%s';" % (tempSID, self.sha256hash(password)) # paramaterised StaffID & Password to avoid SQL injection
                resultTup = self.dbConnection(statement) # execute the above statement in the database
                if len(resultTup) == 1: # should only return maximum of 1 row
                    self.staffID = tempSID
                    self.credentialFailFlag = False
                    self.loginComplete()
                else:   # if no rows are returned, user login credentials were incorrect
                    self.credentialFailFlag = True
                    self.forgetAllWidgets() # clear screen of widgets
                    self.loginScreen()  # prompt user for login details again

    def loginComplete(self):    # if user login credentials are valid
        if self.credentialFailFlag == False:
            self.forgetAllWidgets() # clear the screen
            h = HomePage(self.root, self.staffID) # home page object passing the root so everything is presented on same window
            h.homeScreen() # show home screen

class HomePage(VesselManSys): # home screen - menu for the different program functionalities
    def __init__(self, parent, staffID):
        self.root = parent # inherit root window from VesselManSys
        self.staffID = staffID
        self.Flag = False
        tK.Label(self.root, text="Passenger Vessel Management System", font=("Calibri", 28), fg="white",bg="#114F69").place(relx=0.5, rely=0.05,anchor="center")  # window heading text centered at the top available space
        logoutImg = tK.PhotoImage(file="ImageResources/logout.png")  # opens image
        logoutImg = logoutImg.subsample(8, 8)  # changes image size
        logoutBut = tK.Button(self.root, text="  Logout", command=lambda: self.logout(), image=logoutImg,compound="left")  # logs button - compound = justify the image
        logoutBut.photo = logoutImg  # must store the variable as a property of the button
        logoutBut.place(relx=0.95, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def logout(self):
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
            aisBut = tK.Button(self.root, text="AIS - External window", command=lambda : self.aisLink(), image=aisImg, compound="top")  # AIS button
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
        accountManagerBut = tK.Button(self.root, text="User Account Mangement", command=lambda : self.UAMLink(), image=accountManagerImg, compound="top")  # accountManager button
        accountManagerBut.photo = accountManagerImg # must store the variable as a property of the button
        accountManagerBut.place(relx=0.7, rely=0.7, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def calendarLink(self):
        c = CalendarScreen(self.root, self.staffID)
        c.showCalendar()

    def weatherLink(self):
        w = WeatherScreen(self.root, self.staffID)
        w.showWeatherFinder()

    def aisLink(self):
        a = AISScreen(self.root)
        a.apiConnect()

    def networkCheck(self, host="http://google.com"): #checks if google.com is accessible, host must be perameter!
        try:
            urllib.request.urlopen(host) # opens host (google.com)
            return True # if connection is successful
        except:
            return False # if connection is unsuccessful

    def tideLink(self):
        t = TideScreen(self.root, self.staffID)
        t.showLocationPicker()

    def logLink(self):
        l = LogsScreen(self.root, self.staffID)
        l.logMenu()

    def UAMLink(self):
        u = UAMScreen(self.root, self.staffID)
        u.checkPrivileges()

    def crewLookupLink(self):
        c = CrewLookupScreen(self.root, self.staffID)
        c.checkPrivileges()

    def emergencyLink(self):
        e = EmergencyScreen(self.root, self.staffID)
        e.checkPrivileges()

    def checklistLink(self):
        ch = ChecklistScreen(self.root, self.staffID)
        ch.checklistHome(0)

class UAMScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID
        self.clearScreen()
        self.tree = tK.ttk.Treeview(self.root, columns=("one"))  # create the Treeview (list) object with 2 columns, #0 and "one - does not show without pack()
        self.treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        self.treeStyle.theme_use("default")  # use the default theme until some specifics are modified below

    def clearScreen(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg, compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def goHome(self):
        self.forgetAllWidgets()  # clear the screen
        h = HomePage(self.root, self.staffID)  # create home screen object
        h.homeScreen()  # show home screen

    def checkPrivileges(self):
        self.clearScreen()
        try:
            self.oldpwbox.delete(0, tK.END)
            self.newpw1.delete(0, tK.END)
            self.newpw2.delete(0, tK.END)
        except Exception:
            pass
        statement = "SELECT * FROM users WHERE staffID = '%s' AND Supervisor = 1;" % self.staffID
        resultTup = self.dbConnection(statement)
        if len(resultTup) != 0:
            self.supervisorUAM()
        else:
            self.subordinateUAM(self.staffID)

    def subordinateUAM(self, sid):
        self.clearScreen()
        tK.Label(self.root, text="User Account Manager", font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Change Password", font=("Calibi 16"), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        if self.staffID == sid:
            tK.Label(self.root, text="Current Password:", font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="e")
            self.oldpwbox = tK.Entry(self.root, show="⚫", width=35)  # text entry box for password
            self.oldpwbox.place(relx=0.5, rely=0.4, anchor="w")
        tK.Label(self.root, text="New Password:", font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.5, rely=0.45, anchor="e")
        self.newpw1 = tK.Entry(self.root, show="⚫", width=35)  # text entry box for password
        self.newpw1.place(relx=0.5, rely=0.45, anchor="w")
        tK.Label(self.root, text="Repeat New Password:", font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.5, rely=0.5, anchor="e")
        self.newpw2 = tK.Entry(self.root, show="⚫", width=35)  # text entry box for password
        self.newpw2.place(relx=0.5, rely=0.5, anchor="w")
        tK.Button(self.root, text="Change Password", command=lambda: self.newPWCheck(sid), width=20, height=2).place(relx=0.5, rely=0.6, anchor="center")

    def supervisorUAM(self):
        tK.Label(self.root, text="User Account Manager", font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Button(self.root, text="Change Password", command=lambda: self.subordinateUAM(self.staffID), width=20, height=2).place(relx=0.55, rely=0.4, anchor="center")
        tK.Button(self.root, text="Change Crew Information", command=lambda: self.accountViewer(), width=20, height=2).place(relx=0.45, rely=0.4, anchor="center")

    def accountViewer(self):
        self.clearScreen()
        self.tree.delete(*self.tree.get_children())
        tK.Label(self.root, text="User Accounts", fg="white", bg="#114F69", font=("Calibri bold", 18)).place(relx=0.5, rely=0.3, anchor="center")
        self.treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 18), foreground="black")  # this is the heading fields for the list
        self.treeStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        scrollbar = tK.ttk.Scrollbar(self.root, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.652, rely=0.383, relheight=0.268, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree["columns"] = ("zero", "one", "two")
        self.tree.heading("zero", text="Staff ID")  # first column header
        self.tree.heading("one", text="First Name")  # second column header
        self.tree.heading("two", text="Surname")  # third hidden column
        self.tree.column("zero", minwidth=120, width=120, anchor=tK.CENTER)  # set the default and minimum width for each column
        self.tree.column("one", minwidth=250, width=250, anchor=tK.CENTER)
        self.tree.column("two", width=250, anchor=tK.CENTER)
        resultsTup = self.dbConnection("SELECT StaffID, FirstName, Surname FROM users;")
        for each in range(0, len(resultsTup)):
            row = self.tree.insert("", index="end", iid=each, text="", values=(resultsTup[each][0], resultsTup[each][1], resultsTup[each][2]))  # insert the values at the end of the current list
        self.tree["show"] = "headings"  # hide the ID column
        self.tree.selection_set("0")  # highlight the first result if exists
        submitBut = tK.Button(self.root, text="Edit Account", command=lambda: self.editAccount(False), width=20, height=2)
        submitBut.place(relx=0.4, rely=0.7, anchor="center")
        delAccBut = tK.Button(self.root, text="Remove Account", command=lambda: self.removeAccount(), width=20, height=2)
        delAccBut.place(relx=0.5, rely=0.7, anchor="center")
        newAccBut = tK.Button(self.root, text="Add Account", command=lambda: self.addAccount(False), width=20, height=2)
        newAccBut.place(relx=0.6, rely=0.7, anchor="center")
        self.tree.place(relx=0.5, rely=0.5, anchor="center", relheight=0.3)  # show the list on screen

    def addAccount(self, hasError):
        if hasError:
            self.clearScreen()
            tK.Label(self.root, text="Please ensure ALL entry boxes are filled correctly before submitting.", fg="red", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.2, anchor="center")
        else:
            self.clearScreen()
        tK.Label(self.root, text="First Name:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.35, anchor="e")
        fnbox = tK.Entry(self.root, width=40)
        fnbox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(self.root, text="Surname:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.4, anchor="e")
        lnbox = tK.Entry(self.root, width=40)
        lnbox.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(self.root, text="Phone Number:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.45, anchor="e")
        pnbox = tK.Entry(self.root, width=40)
        pnbox.place(relx=0.51, rely=0.45, anchor="w")
        tK.Label(self.root, text="DOB (YYYY-MM-DD):", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.5, anchor="e")
        dobbox = tK.Entry(self.root, width=40)
        dobbox.place(relx=0.51, rely=0.5, anchor="w")
        tK.Label(self.root, text="Next of Kin:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.55, anchor="e")
        nokbox = tK.Entry(self.root, width=40)
        nokbox.place(relx=0.51, rely=0.55, anchor="w")
        tK.Label(self.root, text="Supervisor:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.6, anchor="e")
        checkState = tK.IntVar()
        supButton = tK.Checkbutton(self.root, variable=checkState, bg="#114F69", activebackground="#114F69")
        supButton.place(relx=0.51, rely=0.6, anchor="w")
        tK.Label(self.root, text="Password:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.65, anchor="e")
        pwbox = tK.Entry(self.root, width=40)
        pwbox.place(relx=0.51, rely=0.65, anchor="w")
        subBut = tK.Button(self.root, text="Submit New Details", command=lambda: self.newAccountBackend(fnbox.get(), lnbox.get(), pnbox.get(), dobbox.get(), nokbox.get(), checkState.get(), pwbox.get()))
        subBut.place(relx=0.55, rely=0.7, anchor="center")

    def newAccountBackend(self, fn, sn, pn, dob, nok, sup, pw):
        def anyNums(str):
            return any(each.isdigit() for each in str)

        if len(fn) == 0 or len(sn) == 0 or len(pn) < 10 or len(dob) == 0 or len(nok) == 0:
            self.addAccount(True)
            return
        if anyNums(fn) or anyNums(sn):
            self.addAccount(True)
            return
        try:
            testdob = datetime.datetime.strptime(dob, "%Y-%m-%d")
        except Exception:
            self.addAccount(True)
            return
        statement1 = "INSERT INTO users (password, FirstName, Surname, PhoneNum, DOB, nokName, Supervisor) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (self.sha256hash(pw), fn, sn, pn, dob, nok, sup)
        self.dbConnection(statement1)
        statement2 = "SELECT StaffID FROM users where FirstName = '%s' AND Surname = '%s' AND PhoneNum = '%s' AND nokName = '%s';" % (fn, sn, pn, nok)
        resultTup = self.dbConnection(statement2)
        if len(resultTup) == 0:
            self.addAccount(True)
        else:
            self.clearScreen()
            tK.Label(self.root, text="Successfully added staff member.", font=("Calibri bold", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
            tK.Label(self.root, text="Staff ID: %s" % resultTup[0], font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
            tK.Label(self.root, text="Password: %s" % pw, font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.5, anchor="center")
            tK.Button(self.root, text="Home")

    def removeAccount(self):
        acc = self.tree.item(self.tree.selection())['values']
        self.clearScreen()
        tK.Label(self.root, text="Are you sure you want to delete this account?\nThis cannot be undone.", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="Staff ID: %s" % acc[0], fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="First Name: %s" % acc[1], fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.45, anchor="center")
        tK.Label(self.root, text="Surname: %s" % acc[2], fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.5, anchor="center")
        yesBut = tK.Button(self.root, text="Yes, delete this account.", command=lambda: self.delAccBackend(acc[0]), width=20, height=2)
        yesBut.place(relx=0.4, rely=0.65, anchor="center")
        noBut = tK.Button(self.root, text="No, cancel.", command=lambda: self.accountViewer(), width=20, height=2)
        noBut.place(relx=0.6, rely=0.65, anchor="center")

    def delAccBackend(self, sid):
        statement = "DELETE FROM users WHERE StaffID = %s;" % sid
        self.dbConnection(statement)
        self.clearScreen()
        self.accountViewer()

    def editAccount(self, hasError):
        if hasError:
            self.clearScreen()
            tK.Label(self.root, text="Please ensure ALL entry boxes are filled correctly before submitting.", fg="red", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.2, anchor="center")
        else:
            self.clearScreen()
        acc = self.tree.item(self.tree.selection())["values"]
        statement = "SELECT * FROM users WHERE staffID = '%s';" % acc[0]
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Staff ID: %s" % acc[0], fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="First Name:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.35, anchor="e")
        fnbox = tK.Entry(self.root, width=40)
        fnbox.place(relx=0.51, rely=0.35 , anchor="w")
        fnbox.insert(0, resultTup[0][2])
        tK.Label(self.root, text="Surname:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.4, anchor="e")
        lnbox = tK.Entry(self.root, width=40)
        lnbox.place(relx=0.51, rely=0.4, anchor="w")
        lnbox.insert(0, resultTup[0][3])
        tK.Label(self.root, text="Phone Number:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.45, anchor="e")
        pnbox = tK.Entry(self.root, width=40)
        pnbox.place(relx=0.51, rely=0.45, anchor="w")
        pnbox.insert(0, resultTup[0][4])
        tK.Label(self.root, text="DOB (YYYY-MM-DD):", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.5, anchor="e")
        dobbox = tK.Entry(self.root, width=40)
        dobbox.place(relx=0.51, rely=0.5, anchor="w")
        dobbox.insert(0, resultTup[0][5])
        tK.Label(self.root, text="Next of Kin:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.55, anchor="e")
        nokbox = tK.Entry(self.root, width=40)
        nokbox.place(relx=0.51, rely=0.55, anchor="w")
        nokbox.insert(0, resultTup[0][6])
        tK.Label(self.root, text="Supervisor:", fg="white", bg="#114F69", font=("Calibri", 15)).place(relx=0.49, rely=0.6, anchor="e")
        checkState = tK.IntVar()
        supButton = tK.Checkbutton(self.root, variable=checkState, bg="#114F69", activebackground="#114F69")
        if resultTup[0][7] == 1:
            supButton.select()
        supButton.place(relx=0.51, rely=0.6, anchor="w")
        pwBut = tK.Button(self.root, text="Change Account Password", command=lambda: self.subordinateUAM(acc[0]))
        pwBut.place(relx=0.45, rely=0.7, anchor="center")
        subBut = tK.Button(self.root, text="Submit New Details", command=lambda: self.editAccountBackend(acc[0], fnbox.get(), lnbox.get(), pnbox.get(), dobbox.get(), nokbox.get(), checkState.get()))
        subBut.place(relx=0.55, rely=0.7, anchor="center")

    def editAccountBackend(self, sid, fn, sn, pn, dob, nok, sup):
        def anyNums(str):
            return any(each.isdigit() for each in str)

        if len(fn) == 0 or len(sn) == 0 or len(pn) < 10 or len(dob) == 0 or len(nok) == 0:
            self.editAccount(True)
            return
        if anyNums(fn) or anyNums(sn):
            self.editAccount(True)
            return
        try:
            testdob = datetime.datetime.strptime(dob, "%Y-%m-%d")
        except Exception:
            self.editAccount(True)
            return
        statement = "UPDATE users SET firstName = '%s' , surname = '%s' , phoneNum = '%s' , dob = '%s' , nokName = '%s' , supervisor = %s WHERE StaffID = %s" % (fn, sn, pn, dob, nok, sup, sid)
        self.dbConnection(statement)
        self.goHome()

    def newPWCheck(self, sid):
        if self.staffID == sid:
            statement = "SELECT * FROM users WHERE StaffID = '%s' AND password = '%s';" % (sid, self.sha256hash(self.oldpwbox.get()))
        else:
            statement = "SELECT * FROM users WHERE StaffID = '%s';" % (sid)
        resultTup = self.dbConnection(statement)
        if len(resultTup) != 0:
            if self.newpw1.get() == self.newpw2.get():
                statement = "UPDATE users SET password = '%s' WHERE StaffID = '% s'" % (self.sha256hash(self.newpw1.get()), sid)
                try:
                    self.dbConnection(statement)
                except Exception:
                    self.newPWError(1)
                    return
                tK.Label(self.root, text="Password Changed Successfully", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.6, anchor="center")
            else:
                self.newPWError(3)
        else:
            self.newPWError(2)

    def newPWError(self, mode):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg, compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        if mode == 1:
            tK.Label(self.root, text="An error occurred while updating your password. Your password has not been changed.", font=("Calibri 18"), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        elif mode == 2:
            tK.Label(self.root, text="Your current password is incorrect. Please try again.", font=("Calibri 18"), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        elif mode == 3:
            tK.Label(self.root, text="Your new passwords don't match. Please try again.", font=("Calibri 18"), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        tK.Button(self.root, text="Try Again", command=lambda: self.checkPrivileges(self.staffID), width=20, height=2).place(relx=0.5, rely=0.5, anchor="center")

class CalendarScreen(VesselManSys): # For showing and using the calendar feature
    def __init__(self, parent, staffID):
        self.root = parent #inherit root window from parent (vesselManSys)
        self.staffID = staffID
        self.commonStyles()
        self.calendarCursor = ""    # define class member variables
        self.tree = tK.ttk.Treeview(self.root, columns=("one"))  # create the Treeview (list) object with 2 columns, #0 and "one - does not show without pack()
        self.treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        self.treeStyle.theme_use("default")  # use the default theme until some specifics are modified below

    def goHome(self): # called from Back button on showCalendar()
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen

    def showCalendar(self):  # show the calendar on screen
        self.forgetAllWidgets()
        self.commonStyles()
        todaydate = datetime.date.today()   # get today date and time
        yearnow = int(todaydate.strftime("%Y")) # get the year from that date/time
        monthnow = int(todaydate.strftime("%m")) # get the month
        datenow = int(todaydate.strftime("%d")) # get the day
        self.mainCal = tkcalendar.Calendar(self.root, font=("Calibri", 20), selectmode="day", locale="en_GB", year=yearnow, month=monthnow, day=datenow) # make a calendar, selectable by day, default to today date
        self.mainCal.place(relx=0.5, rely=0.375, anchor="center", relheight=0.5, relwidth=0.5) # show calendar on screen
        tK.Label(self.root, text="\n", bg="#114F69").pack() # for spacing, blank new line

        self.mainCal.bind("<<CalendarSelected>>",self.dateSelect) # bind the mouse click of a date in calendar to dateSelect function
        self.viewEventsOnDay()

        addImg = tK.PhotoImage(file="ImageResources/plus.png")  # opens image
        addImg = addImg.subsample(6, 6)  # changes image size
        addBut = tK.Button(self.root, text="Add Event", command=lambda: self.addEvent(), image=addImg,compound="top")  # add event button
        addBut.photo = addImg  # must store the variable as a property of the button
        addBut.place(relx=0.25, rely=0.75,anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        addImg = tK.PhotoImage(file="ImageResources/minus.png")  # opens image
        addImg = addImg.subsample(6, 6)  # changes image size
        addBut = tK.Button(self.root, text="Remove Event", command=lambda: self.removeEvent(), image=addImg,compound="top")  # remove event button
        addBut.photo = addImg  # must store the variable as a property of the button
        addBut.place(relx=0.25, rely=0.9,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def viewEventsOnDay(self): # shows a list of events happening ona particular day
        self.tree.delete(*self.tree.get_children()) # removes all items in list
        self.treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 18), foreground="black")  # this is the heading fields for the list
        self.treeStyle.configure("Treeview", font=("Calibri", 12))   # the entry fields for the list
        if self.calendarCursor == "":
            self.calendarCursor = datetime.datetime.today().strftime("%Y-%m-%d")
        statement = "SELECT CONVERT(timeStarts,CHAR), CONVERT(timeEnds,CHAR), eventTitle, eventDetails FROM calendar WHERE Date = '%s' ORDER BY timeStarts ASC;" % (self.calendarCursor) # return the time and event details for the specified date
        results = self.dbConnection(statement) # execute the SQL statement in the database
        if self.tree.winfo_exists() == 1: # if a Treeview (list object) already exists - destroy it
            self.tree.pack_forget() # remove the widget from screen
        scrollbar = tK.ttk.Scrollbar(self.root, command=self.tree.yview, orient="vertical") # vertical scrollbar for the list box
        scrollbar.place(relx=0.66, rely=0.683, relheight=0.268, relwidth=0.010) # set the position on screen and size relative to screen size
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
                    row = self.tree.insert("", index=num+1, iid=num+1, text="", values=(resultEventTimeString,resultEventTitle,resultDetails))  # insert the values at the end of the current list
            else: # show the whole string if it fits in the column
                if num < len(results): # stops out of range error
                    row = self.tree.insert("", index="end", iid=num, text="", values=(resultEventTimeString,resultEventTitle,resultDetails))  # insert the values at the end of the current list

        if len(results) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.tree["show"] = "headings" # hide the ID column
        self.tree.bind("<Double-1>", self.viewEventDetails) # bind a double-click event to the viewEventDetails member function
        self.tree.place(relx=0.5, rely=0.8, anchor="center", relheight=0.3)   # show the list on screen

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
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID
        self.forgetAllWidgets() # clear window
        self.commonStyles()
        self.imgLinks = [] # will contain file paths to images used
        self.currWeatherIcon = str() # the file path for the weather icon at current time
        self.dayLabel = tK.Label(self.root, text="", fg="#B9CBCA", bg="#114F69", font=("Calibri 18")) # defined but not placed on screen, will be day/date of results
        self.weatherFrame = tK.Frame(self.root, width=1200, height=500, bg="#729796") # for upto 8 canvases/weather times to fit into

    def goHome(self): # called from Back button on showWeatherFinder()
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen

    def forgetFrameContents(self, frame): # works as vesselManSys.forgetAllWidgets() but for frame not window
        widgetList = frame.winfo_children()  # all widgets (items) shown on the window
        for item in widgetList:
            if item.winfo_children():
                widgetList.extend(item.winfo_children())
        for item in widgetList:
            item.place_forget()

    def showWeatherFinder(self): # location chooser for weather
        tK.Label(self.root, text="Weather Forecast Finder", font=("Calibri", 24), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        tK.Label(self.root, text="UK Location:", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.466, rely=0.225, anchor="e")
        locationBox = tK.Entry(self.root, width=40) # text box for user entry of location
        locationBox.place(relx=0.468, rely=0.225, anchor="w")
        submit = tK.Button(self.root, text="Go!", command=lambda: self.apiConnect(locationBox.get()), width=50) # passes user input to apiConnect to retrieve weather
        submit.place(relx=0.5, rely=0.275, anchor="center")
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.goHome, image=backImg,compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def apiConnect(self, location): # connects to openweathermap API and returns data from urls below
        file = open("weatherAPIKeys.txt", "r") # read API key from text file
        key = file.read() # key = contents of text file
        currentString = "http://api.openweathermap.org/data/2.5/weather?q=%s,uk&APPID=%s" % (location, key) # for current weather data
        returnedDict1 = requests.get(currentString).json() # returns data in json format in a dictionary
        dailyString = "http://api.openweathermap.org/data/2.5/forecast?q=%s,uk&APPID=%s" % (location, key) # for every 3 hour/5 day forecast
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

                feelsLikeText = "Feels Like: " + str(int(fiveDayDict['list'][0]['main']['feels_like'] - 273.15)) + "°C"
                canvas.create_text((75, 200), text=feelsLikeText, font=("Calibri 16"), justify="center", anchor="n", width=200)
                windText = "Wind: " + str(round(fiveDayDict['list'][0]['wind']['speed'] * 1.943845, 1)) + "kn\n@ " + str(fiveDayDict['list'][0]['wind']['deg']) + "°"
                canvas.create_text((75, 230), text=windText, font=("Calibri 16"), justify="center", anchor="n", width=200)
                pressureText = "Pressure: " + str(fiveDayDict['list'][0]['main']['pressure']) + "hPa"
                canvas.create_text((75, 300), text=pressureText, font=("Calibri 12"), justify="center", anchor="n", width=200)
                humidityText = "Humidity: " + str(fiveDayDict['list'][0]['main']['humidity']) + "%"
                canvas.create_text((75, 330), text=humidityText, font=("Calibri 14"), justify="center", anchor="n", width=200)
                visibilityText = "Visibility: " + str(round(fiveDayDict['list'][0]['visibility'] * 0.000539957, 2)) + "nm"
                canvas.create_text((75, 360), text=visibilityText, font=("Calibri 14"), justify="center", anchor="n", width=200)

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
            dayCount = lowerBound
            for each in range(0, len(canvasArr)):
                canvasArr[each].create_image((75, 30), anchor="n", image=self.imgLinks[each])
                descText = str(fiveDayDict['list'][dayCount]['weather'][0]['description']).title()
                canvasArr[each].create_text((75, 120), text=descText, font=("Calibri 16"), justify="center", anchor="n", width=150)  #
                temperatureText = int(fiveDayDict['list'][dayCount]['main']['temp'] - 273.15)
                temperatureText = str(temperatureText) + "°C"
                canvasArr[each].create_text((75, 170), text=temperatureText, font=("Calibri 18"), justify="center", anchor="n", width=150)
                canvasArr[each].place(x=relxCount, y=0, anchor="nw")
                feelsLikeText = "Feels Like: " + str(int(fiveDayDict['list'][dayCount]['main']['feels_like'] - 273.15)) + "°C"
                canvasArr[each].create_text((75, 200), text=feelsLikeText, font=("Calibri 16"), justify="center", anchor="n",width=200)
                windText = "Wind: " + str(round(fiveDayDict['list'][dayCount]['wind']['speed'] * 1.943845, 1)) + "kn\n@ " + str(fiveDayDict['list'][dayCount]['wind']['deg']) + "°"
                canvasArr[each].create_text((75, 230), text=windText, font=("Calibri 16"), justify="center", anchor="n", width=200)
                pressureText = "Pressure: " + str(fiveDayDict['list'][dayCount]['main']['pressure']) + "hPa"
                canvasArr[each].create_text((75, 300), text=pressureText, font=("Calibri 12"), justify="center", anchor="n", width=200)
                humidityText = "Humidity: " + str(fiveDayDict['list'][dayCount]['main']['humidity']) + "%"
                canvasArr[each].create_text((75, 330), text=humidityText, font=("Calibri 14"), justify="center", anchor="n", width=200)
                visibilityText = "Visibility: " + str(round(fiveDayDict['list'][dayCount]['visibility'] * 0.000539957, 2)) + "nm"
                canvasArr[each].create_text((75, 360), text=visibilityText, font=("Calibri 14"), justify="center", anchor="n", width=200)
                dayCount += 1
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
        canvas.create_text((100, 290), text=pressureText, font=("Calibri 12"), justify="center", anchor="n", width=200)
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

    def apiConnect(self):
        sys.excepthook = cefpython.ExceptHook  # To shutdown all CEF processes on error
        cefpython.Initialize()
        cefpython.CreateBrowserSync(url="http://localhost/ais.html", window_title="Map of AIS enabled vessels - Provided by Marinetraffic.com")
        cefpython.MessageLoop()

class LogsScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg, compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def goHome(self):
        self.forgetAllWidgets()  # clear the screen
        h = HomePage(self.root, self.staffID)  # create home screen object
        h.homeScreen()  # show home screen

    def logMenu(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        dailyBut = tK.Button(self.root, text="Trip Log", command=lambda: self.tripLog(0), width=40, height=4)
        dailyBut.place(relx=0.25, rely=0.3, anchor="center")
        incidentBut = tK.Button(self.root, text="Incident Log", command=lambda: self.incidentLog(0), width=40, height=4)
        incidentBut.place(relx=0.5, rely=0.3, anchor="center")
        radioBut = tK.Button(self.root, text="Radio Log", command=lambda: self.radioLog(0), width=40, height=4)
        radioBut.place(relx=0.75, rely=0.3, anchor="center")
        fuelBut = tK.Button(self.root, text="Fuel Log", command=lambda: self.fuelLog(0), width=40, height=4)
        fuelBut.place(relx=0.25, rely=0.5, anchor="center")
        maintenanceBut = tK.Button(self.root, text="Maintenance Log", command=lambda: self.maintenanceLog(0), width=40, height=4)
        maintenanceBut.place(relx=0.5, rely=0.5, anchor="center")
        miscBut = tK.Button(self.root, text="Miscellaneous Log", command=lambda: self.miscLog(0), width=40, height=4)
        miscBut.place(relx=0.75, rely=0.5, anchor="center")

    def tripLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure('TNotebook', tabposition='n')
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height()-450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Log Entries")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height()-450, bg="#729796")
        tabHolder.add(tab2, text="Create New Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree= tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.8313, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('dt', 'df', 'ati', 'ato')
        self.tree.column("#0", width=125, minwidth=125, stretch="no")
        self.tree.column("dt", width=150, minwidth=150, stretch="no")
        self.tree.column("df", width=220, minwidth=220, stretch="no")
        self.tree.column("ati", width=150, minwidth=150, stretch="no")
        self.tree.column("ato", width=220, minwidth=220, stretch="no")
        self.tree.heading('#0', text="Date", anchor="w")
        self.tree.heading('dt', text="Departure Time", anchor="w")
        self.tree.heading('df', text="Departure From", anchor="w")
        self.tree.heading('ati', text="Arrival Time", anchor="w")
        self.tree.heading('ato', text="Arrival At", anchor="w")
        statement = "SELECT DateAndTime, DepartureTime, DepartingFrom, ETA, HeadingTo FROM triplog ORDER BY DateAndTime;"
        resultTup = self.dbConnection(statement)
        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y") # reformat each date value into UK common style (DD/MM/YYYY)
            self.tree.insert("", index="end", iid=each, text=eachDate, values=(resultTup[each][1], resultTup[each][2], resultTup[each][3], resultTup[each][4])) # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewEntryDetails)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)
        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure entered values are in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.76, anchor="center")

        tK.Label(tab2, text="New Trip Log Entry", font=("Calibri bold", 20), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab2, text="Departure Date:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        dateBox = tkcalendar.DateEntry(tab2, width=27)
        dateBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Vessel Name:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.3, anchor="e")
        vNameBox = tK.Entry(tab2, width=30)
        vNameBox.place(relx=0.51, rely=0.3, anchor="w")
        tK.Label(tab2, text="Master Staff ID:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        MSIDBox = tK.Entry(tab2, width=30)
        MSIDBox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Weather / Wind:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.4, anchor="e")
        weatherBox = tK.Entry(tab2, width=30)
        weatherBox.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(tab2, text="Number of Crew:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.45, anchor="e")
        crewNumBox = tK.Entry(tab2, width=30)
        crewNumBox.place(relx=0.51, rely=0.45, anchor="w")
        tK.Label(tab2, text="Departing From:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.5, anchor="e")
        depFromBox = tK.Entry(tab2, width=30)
        depFromBox.place(relx=0.51, rely=0.5, anchor="w")
        tK.Label(tab2, text="Departure Time (HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.55, anchor="e")
        depTimeBox = tK.Entry(tab2, width=30)
        depTimeBox.place(relx=0.51, rely=0.55, anchor="w")
        tK.Label(tab2, text="Heading To:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.6, anchor="e")
        headingBox = tK.Entry(tab2, width=30)
        headingBox.place(relx=0.51, rely=0.6, anchor="w")
        tK.Label(tab2, text="Arrival Time (HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.65, anchor="e")
        arrTimeBox = tK.Entry(tab2, width=30)
        arrTimeBox.place(relx=0.51, rely=0.65, anchor="w")
        tK.Label(tab2, text="Number of Passengers:", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.7, anchor="e")
        paxNumBox = tK.Entry(tab2, width=30)
        paxNumBox.place(relx=0.51, rely=0.7, anchor="w")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newTripBackend(dateBox.get(), vNameBox.get(), MSIDBox.get(), weatherBox.get(), crewNumBox.get(), depFromBox.get(), depTimeBox.get(), headingBox.get(), arrTimeBox.get(), paxNumBox.get()), width=25, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="n")

    def newTripBackend(self, date, vName, MSID, weather, crewNum, depFrom, depTime, headingTo, arrTime, paxNum):
        if not re.match(r"([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]", depTime): # regex for 24h time, if no match, error
            self.tripLog(1)
            return
        if not re.match(r"([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]", arrTime): # regex for 24h time, if no match, error
            self.tripLog(1)
            return
        if not crewNum.isdecimal(): # is crewNum contains non numerical character, error
            self.tripLog(1)
            return
        if not paxNum.isdecimal(): # is crewNum contains non numerical character, error
            self.tripLog(1)
            return
        result1 = self.dbConnection("SELECT StaffID FROM users WHERE supervisor = 1")
        foundSID = False
        for each in result1: # check is MSID is in list of supervisor/master staffIDs
            if each[0] == int(MSID):
                foundSID = True
        if foundSID == False:
            self.tripLog(1)
            return
        dateList = date.split("/") # split in to month, day, year
        if len(dateList[0]) == 1: # if length of month = 1, pad with leading 0
            dateList[0] = "0" + dateList[0]
        if len(dateList[1]) == 1: # if length of day = 1, pad with leading 0
            dateList[1] = "0" + dateList[1]
        if len(dateList[2]) == 2: # if length of year = 2 (like 21 not 2021), pad with leading 20
            dateList[2] = "20" + dateList[2]
        separator = "/" # what to join date elements with
        date = datetime.datetime.strptime(separator.join(dateList), "%m/%d/%Y").strftime("%Y-%m-%d") # join date elements together and reformat as SQL format (YYYY-MM-DD)
        result2 = self.dbConnection("SELECT * FROM triplog WHERE DepartureDate = '%s' AND DepartureTime = '%s';" % (date, depTime))
        if len(result2) != 0:
            self.tripLog(1)
        statement = "INSERT INTO triplog (DepartureDate, ShipName, MasterID, Weather, NumOfCrew, DepartingFrom, DepartureTime, HeadingTo, ETA, NumOfPax) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (date, vName, MSID, weather, crewNum, depFrom, depTime, headingTo, arrTime, paxNum)
        self.dbConnection(statement)
        self.forgetAllWidgets()
        self.commonStyles()
        self.tripLog(0)
        return

    def viewEntryDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.tripLog, image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        date = datetime.datetime.strptime(self.tree.item(self.tree.selection())["text"], "%d/%m/%Y").strftime("%Y-%m-%d")
        entryDict = self.tree.item(self.tree.selection())["values"] # retrieve values relating to the row picked from the list
        statement = "SELECT * FROM triplog WHERE DepartureDate = '%s' AND DepartureTime = '%s';" % (date, entryDict[0])
        resultTup = self.dbConnection(statement)[0]

        tK.Label(self.root, text="Log Entry Details", font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        tK.Label(self.root, text="Date and Time Submitted: "+resultTup[0].strftime("%d/%m/%Y %H:%M:%S"), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Departure Date: "+resultTup[1].strftime("%d/%m/%Y"), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="Vessel Name: "+resultTup[2], font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.35, anchor="center")
        tK.Label(self.root, text="Weather Conditions: "+resultTup[4], font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="Departure From: "+resultTup[6], font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.5, anchor="center")
        tK.Label(self.root, text="Departure Time: "+str(resultTup[7]), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.55, anchor="center")
        tK.Label(self.root, text="Arrival At: "+resultTup[8], font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.65, anchor="center")
        tK.Label(self.root, text="Arrival Time: "+str(resultTup[9]), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.7, anchor="center")
        tK.Label(self.root, text="Master Staff ID: "+str(resultTup[3]), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.8, anchor="center")
        tK.Label(self.root, text="Number of Crew: "+str(resultTup[5]), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.85, anchor="center")
        tK.Label(self.root, text="Number of Passengers: "+str(resultTup[10]), font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.9, anchor="center")

    def incidentLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.configure('TNotebook', tabposition='n')
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Incidents")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Incident Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.8062, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('msid', 'it')
        self.tree.column("#0", width=250, minwidth=250, stretch="no")
        self.tree.column("msid", width=250, minwidth=250, stretch="no")
        self.tree.column("it", width=300, minwidth=300, stretch="no")
        self.tree.heading('#0', text="Incident Date and Time", anchor="w")
        self.tree.heading('msid', text="Master Name", anchor="w")
        self.tree.heading('it', text="Incident Type", anchor="w")
        statement = "SELECT DateAndTime, FirstName, Surname, IncidentType FROM incidentlog JOIN users ON incidentlog.MasterID = users.StaffID;"
        resultTup = self.dbConnection(statement)

        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y %H:%M:%S") # reformat each date value into UK common style (DD/MM/YYYY)
            nameStr = str(resultTup[each][1] + " " + resultTup[each][2])
            self.tree.insert("", index="end", iid=each, text=eachDate, values=(nameStr, resultTup[each][3])) # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewIncidentDetails)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure date, time and Staff ID entries are in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.85, anchor="center")

        tK.Label(tab2, text="New Incident Log Entry", font=("Calibri bold", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="Date and Time (YYYY-MM-DD HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.15, anchor="e")
        dateandtimeBox = tK.Entry(tab2, width=30)
        dateandtimeBox.place(relx=0.51, rely=0.15, anchor="w")
        tK.Label(tab2, text="Master Staff ID: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        msidBox = tK.Entry(tab2, width=30)
        msidBox.place(relx=0.51, rely=0.2, anchor="w")
        tK.Label(tab2, text="Other Staff ID Involved: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        osidBox = tK.Entry(tab2, width=30)
        osidBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Incident Type: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.3, anchor="e")
        itBox = tK.Entry(tab2, width=30)
        itBox.place(relx=0.51, rely=0.3, anchor="w")
        tK.Label(tab2, text="Police Notified: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        checkState1 = tK.IntVar()
        pnButton = tK.Checkbutton(tab2, variable=checkState1, bg="#729796", activebackground="#729796")
        pnButton.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Ambulance Called: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.4, anchor="e")
        checkState2 = tK.IntVar()
        acButton = tK.Checkbutton(tab2, variable=checkState2, bg="#729796", activebackground="#729796")
        acButton.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(tab2, text="Fire Service Called: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.45, anchor="e")
        checkState3 = tK.IntVar()
        fcButton = tK.Checkbutton(tab2, variable=checkState3, bg="#729796", activebackground="#729796")
        fcButton.place(relx=0.51, rely=0.45, anchor="w")
        tK.Label(tab2, text="Coastguard Called: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.5, anchor="e")
        checkState4 = tK.IntVar()
        ccButton = tK.Checkbutton(tab2, variable=checkState4, bg="#729796", activebackground="#729796")
        ccButton.place(relx=0.51, rely=0.5, anchor="w")
        tK.Label(tab2, text="Designated Person Informed: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.55, anchor="e")
        checkState5 = tK.IntVar()
        dpiButton = tK.Checkbutton(tab2, variable=checkState5, bg="#729796", activebackground="#729796")
        dpiButton.place(relx=0.51, rely=0.55, anchor="w")
        tK.Label(tab2, text="MCA/MAIB Informed: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.6, anchor="e")
        checkState6 = tK.IntVar()
        mcaiButton = tK.Checkbutton(tab2, variable=checkState6, bg="#729796", activebackground="#729796")
        mcaiButton.place(relx=0.51, rely=0.6, anchor="w")#
        tK.Label(tab2, text="Description of Incident (Max. 3000 Characters): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.5, rely=0.65, anchor="center")
        descBox = tK.Text(tab2, width=100, height=5)
        descBox.place(relx=0.5, rely=0.67, anchor="n")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newIncidentBackend(dateandtimeBox.get(), msidBox.get(), osidBox.get(), itBox.get(), checkState1, checkState2, checkState3, checkState4, checkState5, checkState6, descBox.get("1.0",'end-1c')), width=30, height=2)
        subBut.place(relx=0.5, rely=0.95, anchor="center")

    def newIncidentBackend(self, dateAndTime, masterSID, otherSID, incidentType, polNotif, ambCalled, fireCalled, cgCalled, dpInformed, mcaInformed, description):
        try:
            dateAndTime = datetime.datetime.strptime(dateAndTime, "%Y-%m-%d %H:%M")
        except Exception:
            self.incidentLog(1)
            return
        if not masterSID.isdecimal():
            self.incidentLog(1)
            return
        if not otherSID.isdecimal():
            self.incidentLog(1)
            return
        if len(incidentType) == 0:
            self.incidentLog(1)
            return
        if len(description) < 10:
            self.incidentLog(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s' AND Supervisor = 1;" % (masterSID)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.incidentLog(1)
            return
        statement2 = """INSERT INTO incidentlog 
        (DateAndTime, MasterID, StaffIDInvolved, IncidentType, PoliceNotified, AmbulanceCalled, FireServiceCalled, CoastguardCalled, DesignatedPersonInformed, MCAMAIBInformed, Description)
        VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
        """ % (dateAndTime, masterSID, otherSID, incidentType, polNotif.get(), ambCalled.get(), fireCalled.get(), cgCalled.get(), dpInformed.get(), mcaInformed.get(), description)
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.incidentLog(0)
        return

    def viewIncidentDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.incidentLog(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        entryDict = self.tree.item(self.tree.selection())["values"]  # retrieve values relating to the row picked from the list
        dateAndTime = datetime.datetime.strptime(self.tree.item(self.tree.selection())["text"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")  # retrieve row #0 from tree
        statement = "SELECT DateAndTime, MasterID, StaffIDInvolved, IncidentType, PoliceNotified, AmbulanceCalled, FireServiceCalled, CoastguardCalled, DesignatedPersonInformed, MCAMAIBInformed, Description, firstName, Surname FROM incidentlog JOIN users ON incidentlog.MasterID=users.StaffID WHERE DateAndTime = '%s'" % dateAndTime
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Incident Details", font=("Calibri bold", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        titleText = resultTup[0][3] + " - " + resultTup[0][0].strftime("%A %d %B %Y")
        tK.Label(self.root, text=titleText, font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Master Staff ID at time: "+str(resultTup[0][1]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="Master at time: "+resultTup[0][11]+" "+resultTup[0][12], font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.35, anchor="center")
        tK.Label(self.root, text="Other Involved Staff ID: "+str(resultTup[0][2]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="Police Notified: "+str(resultTup[0][4]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.45, anchor="center")
        tK.Label(self.root, text="Ambulance Called: "+str(resultTup[0][5]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.5, anchor="center")
        tK.Label(self.root, text="Fire Service Called: "+str(resultTup[0][6]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.55, anchor="center")
        tK.Label(self.root, text="Coastguard Called: "+str(resultTup[0][7]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.6, anchor="center")
        tK.Label(self.root, text="Designated Person Informed: "+str(resultTup[0][8]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.65, anchor="center")
        tK.Label(self.root, text="MCA / MAIB Informed: "+str(resultTup[0][9]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.7, anchor="center")
        tK.Label(self.root, text="Description of incident:\n\n"+str(resultTup[0][10]), justify="center", wraplength=800, font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.775, anchor="center")

    def radioLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabStyle.configure('TNotebook', tabposition='n')
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Radio Communication Logs")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Radio Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.8042, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('scl', 'scd')
        self.tree.column("#0", width=300, minwidth=300, stretch="no")
        self.tree.column("scl", width=275, minwidth=275, stretch="no")
        self.tree.column("scd", width=275, minwidth=275, stretch="no")
        self.tree.heading('#0', text="Date and Time", anchor="w")
        self.tree.heading('scl', text="Station Calling", anchor="w")
        self.tree.heading('scd', text="Station Called", anchor="w")
        statement = "SELECT DateAndTime, StationCalling, StationCalled FROM radiolog;"
        resultTup = self.dbConnection(statement)

        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y %H:%M:%S")  # reformat each date value into UK common style (DD/MM/YYYY)
            self.tree.insert("", index="end", iid=each, text=eachDate,values=(resultTup[each][1], resultTup[each][2]))  # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0")  # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewRadioTransmissionDetails)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure date, time and Staff ID entries are in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.9, anchor="center")

        tK.Label(tab2, text="New Radio Transmission Entry", font=("Calibri bold", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="Date and Time (YYYY-MM-DD HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.15, anchor="e")
        dateandtimeBox = tK.Entry(tab2, width=30)
        dateandtimeBox.place(relx=0.51, rely=0.15, anchor="w")
        tK.Label(tab2, text="Station Calling: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        callingBox = tK.Entry(tab2, width=30)
        callingBox.place(relx=0.51, rely=0.2, anchor="w")
        tK.Label(tab2, text="Station Called: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        calledBox = tK.Entry(tab2, width=30)
        calledBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Original VHF Channel: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.3, anchor="e")
        origChannelBox = tK.Entry(tab2, width=30)
        origChannelBox.place(relx=0.51, rely=0.3, anchor="w")
        tK.Label(tab2, text="Secondary VHF Channnel: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        secChannelBox = tK.Entry(tab2, width=30)
        secChannelBox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Radio Operator Staff ID: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.4, anchor="e")
        opSIDBox = tK.Entry(tab2, width=30)
        opSIDBox.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(tab2, text="Conversation Details (Max. 3000 Characters): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.5, rely=0.5, anchor="center")
        descBox = tK.Text(tab2, width=100, height=5)
        descBox.place(relx=0.5, rely=0.55, anchor="n")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newTransmissionBackend(dateandtimeBox.get(), callingBox.get(), calledBox.get(), origChannelBox.get(), secChannelBox.get(), opSIDBox.get(), descBox.get("1.0", 'end-1c')), width=30, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="center")

    def viewRadioTransmissionDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.radioLog(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        entryDict = self.tree.item(self.tree.selection())["values"]  # retrieve values relating to the row picked from the list
        dateAndTime = datetime.datetime.strptime(self.tree.item(self.tree.selection())["text"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")  # retrieve row #0 from tree
        statement = "SELECT DateAndTime, StationCalling, StationCalled, OriginalVHFChannel, SecondaryVHFChannel, ConversationDetails, RadioOpStaffID, firstName, Surname FROM radiolog JOIN users ON radiolog.RadioOpStaffID = users.StaffID WHERE DateAndTime = '%s'" % dateAndTime
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Radio Communication Details", font=("Calibri bold", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        tK.Label(self.root, text=resultTup[0][0].strftime("%A %d %B %Y %H:%M"), font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Station Calling: " + str(resultTup[0][1]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="Station Called: " + resultTup[0][2], font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.35, anchor="center")
        tK.Label(self.root, text="Original VHF Channel: " + str(resultTup[0][3]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="Secondary VHF Channel: " + str(resultTup[0][4]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.45, anchor="center")
        tK.Label(self.root, text="Radio Operator Staff ID: " + str(resultTup[0][6]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.55, anchor="center")
        tK.Label(self.root, text="Radio Operator Name: "+ resultTup[0][7] + " " + str(resultTup[0][8]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.6, anchor="center")
        tK.Label(self.root, text="Conversation Details:\n\n" + str(resultTup[0][5]), justify="center", wraplength=800, font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.7, anchor="center")

    def newTransmissionBackend(self, dateAndTime, calling, called, origChannel, secChannel, opSID, desc):
        try:
            dateAndTime = datetime.datetime.strptime(dateAndTime, "%Y-%m-%d %H:%M")
        except Exception:
            self.radioLog(1)
            return
        if not opSID.isdecimal():
            self.radioLog(1)
            return
        if len(calling) == 0 or len(called) == 0 or len(origChannel) == 0 or len(opSID) == 0:
            self.radioLog(1)
            return
        if len(desc) < 10:
            self.radioLog(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s';" % (opSID)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.radioLog(1)
            return
        statement2 = """INSERT INTO radiolog 
        (DateAndTime, StationCalling, StationCalled, OriginalVHFChannel, SecondaryVHFChannel, ConversationDetails, RadioOpStaffID)
        VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s');
        """ % (dateAndTime, calling, called, origChannel, secChannel, desc, opSID)
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.radioLog(0)
        return

    def fuelLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabStyle.configure('TNotebook', tabposition='n')
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Fuel Bunkering Logs")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Bunkering Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.864, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('loc', 'lit', 'cost', 'tank', 'ftype', 'sid')
        self.tree.column("#0", width=200, minwidth=200, stretch="no")
        self.tree.column("loc", width=150, minwidth=150, stretch="no")
        self.tree.column("lit", width=150, minwidth=150, stretch="no")
        self.tree.column("cost", width=150, minwidth=150, stretch="no")
        self.tree.column("tank", width=150, minwidth=150, stretch="no")
        self.tree.column("ftype", width=100, minwidth=100, stretch="no")
        self.tree.column("sid", width=100, minwidth=100, stretch="no")
        self.tree.heading('#0', text="Date and Time", anchor="w")
        self.tree.heading('loc', text="Location", anchor="w")
        self.tree.heading('lit', text="Litres Received", anchor="w")
        self.tree.heading('cost', text="Total Cost GBP", anchor="w")
        self.tree.heading('tank', text="Tank Name", anchor="w")
        self.tree.heading('ftype', text="Fuel Type", anchor="w")
        self.tree.heading('sid', text="Staff ID", anchor="w")
        statement = "SELECT DateAndTime, location, litresReceived, TotalCostOfFuelGBP, TankName, FuelType, StaffID from bunkeringlog;"
        resultTup = self.dbConnection(statement)

        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y %H:%M:%S")  # reformat each date value into UK common style (DD/MM/YYYY)
            self.tree.insert("", index="end", iid=each, text=eachDate, values=(resultTup[each][1], resultTup[each][2], resultTup[each][3], resultTup[each][4], resultTup[each][5], resultTup[each][6]))  # insert each row into tree
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure value entries are in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.9, anchor="center")

        tK.Label(tab2, text="New Fuel Bunkering Entry", font=("Calibri bold", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="Date and Time (YYYY-MM-DD HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.15, anchor="e")
        dateandtimeBox = tK.Entry(tab2, width=30)
        dateandtimeBox.place(relx=0.51, rely=0.15, anchor="w")
        tK.Label(tab2, text="Location: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        locBox = tK.Entry(tab2, width=30)
        locBox.place(relx=0.51, rely=0.2, anchor="w")
        tK.Label(tab2, text="Litres Received: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        litBox = tK.Entry(tab2, width=30)
        litBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Total cost of fuel (GBP): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.3, anchor="e")
        costBox = tK.Entry(tab2, width=30)
        costBox.place(relx=0.51, rely=0.3, anchor="w")
        tK.Label(tab2, text="Tank Name: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        tankBox = tK.Entry(tab2, width=30)
        tankBox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Fuel Type: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.4, anchor="e")
        ftypeBox = tK.Entry(tab2, width=30)
        ftypeBox.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(tab2, text="Staff ID: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.5, anchor="e")
        sidBox = tK.Entry(tab2, width=30)
        sidBox.place(relx=0.51, rely=0.5, anchor="w")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newFuelBackend(dateandtimeBox.get(), locBox.get(), litBox.get(), costBox.get(), tankBox.get(), ftypeBox.get(), sidBox.get()), width=30, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="center")

    def newFuelBackend(self, dateAndTime, loc, lit, cost, tank, ftype, sid):
        try:
            dateAndTime = datetime.datetime.strptime(dateAndTime, "%Y-%m-%d %H:%M")
        except Exception:
            self.fuelLog(1)
            return
        if len(loc) == 0 or len(lit) == 0 or len(cost) == 0 or len(tank) == 0 or len(ftype) == 0 or len(sid) == 0:
            self.fuelLog(1)
            return
        if not sid.isdecimal():
            self.fuelLog(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s';" % (sid)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.fuelLog(1)
            return
        statement2 = """INSERT INTO bunkeringlog 
        (DateAndTime, Location, LitresReceived, TotalCostOfFuelGBP, TankName, FuelType, StaffID)
        VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s');
        """ % (dateAndTime, loc, lit, cost, tank, ftype, sid)
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.fuelLog(0)
        return

    def maintenanceLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabStyle.configure('TNotebook', tabposition='n')
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Radio Communication Logs")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Radio Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.8042, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('mn', 'po')
        self.tree.column("#0", width=200, minwidth=200, stretch="no")
        self.tree.column("mn", width=325, minwidth=325, stretch="no")
        self.tree.column("po", width=325, minwidth=325, stretch="no")
        self.tree.heading('#0', text="Date and Time", anchor="w")
        self.tree.heading('mn', text="Maintenance Name", anchor="w")
        self.tree.heading('po', text="Performed On", anchor="w")
        statement = "SELECT DateAndTime, MaintenanceName, PerformedOn FROM maintenancelog;"
        resultTup = self.dbConnection(statement)

        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y %H:%M:%S")  # reformat each date value into UK common style (DD/MM/YYYY)
            self.tree.insert("", index="end", iid=each, text=eachDate, values=(resultTup[each][1], resultTup[each][2]))  # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0")  # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewMaintenanceDetails)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure date, time and Staff ID entries are in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.9, anchor="center")

        tK.Label(tab2, text="New Maintenance Log Entry", font=("Calibri bold", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="Date and Time (YYYY-MM-DD HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.15, anchor="e")
        dateandtimeBox = tK.Entry(tab2, width=30)
        dateandtimeBox.place(relx=0.51, rely=0.15, anchor="w")
        tK.Label(tab2, text="Maintnance Name: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        mNameBox = tK.Entry(tab2, width=30)
        mNameBox.place(relx=0.51, rely=0.2, anchor="w")
        tK.Label(tab2, text="Machinery Performed On: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        perfOnBox = tK.Entry(tab2, width=30)
        perfOnBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Main Engine Hours: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.3, anchor="e")
        engineHBox = tK.Entry(tab2, width=30)
        engineHBox.place(relx=0.51, rely=0.3, anchor="w")
        tK.Label(tab2, text="Maintenance Performed By (External Personnel): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        perfByBox = tK.Entry(tab2, width=30)
        perfByBox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Master Staff ID: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.4, anchor="e")
        msidBox = tK.Entry(tab2, width=30)
        msidBox.place(relx=0.51, rely=0.4, anchor="w")
        tK.Label(tab2, text="Maintenance Details (Max. 3000 Characters): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.5, rely=0.5, anchor="center")
        descBox = tK.Text(tab2, width=100, height=5)
        descBox.place(relx=0.5, rely=0.55, anchor="n")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newMaintenanceBackend(dateandtimeBox.get(), mNameBox.get(), perfOnBox.get(), engineHBox.get(), perfByBox.get(), msidBox.get(), descBox.get("1.0", 'end-1c')), width=30, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="center")

    def newMaintenanceBackend(self, dateAndTime, mName, perfOn, engineH, perfBy, msid, desc):
        try:
            dateAndTime = datetime.datetime.strptime(dateAndTime, "%Y-%m-%d %H:%M")
        except Exception:
            self.maintenanceLog(1)
            return
        if len(mName) == 0 or len(perfOn) == 0 or len(engineH) == 0:
            self.maintenanceLog(1)
            return
        if not msid.isdecimal():
            self.maintenanceLog(1)
            return
        if not engineH.isdecimal():
            self.maintenanceLog(1)
            return
        if len(desc) < 10:
            self.maintenanceLog(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s' AND Supervisor = 1;" % (msid)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.maintenanceLog(1)
            return
        statement2 = """INSERT INTO maintenanceLog 
        (DateAndTime, MaintenanceName, PerformedOn, MainEngineHours, MaintenancePerformedBy, MasterStaffID, MaintenanceDetails)
        VALUES
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s');
        """ % (dateAndTime, mName, perfOn, engineH, perfBy, msid, desc)
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.maintenanceLog(0)
        return

    def viewMaintenanceDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.maintenanceLog(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        entryDict = self.tree.item(self.tree.selection())["values"]  # retrieve values relating to the row picked from the list
        dateAndTime = datetime.datetime.strptime(self.tree.item(self.tree.selection())["text"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")  # retrieve row #0 from tree
        statement = "SELECT DateAndTime, MaintenanceName, PerformedOn, MainEngineHours, MaintenanceDetails, MaintenancePerformedBy, MasterStaffID, FirstName, Surname FROM maintenanceLog JOIN users ON maintenanceLog.MasterStaffID = users.StaffID WHERE DateAndTime = '%s'" % dateAndTime
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Maintenance Details", font=("Calibri bold", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        titleText = resultTup[0][1] + " - " + resultTup[0][0].strftime("%A %d %B %Y")
        tK.Label(self.root, text=titleText, font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Performed On: "+str(resultTup[0][2]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.3, anchor="center")
        tK.Label(self.root, text="Maintenance Performed By: "+resultTup[0][5], font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="Master Staff ID: "+str(resultTup[0][6]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.45, anchor="center")
        tK.Label(self.root, text="Master Name: "+resultTup[0][7]+" "+resultTup[0][8], font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.5, anchor="center")
        tK.Label(self.root, text="Main Engine Hours: "+str(resultTup[0][3]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.6, anchor="center")
        tK.Label(self.root, text="Maintenance Details:\n\n"+str(resultTup[0][4]), justify="center", wraplength=800, font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.8, anchor="center")

    def miscLog(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.logMenu(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabStyle.configure('TNotebook', tabposition='n')
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Previous Miscellaneous Logs")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Miscellaneous Log Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.6845, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('en')
        self.tree.column("#0", width=200, minwidth=200, stretch="no")
        self.tree.column("en", width=325, minwidth=325, stretch="no")
        self.tree.heading('#0', text="Date and Time", anchor="w")
        self.tree.heading('en', text="Entry name", anchor="w")
        statement = "SELECT DateAndTime, entryName FROM misclog;"
        resultTup = self.dbConnection(statement)

        for each in range(0, len(resultTup)):
            eachDate = resultTup[each][0].strftime("%d/%m/%Y %H:%M:%S")  # reformat each date value into UK common style (DD/MM/YYYY)
            self.tree.insert("", index="end", iid=each, text=eachDate, values=(resultTup[each][1]))  # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0")  # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewMiscEntryDetails)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure all fields are filled and in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.9, anchor="center")

        tK.Label(tab2, text="New Miscellaneous Log Entry", font=("Calibri bold", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="Date and Time (YYYY-MM-DD HH:MM):", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        dateandtimeBox = tK.Entry(tab2, width=30)
        dateandtimeBox.place(relx=0.51, rely=0.2, anchor="w")
        tK.Label(tab2, text="Entry Name: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.25, anchor="e")
        eNameBox = tK.Entry(tab2, width=30)
        eNameBox.place(relx=0.51, rely=0.25, anchor="w")
        tK.Label(tab2, text="Master Staff ID: ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.49, rely=0.35, anchor="e")
        msidBox = tK.Entry(tab2, width=30)
        msidBox.place(relx=0.51, rely=0.35, anchor="w")
        tK.Label(tab2, text="Entry Details/Notes (Max. 3000 Characters): ", font=("Calibri", 16), fg="white", bg="#729796").place(relx=0.5, rely=0.5, anchor="center")
        descBox = tK.Text(tab2, width=100, height=5)
        descBox.place(relx=0.5, rely=0.55, anchor="n")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newMiscEntryBackend(dateandtimeBox.get(), eNameBox.get(), msidBox.get(), descBox.get("1.0", 'end-1c')), width=30, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="center")
    
    def newMiscEntryBackend(self, dateAndTime, eName, msid, desc):
        try:
            dateAndTime = datetime.datetime.strptime(dateAndTime, "%Y-%m-%d %H:%M")
        except Exception:
            self.miscLog(1)
            return
        if len(eName) == 0 or len(msid) == 0 or len(desc) == 0:
            self.miscLog(1)
            return
        if not msid.isdecimal():
            self.miscLog(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s' AND Supervisor = 1;" % (msid)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.miscLog(1)
            return
        statement2 = """INSERT INTO miscLog 
        (DateAndTime, entryName, MasterID, notes)
        VALUES
        ('%s', '%s', '%s', '%s');
        """ % (dateAndTime, eName, msid, desc)
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.miscLog(0)
        return     

    def viewMiscEntryDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.miscLog(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        entryDict = self.tree.item(self.tree.selection())["values"]  # retrieve values relating to the row picked from the list
        dateAndTime = datetime.datetime.strptime(self.tree.item(self.tree.selection())["text"], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")  # retrieve row #0 from tree
        statement = "SELECT DateAndTime, entryName, MasterID, notes, FirstName, Surname FROM misclog JOIN users ON misclog.MasterID = users.StaffID WHERE DateAndTime = '%s'" % dateAndTime
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Miscellaneous Log Entry Details", font=("Calibri bold", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        titleText = resultTup[0][1] + " - " + resultTup[0][0].strftime("%A %d %B %Y")
        tK.Label(self.root, text=titleText, font=("Calibri bold", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.25, anchor="center")
        tK.Label(self.root, text="Master Staff ID: "+str(resultTup[0][2]), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        tK.Label(self.root, text="Master Name: "+resultTup[0][4]+" "+resultTup[0][5], font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.45, anchor="center")
        tK.Label(self.root, text="Entry Details:\n\n"+str(resultTup[0][3]), justify="center", wraplength=800, font=("Calibri", 16), fg="white", bg="#114F69").place(relx=0.5, rely=0.7, anchor="center")

class EmergencyScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID

    def checkPrivileges(self):
        statement = "SELECT * FROM users WHERE StaffID = %s AND Supervisor = 1;" % self.staffID
        resultTup = self.dbConnection(statement)
        if len(resultTup) != 0:
            self.supervisor = True
            self.mainMenu()
        else:
            self.supervisor = False
            self.mainMenu()

    def goHome(self):
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen

    def mainMenu(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        procBut = tK.Button(self.root, text="Emergency Procedures", command=lambda: self.emergencyProc(), font=("Calibri", 20), width=30, height=3)
        procBut.place(relx=0.25, rely=0.5, anchor="center")
        radioBut = tK.Button(self.root, text="VHF Radio Procedures", command=lambda: self.vhf(), font=("Calibri", 20), width=30, height=3)
        radioBut.place(relx=0.5, rely=0.5, anchor="center")
        medicalBut = tK.Button(self.root, text="Medical Procedures", command=lambda: self.medical(), font=("Calibri", 20), width=30, height=3)
        medicalBut.place(relx=0.75, rely=0.5, anchor="center")

    def emergencyProc(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.checkPrivileges(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        fireBut = tK.Button(self.root, text="Fire", command=lambda: self.showProcedure("Fire"), font=("Calibri", 20), width=20, height=2)
        fireBut.place(relx=0.2, rely=0.4, anchor="center")
        collBut = tK.Button(self.root, text="Collision", command=lambda: self.showProcedure("Collision"), font=("Calibri", 20), width=20, height=2)
        collBut.place(relx=0.4, rely=0.4, anchor="center")
        sinkBut = tK.Button(self.root, text="Sinking", command=lambda: self.showProcedure("Sinking"), font=("Calibri", 20), width=20, height=2)
        sinkBut.place(relx=0.6, rely=0.4, anchor="center")
        groundBut = tK.Button(self.root, text="Grounding", command=lambda: self.showProcedure("Grounding"), font=("Calibri", 20), width=20, height=2)
        groundBut.place(relx=0.8, rely=0.4, anchor="center")
        abandonBut = tK.Button(self.root, text="Abandon Ship", command=lambda: self.showProcedure("Abandon Ship"), font=("Calibri", 20), width=20, height=2)
        abandonBut.place(relx=0.2, rely=0.6, anchor="center")
        mobBut = tK.Button(self.root, text="Man Overboard (MOB)", command=lambda: self.showProcedure("Man Overboard"), font=("Calibri", 20), width=20, height=2)
        mobBut.place(relx=0.4, rely=0.6, anchor="center")
        floodBut = tK.Button(self.root, text="Flooding", command=lambda: self.showProcedure("Flood"), font=("Calibri", 20), width=20, height=2)
        floodBut.place(relx=0.6, rely=0.6, anchor="center")
        pollBut = tK.Button(self.root, text="Pollution", command=lambda: self.showProcedure("Pollution"), font=("Calibri", 20), width=20, height=2)
        pollBut.place(relx=0.8, rely=0.6, anchor="center")

    def showProcedure(self, emergencyType):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.emergencyProc(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        statement = "SELECT ProcedureInfo FROM emergencyprocedures WHERE EmergencyType = '%s'" % (emergencyType)
        result = self.dbConnection(statement)[0]
        if len(result[0]) >= 140:
            detailsWrapped = "\n".join(textwrap.wrap(result[0], 140)) # wrap text at 140 characters
        else:
            detailsWrapped = result[0]
        tK.Label(self.root, text=emergencyType, font=("Calibri bold", 26), fg="white", bg="#114F69").place(relx=0.5, rely=0.2, anchor="center")
        tK.Label(self.root, text=detailsWrapped, font=("Calibri", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.5, anchor="center")
        if self.supervisor == True:
            changeBut = tK.Button(self.root, text="Change Procedure", command=lambda: self.changeProcedure(emergencyType, result[0]), width=30, height=2)
            changeBut.place(relx=0.5, rely=0.8, anchor="center")

    def changeProcedure(self, emergencyType, desc):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.showProcedure(emergencyType), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05,anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tK.Label(self.root, text="Change Procedure Details - "+emergencyType, font=("Calibri bold", 26), fg="white", bg="#114F69").place(relx=0.5, rely=0.2, anchor="center")
        descriptionBox = tK.Text(self.root, width=100, wrap=tK.WORD)
        descriptionBox.insert(tK.END, desc)
        descriptionBox.place(relx=0.5, rely=0.4, anchor="center", height=300)
        subBut = tK.Button(self.root, text="Submit", command=lambda: self.changeProcedureBackend(emergencyType, descriptionBox.get("1.0",'end-1c')), width=40, height=3)
        subBut.place(relx=0.5, rely=0.7, anchor="center")

    def changeProcedureBackend(self, name, notes):
        statement = "UPDATE emergencyProcedures SET ProcedureInfo = '%s' WHERE EmergencyType = '%s';" % (notes, name)
        self.dbConnection(statement)
        self.forgetAllWidgets()
        self.mainMenu()
        return

    def vhf(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.mainMenu(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        style = tK.ttk.Style(self.root)
        currentTheme = style.theme_use()
        style.configure('TNotebook', tabposition='wn')
        style.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [50, 30]}}})
        style.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"font": ("Calibri", 18)}}})
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.52, anchor="center")
        tab1 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab2 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab3 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab4 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab5 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab6 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)
        tab7 = tK.Frame(tabHolder, bg='#729796', width=1000, height=self.root.winfo_height() - 150)

        tabHolder.add(tab1, text='                    MAYDAY                    ')
        tabHolder.add(tab2, text='        PAN PAN / SECURITÉ        ')
        tabHolder.add(tab3, text='                        DSC                        ')
        tabHolder.add(tab4, text='    10 Rules of Transmission    ')
        tabHolder.add(tab5, text='         Speaking Procedure         ')
        tabHolder.add(tab6, text='   Frequently Used Channels   ')
        tabHolder.add(tab7, text='          Phonetic Alphabet          ')
        tK.Label(tab1, text="MAYDAY Distress Call", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab2, text="PAN PAN / SECURITÉ", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab3, text="Digital Selective Calling (DSC)", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab4, text="10 Rules of Transmission", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab5, text="Speaking Procedure", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab6, text="Frequently Used Channels", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab7, text="Phonetic Alphabet", font=("Calibri bold", 24), fg="white", bg="#729796").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(tab1, text="""
        A MAYDAY call should only be made where a vessel, vehicle, aircraft or 
        person is in grave and imminent danger.
         
        Ensure the VHF set is on Channel 16 and on high power.
        When making a MAYDAY call remember MIPDANIO.
        
        M - MAYDAY x3
        I - Identification: Vessel Name, MMSI, Callsign
        P - Position: GPS Latitude and Longitude, or distance and bearing from a charted landmark.
        D - Distress: Nature of distress e.g. fire, sinking, flooding
        A - Assistance Required: Request a tow, helicopter evacuation, or immediate assistance. 
        N - Number: Number of passengers and crew on board
        I - Information: e.g. 'Abandoning into liferafts', or '15 metre blue passenger boat'. 
        O - Over
        """, font=("Calibri", 18), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.15, anchor="nw")
        tK.Label(tab2, text="""
        PAN PAN is the call for an urgency situation, like for medical assistance or loss of steering.
        
        Pan Pan x3.
        All Stations / ___ Coastguard x3
        This is (Vessel Name) x3
        Call Sign
        MMSI
        Position
        Nature of Distress
        Assistance Required
        (Number of persons on board)
        Extra Information (e.g. 15 metre blue passenger vessel)
        Over
        
        SECURITÉ announcements are usually made by the Coatguard and give non 
        urgent or emergency information, such as weather or gale warnings in
        specific areas, or unexpected navigational hazards.
        
        Securité x3
        All Ships x3
        This is (Vessel Name / Coastguard)
        Information
        Out
        """, font=("Calibri", 18), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.15, anchor="nw")
        tK.Label(tab3, text="""
        DSC functionality is built-in to most new fixed VHF sets and allows the user to press 
        the DISTRESS button on the set which sends a distress signal to all stations,
        automatically sending your location, vessel identity, and nature of distress which is
        selectable. It is also possible to send an urgency or safety call to all stations or
        an individual station.
        
        To activate:
        
        Press red DISTRESS button on fixed VHF set 
        (If this button is held, it will send a generic distress signal)
        Input nature of distress
        Hold DISTRESS button for 5 seconds.
        
        The MMSI, Location and Nature of distress has now been sent to all stations and should be 
        followed by a distress voice call on channel 16.        
        """, font=("Calibri", 18), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.15, anchor="nw")
        tK.Label(tab4, text="""
        There are 10 rules of transmitting over VHF which must be followed.
        
        1. Do not transmit without the authority of the master of the vessel.
        2. Do not transmit false or deceptive distress or safety signals.
        3. Do not transmit without identification (vessel name or call sign)
        4. Do not shut down a radio telephone before finishing all operations resulting from a 
            distress, urgency, or safety call.
        5. Do not broadcast to everyone other than distress messages
        6. Do not transmit music
        7. Do not make unneccesary transmissions (not to do with ship's business)
        8. Do not transmit profane, indecent or obscene language.
        9. Do not use unauthorised frequencies
        10. Do not transmit messages intended to be received ashore, other than by a licensed
            coast radio station.
        """, font=("Calibri", 18), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.15, anchor="nw")
        tK.Label(tab5, text="""
        - Listen before transmitting
        - Plan what you are going to say
        - Use the microphone correctly
        - Speak normally and clearly
        
        - Example
        
        Bristol Marina x3
        This is (MY Example) x3
        On channel 16
        over
        
        After reply / acknowlegement, should switch to a working channel.
        """, font=("Calibri", 18), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.15, anchor="nw")
        tK.Label(tab6, text="""
        00 - UK SAR - DO NOT USE
        01-05 - Public Correspondence and Port Operations
        06 - Primary Ship To Ship Channel
        07 - Public Correspondence and Port Operations
        08 - Ship To Ship
        09 - Ship To Ship - Frequently Used By Pilots
        10 - Ship To Ship / Port Operations
        11/12 - Port Operations
        13 - GMDSS Bridge-To-Bridge
        14 - Port Operations - Frequently Used By Marinas
        15 - On Board Working - 1 Watt
        16 - International Distress, Urgency, Safety and Calling
        17 - On Board Working - 1 Watt
        18-22 - Port Operations
        23 - Public Correspondence and UKCG Medilink
        24-28 - Public Correspondence
        31 - RNLI Launch, Recovery and Training - DO NOT USE
        37A/M1 - Private Channel Used By Yacht Clubs, Marinas etc.
        60/61 - Public Correspondence and Port Operations
        62-64 - HMCG Maritime Safety Information
        65 - National Coastwatch Institution
        66 - Public Correspondence and Port Operations
        67 - UKCG - UK Small Ship Safety Channel
        68 - Port Operations
        69 - Ship To Ship and Port Operations
               
        """, font=("Calibri", 14), justify="left", fg="white", bg="#729796").place(relx=0.001, rely=0.12, anchor="nw")

        tK.Label(tab6, text="""
        70 - DSC - NO VOICE
        71 - Port Operations
        72 - Ship To Ship
        73 - UKCG - UK Small Ship Safety Channel
        74 - Port Operations
        77 - Ship To Ship
        78 - Public Correspondence and Port Operations
        79 - Port Operations
        80 - UK Marina Channel
        81/82 - Public Correspondence and Port Operations
        83 - Public Correspondence
        84 - Public Correspondence and Port Operations
        85 - Public Correspondence / UKSAR
        86 - Public Correspondence and UKCG Medilink
        87/88 - AIS / SART - DO NOT USE     
        """, font=("Calibri", 14), justify="left", fg="white", bg="#729796").place(relx=0.52, rely=0.12, anchor="nw")

        tK.Label(tab7, text="""
        LETTER
        A
        B
        C
        D
        E
        F
        G
        H
        I
        J
        K
        L
        M
        N
        O
        P
        Q
        R
        S
        T
        U
        V
        W
        X
        Y
        Z
        """, font=("Calibri", 16), justify="left", fg="white", bg="#729796").place(relx=0.1, rely=0.12, anchor="nw")
        tK.Label(tab7, text=""" 
        MORSE CODE
        *-
        -***
        -*-*
        -**
        * 
        **-* 
        --* 
        **** 
        ** 
        *--- 
        -*- 
        *-** 
        -- 
        -* 
        --- 
        *--* 
        --*- 
        *-* 
        *** 
        - 
        **- 
        ***- 
        *-- 
        -**- 
        -*-- 
        --** 
        """, font=("Calibri", 16), justify="left", fg="white", bg="#729796").place(relx=0.3, rely=0.12, anchor="nw")
        tK.Label(tab7, text=""" 
        CODE WORD
        Alfa
        Bravo
        Charlie
        Delta
        Echo
        Foxtrot
        Gold
        Hotel
        India
        Juiliett
        Kilo
        Lima
        Mike
        November
        Oscar
        Papa
        Quebec
        Romeo
        Sierra
        Tango
        Uniform
        Victor
        Whiskey
        X-ray
        Yankee
        Zulu
        """, font=("Calibri", 16), justify="left", fg="white", bg="#729796").place(relx=0.5, rely=0.12, anchor="nw")

    def medical(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.mainMenu(), image=backImg,compound="left")  # logs button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text
        tK.Label(self.root, text="IN AN EMERGENCY ALWAYS CONTACT THE COASTGUARD ON VHF 16 OR DIAL 999", font=("Calibri bold", 24), fg="white", bg="red").place(relx=0.5, rely=0.1, anchor="center")
        tK.Label(self.root, text="""
        This is a short reference for basic aid and is not a substitute for a first aid course or medical training.
        
        The mnemonic DRS ABC may be useful to remember when finding a casualty.
        """, font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.2, anchor="center")
        tK.Label(self.root, text="""        D - Danger - Make sure you or the casualty aren't in any danger.
        R - Response - is the casualty responsive? shake and shout to check.
        S - Send for help - make sure to raise the alarm.
        
        A - Airway - make sure the casualty's airway is clear, tilt head and open mouth to check.
        B - Breathing - make sure the casualty is breathing, look, listen and feel for this.
        C - Circulation - look for significant bleeding
        """, font=("Calibri", 18), justify="left", fg="white", bg="#114F69").place(relx=0.5, rely=0.32, anchor="center")
        sep = tK.ttk.Separator(self.root, orient="horizontal").place(relx=0.5, rely=0.45, anchor="center", relwidth=1, relheight=0.003)
        tK.Label(self.root, text="CPR (From NHS Website)", font=("Calibri bold", 20), fg="white", bg="#114F69", justify="left").place(relx=0.5, rely=0.48, anchor="center")
        tK.Label(self.root, text="""Adults
        1. Place the heel of your hand on the centre of the person's chest, then place the other hand on top and press 
            down by 5 to 6cm (2 to 2.5 inches) at a steady rate of 100 to 120 compressions a minute.
        2. After every 30 chest compressions, give 2 rescue breaths.
        3. Tilt the casualty's head gently and lift the chin up with 2 fingers. Pinch the person's nose. 
            Seal your mouth over their mouth, and blow steadily and firmly into their mouth for about 1 second. 
            Check that their chest rises. Give 2 rescue breaths.
        4. Continue with cycles of 30 chest compressions and 2 rescue breaths until they begin to recover or 
            emergency help arrives.
        
Children over 1 year old
        1. Open the child's airway by placing 1 hand on their forehead and gently tilting their head back and lifting the chin.
            Remove any visible obstructions from the mouth and nose.
        2. Pinch their nose. Seal your mouth over their mouth, and blow steadily and firmly into their mouth, 
            checking that their chest rises. Give 5 initial rescue breaths.
        3. Place the heel of 1 hand on the centre of their chest and push down by 5cm (about 2 inches), which is approximately one-third 
            of the chest diameter. The quality (depth) of chest compressions is very important. 
            Use 2 hands if you can't achieve a depth of 5cm using 1 hand.
        4. After every 30 chest compressions at a rate of 100 to 120 a minute, give 2 breaths.
        5. Continue with cycles of 30 chest compressions and 2 rescue breaths until they begin to recover or emergency help arrives.       
        """, font=("Calibri", 14), fg="white", bg="#114F69", justify="left").place(relx=0.02, rely=0.5, anchor="nw")

        tK.Label(self.root, text="""Infants under 1 year old
        1. Open the infant's airway by placing 1 hand on their forehead and gently tilting the head back and lifting the chin. 
            Remove any visible obstructions from the mouth and nose.
        2. Place your mouth over the mouth and nose of the infant and blow steadily and firmly into their mouth, checking 
            that their chest rises. Give 5 initial rescue breaths.
        3. Place 2 fingers in the middle of the chest and push down by 4cm (about 1.5 inches), which is approximately 
            one-third of the chest diameter. The quality (depth) of chest compressions is very important. 
            Use the heel of 1 hand if you can't achieve a depth of 4cm using the tips of 2 fingers.
        4. After 30 chest compressions at a rate of 100 to 120 a minute, give 2 rescue breaths.
        5. Continue with cycles of 30 chest compressions and 2 rescue breaths until they begin to recover 
            or emergency help arrives.
        """, font=("Calibri", 14), fg="white", bg="#114F69", justify="left").place(relx=0.51, rely=0.5, anchor="nw")

class TideScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID
        self.resultFrame = tK.Frame(self.root, width=1200, height=500, bg="#729796")
        self.errorLabel = tK.Label(self.root, text="The tidal prediction service is currently unavailable please ensure you are connected to the internet and try again later.", font=("Calibri", 24), fg="white", bg="#114F69")
        self.locationName = tK.Label(self.root)
        self.forgetAllWidgets()
        self.commonStyles()

    def goHome(self):
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen
        return

    def apiConnect(self, userEntry):
        self.locationName.place_forget()
        f = open("tideAPIKeys.txt", "r")
        key = f.read()
        headers = {'Ocp-Apim-Subscription-Key': key}
        userLocation = {'name': userEntry}
        stationName = urllib.parse.urlencode(userLocation)
        try:
            if len(userEntry) < 3:
                raise Exception
            conn = http.client.HTTPSConnection('admiraltyapi.azure-api.net')
            conn.request("GET", "/uktidalapi/api/V1/Stations?%s" % stationName, "{body}", headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            stationID = data['features'][0]['properties']['Id']
            stationName = data['features'][0]['properties']['Name']
            conn.close()
        except OSError as e:
            if self.errorLabel.winfo_ismapped() == 0:
                self.errorLabel.place(relx=0.5, rely=0.35, anchor="center")

        except Exception as err:
            if self.errorLabel.winfo_ismapped() == 0:
                self.errorLabel = tK.Label(self.root, text="The location you have entered is unavailable. Please ensure it is spelled correctly.", font=("Calibri", 18), fg="white", bg="#114F69")
                self.errorLabel.place(relx=0.5, rely=0.35, anchor="center")

        try:
            predictionDuration = urllib.parse.urlencode({'duration': 7})
            conn.request("GET", "/uktidalapi/api/V1/Stations/%s/TidalEvents?%s" % (stationID, predictionDuration), "{body}", headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            conn.close()
            self.showTideResults(data, stationName)
        except Exception as err:
            if self.errorLabel.winfo_ismapped() == 0:
                self.errorLabel.place(relx=0.5, rely=0.35, anchor="center")

    def showLocationPicker(self):
        tK.Label(self.root, text="Tide Prediction Finder", font=("Calibri", 24), fg="white", bg="#114F69").place(relx=0.5, rely=0.16, anchor="center")
        tK.Label(self.root, text="UK Location:", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.466, rely=0.23, anchor="e")
        locationBox = tK.Entry(self.root, width=40)  # text box for user entry of location
        locationBox.place(relx=0.468, rely=0.23, anchor="w")
        submit = tK.Button(self.root, text="Go!", command=lambda: self.apiConnect(locationBox.get()), width=50)  # passes user input to apiConnect to retrieve weather
        submit.place(relx=0.5, rely=0.275, anchor="center")
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.goHome, image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

    def showTideResults(self, tideData, stationName):
        if self.errorLabel.winfo_ismapped():
            self.errorLabel.place_forget()
        relxCount = 0
        self.resultFrame.place(relx=0.5, rely=0.7, anchor="center")

        self.locationName = tK.Label(self.root, text=stationName, font=("Calibri", 16, "bold"), fg="white", bg="#114F69")
        self.locationName.place(relx=0.5, rely=0.36, anchor="center")

        tK.Label(self.root, text="Today", font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.24, rely=0.4, anchor="center")
        tK.Label(self.root, text=datetime.date.today().strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.24, rely=0.43, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=1)).strftime("%A"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.345, rely=0.4, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=1)).strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.345, rely=0.43, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=2)).strftime("%A"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.45, rely=0.4, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=2)).strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.45, rely=0.43, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=3)).strftime("%A"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.55, rely=0.4, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=3)).strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.55, rely=0.43, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=4)).strftime("%A"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.655, rely=0.4, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=4)).strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.655, rely=0.43, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=5)).strftime("%A"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.76, rely=0.4, anchor="center")
        tK.Label(self.root, text=(datetime.date.today() + datetime.timedelta(days=5)).strftime("%d/%m/%Y"), font=("Calibri 16"), fg="white", bg="#114F69").place(relx=0.76, rely=0.43, anchor="center")

        for each in range(0, 6):
            yCount = 10
            canvas = tK.Canvas(self.resultFrame, width=200, height=600, highlightthickness=1, bg="#B9CBCA")
            while len(tideData) > 0:
                if datetime.datetime.strptime(tideData[0]['DateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%d") == datetime.datetime.strptime(tideData[1]['DateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%d"):
                    canvas.create_text((100, yCount), text=datetime.datetime.strptime(tideData[0]['DateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M"), font=("Calibri 16"), justify="center", anchor="n", width=200)
                    tempText = tideData[0]['EventType'].split("Water")[0] + " Water: " + str(round(tideData[0]['Height'], 2)) + "M"
                    canvas.create_text((100, yCount + 25), text=tempText, font=("Calibri 16"), justify="center", anchor="n", width=200)
                    yCount += 80
                    tideData.pop(0)
                else:
                    canvas.create_text((100, yCount), text=datetime.datetime.strptime(tideData[0]['DateTime'], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M"), font=("Calibri 16"), justify="center", anchor="n", width=200)
                    tempText = tideData[0]['EventType'].split("Water")[0] + " Water: " + str(round(tideData[0]['Height'], 2)) + "M"
                    canvas.create_text((100, yCount + 25), text=tempText, font=("Calibri 16"), justify="center", anchor="n", width=200)
                    yCount += 80
                    tideData.pop(0)
                    break

            canvas.place(x=relxCount, y=0, anchor="nw")
            canvas.update()
            self.resultFrame.update()
            relxCount += 200

class CrewLookupScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID
        self.forgetAllWidgets()
        self.commonStyles()

    def goHome(self):
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen

    def checkPrivileges(self):
        statement = "SELECT * FROM users WHERE StaffID = %s AND Supervisor = 1;" % self.staffID
        resultTup = self.dbConnection(statement)
        if len(resultTup) != 0:
            self.supView()
        else:
            self.subView()

    def supView(self):
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.goHome, image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        supTree = tK.ttk.Treeview(self.root, height=20)
        treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        treeStyle.theme_use("default")  # use the default theme until some specifics are modified below
        treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        treeStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        scrollbar = tK.ttk.Scrollbar(self.root, command=supTree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.7225, rely=0.417, relheight=0.393, relwidth=0.010)  # set the position on screen and size relative to screen size
        supTree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        supTree['columns'] = ('fn', 'sn', 'pn', 'dob', 'nok', 'sup')
        supTree.column("#0", width=70, minwidth=70, stretch="no")
        supTree.column("fn", width=150, minwidth=150, stretch="no")
        supTree.column("sn", width=150, minwidth=150, stretch="no")
        supTree.column("pn", width=150, minwidth=150, stretch="no")
        supTree.column("dob", width=120, minwidth=120, stretch="no")
        supTree.column("nok", width=150, minwidth=150, stretch="no")
        supTree.column("sup", width=100, minwidth=100, stretch="no")
        supTree.heading('#0', text="Staff ID", anchor="w")
        supTree.heading('fn', text="First Name", anchor="w")
        supTree.heading('sn', text="Surname", anchor="w")
        supTree.heading('pn', text="Phone Number", anchor="w")
        supTree.heading('dob', text="Date of Birth", anchor="w")
        supTree.heading('nok', text="Next of Kin", anchor="w")
        supTree.heading('sup', text="Supervisor", anchor="w")
        statement = "SELECT staffID, firstName, surname, phoneNum, DOB, nokName, supervisor FROM users;"
        resultTup = self.dbConnection(statement)
        for each in range(0, len(resultTup)):
            if resultTup[each][6] == 1:
                supTree.insert("", index="end", iid=each, text=resultTup[each][0], values=(resultTup[each][1], resultTup[each][2], resultTup[each][3], resultTup[each][4], resultTup[each][5], "Yes"))
            else:
                supTree.insert("", index="end", iid=each, text=resultTup[each][0], values=(resultTup[each][1], resultTup[each][2], resultTup[each][3], resultTup[each][4], resultTup[each][5], "No"))

        supTree.place(relx=0.5, rely=0.6, anchor="center")

    def subView(self):
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=self.goHome, image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        supTree = tK.ttk.Treeview(self.root, height=20)
        treeStyle = tK.ttk.Style()  # a tkinter style object which can be applied to a widget
        treeStyle.theme_use("default")  # use the default theme until some specifics are modified below
        treeStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        treeStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        scrollbar = tK.ttk.Scrollbar(self.root, command=supTree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.6465, rely=0.417, relheight=0.393, relwidth=0.010)  # set the position on screen and size relative to screen size
        supTree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        supTree['columns'] = ('sn', 'pn')
        supTree.column("#0", width=200, minwidth=200, stretch="no")
        supTree.column("sn", width=200, minwidth=200, stretch="no")
        supTree.column("pn", width=200, minwidth=200, stretch="no")
        supTree.heading('#0', text="First Name", anchor="w")
        supTree.heading('sn', text="Surname", anchor="w")
        supTree.heading('pn', text="Phone Number", anchor="w")
        statement = "SELECT firstName, surname, phoneNum FROM users;"
        resultTup = self.dbConnection(statement)
        for each in range(0, len(resultTup)):
            supTree.insert("", index="end", iid=each, text=resultTup[each][0], values=(resultTup[each][1], resultTup[each][2]))
        supTree.place(relx=0.5, rely=0.6, anchor="center")

class ChecklistScreen(VesselManSys):
    def __init__(self, parent, staffID):
        self.root = parent
        self.staffID = staffID

    def goHome(self): # called from Back button on checklistHome()
        self.forgetAllWidgets() # clear the screen
        h = HomePage(self.root, self.staffID) # create home screen object
        h.homeScreen() # show home screen

    def checklistHome(self, errorCaught):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.goHome(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.configure('TNotebook', tabposition='n')
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Checklist Types")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Checklist Type")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.855, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree['columns'] = ('count')
        self.tree.column("#0", width=450, minwidth=450, stretch="no")
        self.tree.column("count", width=450, minwidth=450, stretch="no")
        self.tree.heading('#0', text="Checklist Type", anchor="w")
        self.tree.heading('count', text="Number of Completed Lists", anchor="w")
        statement = "SELECT ChecklistName, (SELECT COUNT(*) FROM completedchecklists WHERE completedchecklists.ChecklistType = checklisttypes.ChecklistName) AS 'CompletedNum' FROM checklisttypes;"
        resultTup = self.dbConnection(statement)
        for each in range(0, len(resultTup)):
            self.tree.insert("", index="end", iid=each, text=resultTup[each][0], values=(resultTup[each][1])) # insert each row into tree
        changeBut = tK.Button(tab1, text="Modify\nChecklist", command=lambda: self.modifyListType(), width=15, height=6)
        changeBut.place(relx=0.05, rely=0.5, anchor="center")
        if len(resultTup) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.tree.bind("<Double-1>", self.viewChecklists)  # bind a double-click event to the viewEntryDetails function
        self.tree.pack(side="top", pady=10)

        if errorCaught == 1:
            tabHolder.select(tab2)
            tK.Label(tab2, text="Please ensure Staff ID is in the correct format.", font=("Calibri", 16), fg="red", bg="white").place(relx=0.5, rely=0.85, anchor="center")

        tK.Label(tab2, text="New Checklist Type", font=("Calibri bold", 20), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        tK.Label(tab2, text="New Checklist Name:", font=("Calibri", 18), fg="white", bg="#729796").place(relx=0.49, rely=0.2, anchor="e")
        nameBox = tK.Entry(tab2, width=30)
        nameBox.place(relx=0.5, rely=0.2, anchor="w")
        tK.Label(tab2, text="Checklist Items Separated By Commas: \n(E.g. item 1, item 2, item 3 etc.)", font=("Calibri", 18), fg="white", bg="#729796").place(relx=0.5, rely=0.3, anchor="center")
        descBox = tK.Text(tab2, width=100, height=5)
        descBox.place(relx=0.5, rely=0.4, anchor="n")
        tK.Label(tab2, text="Staff ID:", font=("Calibri", 18), fg="white", bg="#729796").place(relx=0.45, rely=0.65, anchor="e")
        sidBox = tK.Entry(tab2, width=30)
        sidBox.place(relx=0.46, rely=0.65, anchor="w")
        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newChecklistBackend(nameBox.get(), descBox.get("1.0",'end-1c'), sidBox.get(), "new"), width=30, height=2)
        subBut.place(relx=0.5, rely=0.8, anchor="center")

    def modifyListType(self):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.checklistHome(), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tK.Label(self.root, text="Modify Checklist - "+self.tree.item(self.tree.selection())["text"], font=("Calibri", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.2, anchor="center")
        tK.Label(self.root, text="Checklist Name:", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.49, rely=0.3, anchor="e")
        nameBox = tK.Entry(self.root, width=30)
        nameBox.place(relx=0.5, rely=0.3, anchor="w")
        tK.Label(self.root, text="Checklist Items Separated By Commas: \n(E.g. item 1, item 2, item 3 etc.)", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.4, anchor="center")
        descBox = tK.Text(self.root, width=100, height=5)
        descBox.place(relx=0.5, rely=0.4, anchor="n")
        tK.Label(self.root, text="Staff ID:", font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.45, rely=0.75, anchor="e")
        sidBox = tK.Entry(self.root, width=30)
        sidBox.place(relx=0.46, rely=0.75, anchor="w")
        subBut = tK.Button(self.root, text="Submit", command=lambda: self.newChecklistBackend(nameBox.get(), descBox.get("1.0",'end-1c'), sidBox.get(), "change"), width=30, height=2)
        subBut.place(relx=0.5, rely=0.85, anchor="center")
        
    def newChecklistBackend(self, name, description, sid, mode): # mode = "change" or "new"
        if not sid.isdecimal():
            self.checklistHome(1)
            return
        if len(name) < 3:
            self.checklistHome(1)
            return
        if len(description) < 1:
            self.checklistHome(1)
            return
        statement1 = "SELECT StaffID from users WHERE StaffID = '%s';" % (sid)
        result1 = self.dbConnection(statement1)
        if len(result1) == 0:
            self.checklistHome(1)
            return
        if mode == "new":
            statement2 = """INSERT INTO checklisttypes 
            (ChecklistName, ComSepHeaders, StaffID)
            VALUES
            ('%s', '%s', '%s');
            """ % (name, description, sid)
        elif mode == "change":
            statement2 = """UPDATE checklisttypes SET ChecklistName = '%s', ComSepHeaders = '%s', StaffID = '%s' 
            WHERE ChecklistName = '%s';""" % (name, description, sid, self.tree.item(self.tree.selection())["text"])
        self.dbConnection(statement2)
        self.forgetAllWidgets()
        self.commonStyles()
        self.checklistHome(0)
        return

    def viewChecklists(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.checklistHome(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        tabStyle = tK.ttk.Style()
        currentTheme = tabStyle.theme_use()
        tabStyle.configure("Treeview.Heading", background="orange", font=("Calibri", 15), foreground="black")  # this is the heading fields for the list
        tabStyle.configure("Treeview", font=("Calibri", 12))  # the entry fields for the list
        tabStyle.configure('TNotebook', tabposition='n')
        tabStyle.theme_settings(currentTheme, {"TNotebook.Tab": {"configure": {"padding": [250, 30]}}})
        tabHolder = tK.ttk.Notebook(self.root)
        tabHolder.place(relx=0.5, rely=0.2, anchor="n")
        tab1 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab1, text="View Checklists")
        tab2 = tK.Frame(tabHolder, width=1000, height=self.root.winfo_height() - 450, bg="#729796")
        tabHolder.add(tab2, text="New Checklist Entry")
        tabHolder.select(tab1)
        tabHolder.enable_traversal()
        clType = self.tree.item(self.tree.selection())["text"]  # retrieve values relating to the row picked from the list
        self.tree.delete(*self.tree.get_children()) # clear everything in the original tree
        self.tree = tK.ttk.Treeview(tab1, height=25)
        scrollbar = tK.ttk.Scrollbar(tab1, command=self.tree.yview, orient="vertical")  # vertical scrollbar for the list box
        scrollbar.place(relx=0.6965, rely=0.021, relheight=0.925, relwidth=0.010)  # set the position on screen and size relative to screen size
        self.tree.configure(yscrollcommand=scrollbar.set)  # relate the created scrollbar to the list
        self.tree.column("#0", width=500, minwidth=500, stretch="no", anchor="center")
        self.tree.heading('#0', text="Completed Date / Time (Double Click for Details)", anchor="w")
        statement = "SELECT DateAndTime FROM completedChecklists WHERE ChecklistType = '%s';" % (clType)
        resultTup = self.dbConnection(statement)
        for each in range(0, len(resultTup)):
            self.tree.insert("", index="end", iid=each, text=resultTup[each][0]) # insert each row into tree
        if len(resultTup) > 0:
            self.tree.selection_set("0") # highlight the first result if exists
        self.root.unbind_all("<Double-1>")
        self.tree.bind("<Double-1>", self.viewChecklistDetails)  # bind a double-click event to the viewchecklistdetails function
        self.tree.pack(side="top", pady=10)

        tK.Label(tab2, text="New Checklist Entry", font=("Calibri bold", 20), fg="white", bg="#729796").place(relx=0.5, rely=0.07, anchor="center")
        statement = "SELECT ComSepHeaders FROM checklisttypes WHERE ChecklistName = '%s';" % (clType)
        resultTup = self.dbConnection(statement)
        headings = resultTup[0][0].split(",")
        yCount = 0.25
        xboxArr = []
        for each in range(0, len(headings)):
            tK.Label(tab2, text=headings[each]+" : ", font=("Calibri", 15), fg="white", bg="#729796").place(relx=0.5, rely=yCount, anchor="e")
            xboxArr.append(tK.IntVar())
            supButton = tK.Checkbutton(tab2, variable=xboxArr[each], bg="#729796", activebackground="#729796")
            supButton.place(relx=0.51, rely=yCount, anchor="w")
            yCount += 0.05

        subBut = tK.Button(tab2, text="Submit", command=lambda: self.newEntryBackend(xboxArr, clType), width=30, height=2)
        subBut.place(relx=0.5, rely=0.9, anchor="center")

    def newEntryBackend(self, xboxArr, clType):
        for each in range(0, len(xboxArr)):
            xboxArr[each] = str(xboxArr[each].get())
        xboxArr = ",".join(xboxArr)
        statement = "INSERT INTO completedchecklists (ChecklistType, CSBoolArray) VALUES ('%s', '%s');" % (clType, xboxArr)
        self.dbConnection(statement)
        self.forgetAllWidgets()
        self.checklistHome(0)
        return

    def viewChecklistDetails(self, *args):
        self.forgetAllWidgets()
        self.commonStyles()
        backImg = tK.PhotoImage(file="ImageResources/back.png")  # opens image
        backImg = backImg.subsample(8, 8)  # changes image size
        backBut = tK.Button(self.root, text="  Back", command=lambda: self.checklistHome(0), image=backImg, compound="left")  # back button - compound = justify the image
        backBut.photo = backImg  # must store the variable as a property of the button
        backBut.place(relx=0.05, rely=0.05, anchor="center")  # relative x and y location from the centre, anchor is for justifying text

        entryDict = self.tree.item(self.tree.selection())["text"] # retrieve values relating to the row picked from the list
        statement = "SELECT * FROM completedchecklists JOIN checklisttypes ON completedchecklists.ChecklistType = checklisttypes.ChecklistName WHERE DateAndTime = '%s';" % (entryDict)
        resultTup = self.dbConnection(statement)
        tK.Label(self.root, text="Log Entry Details", font=("Calibri bold", 20), fg="white", bg="#114F69").place(relx=0.5, rely=0.15, anchor="center")
        print(resultTup)
        tK.Label(self.root, text=resultTup[0][1]+" - "+resultTup[0][0].strftime("%d/%m/%Y %H:%M:%S"), font=("Calibri", 18), fg="white", bg="#114F69").place(relx=0.5, rely=0.2, anchor="center")

        headings = resultTup[0][4].split(",")
        boolValues = resultTup[0][2].split(",")
        for x in range(0, len(boolValues)):
            if boolValues[x] == "1":
                boolValues[x] = "True"
            else:
                boolValues[x] = "False"
        yCount = 0.25
        for each in range(0, len(headings)):
            tK.Label(self.root, text=headings[each]+" : "+boolValues[each], font=("Calibri", 18), justify="right", fg="white", bg="#114F69").place(relx=0.5, rely=yCount, anchor="center")
            yCount += 0.05

def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    icon = tK.PhotoImage(file = "ImageResources/fishing_boat_50.png") # opens an image which can be used by tK
    root.iconphoto(False, icon)     # set the window icon as 'icon' ^
    a = VesselManSys(root)
    vms = UserLoginScreen(a)
    root.mainloop()

runApp()