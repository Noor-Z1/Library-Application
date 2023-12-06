from threading import *
from tkinter import *
from tkinter import messagebox
from socket import *

class LoginScreen(Frame):
    def __init__(self,cSocket,master):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.master = master
        self.lock = RLock()
        # self.serverMsg = self.cSocket.recv(1024).decode()


        self.usernameLabel = Label(self,text='User Name ').grid(row=0,column=0)
        self.username = StringVar()
        self.usernameEntry = Entry(self,textvariable=self.username).grid(row=0,column=1)



        self.passLabel = Label(self,text='Password ').grid(row=1,column=0)
        self.password = StringVar()
        self.passEntry = Entry(self,textvariable=self.password,show='*').grid(row=1,column=1)


        self.loginButton = Button(self,text='Login',justify=CENTER,command=self.approvalMsg).grid(row=2,column=1)

    def approvalMsg(self):
        self.master.showScreen('librarian') # use this after loginsuccess
        # with self.lock:  # with 'with' we are ensuring that the process will be released after it's done
        #                  # or in other words we are using a shortcut for try:acquire finally:release
        #     username = self.usernameEntry.get()
        #     password = self.passEntry.get()
        #     login = 'login;'+username+';'+password
        #     self.cSocket.send(login.encode())
        #     if 'loginfailure' in self.serverMsg:
        #         messagebox.showerror('Login','Username/Password is wrong!\n')

class LibrarianScreen(Frame):
    def __init__(self,cSocket,master):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.master = master

        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        for i in range(0,13):
            self.rowconfigure(i, weight=1)
        for i in range(0,5):
            self.columnconfigure(i, weight=1)


        self.bookLabel = Label(self, text="Books", justify=CENTER, font='Bold')
        self.bookLabel.grid(columnspan=4,sticky=W+E+N+S)

        self.bookNames = [("A Tale of Two Cities by C.Dickens",BooleanVar()),
                          ("The Little Prince by A.Exupery",BooleanVar()),
                          ("Harry Potter by J.K.Rowling",BooleanVar()),
                          ("And Then The Were None by A.Christie",BooleanVar()),
                          ("Dream of the Red Chamber by C.Xueqin",BooleanVar()),
                          ("The Hobbit by J.Tolkien",BooleanVar()),
                          ("She: A History of Adventure by H.Haggard",BooleanVar()),
                          ("Vardi Wala Gunda by V.Sharma",BooleanVar()),
                          ("The Da Vinci Code by D.Brown",BooleanVar()),
                          ("The Alchemist by P.Coelho",BooleanVar())]
        rowindex = 1
        for book in self.bookNames:
            self.books = Checkbutton(self, text=book[0],variable=book[1],height=2)
            self.books.grid(row=rowindex,column=0,columnspan=4,sticky=NS)
            rowindex +=1

        self.dateLabel = Label(self, text="Date(dd.mm.yyyy):", justify=LEFT)
        self.dateLabel.grid(row=rowindex+1, column=0, columnspan=1, sticky=E)

        self.dateEntry = Entry(self, justify=RIGHT)
        self.dateEntry.grid(row=rowindex+1, column=1, columnspan=1, sticky=NS,padx=5,pady=5)

        self.clientLabel = Label(self, text="Client's name:", justify=LEFT)
        self.clientLabel.grid(row=rowindex + 2, column=0, columnspan=1, sticky=E)

        self.clientEntry = Entry(self, justify=RIGHT)
        self.clientEntry.grid(row=rowindex + 2, column=1, columnspan=1, sticky=NS, padx=5, pady=5)

        self.rentButton = Button(self,text='Rent',command=self.rentOperation)
        self.rentButton.grid(row=rowindex+3,column=0,columnspan=1)

        self.returnButton = Button(self, text='Return',command=self.returnOperation)
        self.returnButton.grid(row=rowindex + 3, column=1, columnspan=1)

        self.closeButton = Button(self, text='Close',command=self.closeOperation)
        self.closeButton.grid(row=rowindex + 3, column=2, columnspan=1)

    def rentOperation(self):
        pass
    def returnOperation(self):
        pass
    def closeOperation(self):
        pass
class ManagerScreen(Frame):
    def __init__(self,cSocket,master):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.master = master

        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.reportLabel = Label(self, text="REPORTS", justify=CENTER, font='Bold')
        self.reportLabel.grid(columnspan=4, sticky=W + E + N + S)

        self.reports = [
            ("(1) What is the most rented book overall?",IntVar()),
            ("(2) Which librarian has the highest number of operations?",IntVar()),
            ("(3) What is the total generated revenue by the library?",IntVar()),
            ("(4) What is the average rental period for the 'Harry Potter' book?",IntVar())
        ]
        rowindex = 1
        for r in self.reports:
            self.report = Radiobutton(self, text=r[0], variable=r[1], height=2)
            self.report.grid(row=rowindex, column=0, columnspan=4, sticky=W)
            rowindex += 1

        self.createButton = Button(self, text='Create', command=self.createReportOperation,width=30)
        self.createButton.grid(row=rowindex + 1, column=0, columnspan=2,sticky=W)
        self.createButton.columnconfigure(0,weight=4)
        self.createButton.rowconfigure(rowindex + 1, weight=4)

        self.closeButton = Button(self, text='Close', command=self.closeOperation,width=15)
        self.closeButton.grid(row=rowindex + 1, column=2, columnspan=1, sticky=E)
    def createReportOperation(self):
        pass
    def closeOperation(self):
        pass
class App(Tk):
    def __init__(self, cSocket):
        Tk.__init__(self)

        self.cSocket = cSocket

        self.loginScreen = LoginScreen(self.cSocket,self)
        self.librarianScreen = LibrarianScreen(self.cSocket,self)
        self.managerScreen = ManagerScreen(self.cSocket,self)

        #initially show login
        self.showScreen('login')
    def showScreen(self,screen):
        #hide all the screens
        self.loginScreen.grid_forget()
        self.librarianScreen.grid_forget()
        # self.managerScreen.pack_forget()

        if screen == 'login':
            self.title('Login')
            self.loginScreen.grid(padx=5,pady=5)
        elif screen == 'librarian':
            self.title('Librarian Panel')
            self.librarianScreen.grid(padx=5,pady=5)
        elif screen == 'manager':
            self.title('Manager Panel')
            self.managerScreen.grid(padx=30, pady=10)
if __name__ == "__main__":
    # HOST = "127.0.0.1"
    # PORT = 5000
    # socket = socket(AF_INET, SOCK_STREAM)
    # socket.connect((HOST, PORT))
    window = App(1)
    window.mainloop()