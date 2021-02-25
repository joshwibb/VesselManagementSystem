import tkinter as tK
# import mysql or sqlite or something!


class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        tK.Frame.__init__(self, root) # creates a tkinter frame - a window
        self.root = root # the root window was passed as a parameter
        self.root.title("Vessel Management System")  # the window title
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen

    def dbConnection(self):
        pass

class userLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent): # constructor
        self.root = parent.root # inherit the root tkinter window from VesselManSys class
        self.loginScreen()

    def loginScreen(self):
        h1text = tK.Label(text="Vessel Management System\n\n", font=("Calibri", 28)).pack(side="top")  # window heading text centered at the top available space
        sidtext = tK.Label(text="Staff ID", font=("Calibri", 22)).pack(side="top")  # text left of entry box
        self.sidbox = tK.Entry(self.root, width=35) # text entry box for staff id
        sidboxpack = self.sidbox.pack(side="top") # place the text entry box on the screen
        pwtext = tK.Label(text="\nPassword", font=("Calibri", 22)).pack(side="top")  # text left of entry box
        self.pwbox = tK.Entry(self.root, width=35)  # text entry box for password
        pwboxpack = self.pwbox.pack(side="top") # place the text entry box on the screen
        loginBut = tK.Button(text="Log In", command=lambda : self.loginBackend()).pack(side="top") # login button - when clicked runs loginBackend function

    def loginBackend(self):
        tempSID = self.sidbox.get()

        self.staffID = int(self.sidbox.get())


def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window
    a = VesselManSys(root)
    vms = userLoginScreen(a)
    root.mainloop()


runApp()
