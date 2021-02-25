import tkinter as tK


# import mysql or sqlite or something!


class VesselManSys(tK.Frame):
    def __init__(self, root):  # constructor
        print("hello")
        tK.Frame.__init__(self, root)
        self.root = root
        self.root.title("Vessel Management System")  # the window title
        width, height = self.root.winfo_screenwidth(), self.root.winfo_screenheight()  # obtain screen width and height
        self.root.geometry("%dx%d+0+0" % (width, height))  # set window size to the size of screen

    def dbConnection(self):
        pass

    def myone(self):
        print("asfhkjdhnsfl")


class userLoginScreen(VesselManSys):  # screen for user to input login details
    def __init__(self, parent):
        self.root = parent.root
        h1text = tK.Label(text="Vessel Management System\n\n", font=("Calibri", 24)).pack(side="top")
        print("hello1")

    def myting(self):
        print("yessssss")


def runApp():
    root = tK.Tk()  # creates an an instance of a tK.TK() class, i.e. a blank GUI window =
    a = VesselManSys(root)
    a.myone()
    vms = userLoginScreen(a)
    vms.myting()
    root.mainloop()


runApp()
