import socket
from threading import Thread
from tkinter import *
from tkinter import messagebox



class LoginScreen(Frame):
    def __init__(self, csocket):
        Frame.__init__(self)

        self.csocket = csocket
        self.master.title("Login")

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.frame1 = Frame(self)
        self.frame1.pack(padx=5, pady=5)

        self.username = Label(self.frame1, text="Username ")
        self.username.pack(side=LEFT, padx=5, pady=5)

        self.frame2 = Frame(self)
        self.frame2.pack(padx=5, pady=5)

        self.password = Label(self.frame2, text="Password ")
        self.password.pack(side=LEFT, padx=5, pady=5)

        self.frame3 = Frame(self)
        self.frame3.pack()

        self.button = Button(self.frame3, text="Order", command=self.buttonPressed)
        self.button.pack(side=LEFT, padx=5, pady=5)


    def buttonPressed(self):
        username = self.username.get()
        password = self.password.get()
        clientMsg = "login;" + username + ";" + password
        self.csocket.send(clientMsg.encode())

        serverMsg = self.csocket.recv(1024).decode()
        loginStatus = serverMsg.split(";")[0]


        if loginStatus == "loginsuccess":
            messagebox.showinfo("Login", "Login Successful")
            # now need to redirect to appropriate screen
            # based on role of user which is in serverMsg.split(";")[1]
            if serverMsg.split(";")[1] == "librarian":
                self.master.switch_frame(LibrarianScreen)   # not sure about this
            else:
                self.master.switch_frame(CustomerScreen)
        else:
            messagebox.showinfo("Login", "Login Failed")


class LibrarianScreen:
    pass


class CustomerScreen:
    pass

