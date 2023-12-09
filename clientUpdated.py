from threading import *
from tkinter import *
from tkinter import messagebox
from socket import *

# Login Completed
class LoginScreen(Frame):
    def __init__(self,cSocket,master):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.master = master
        # self.lock = RLock()
        self.serverMessage = None

        self.usernameLabel = Label(self,text='User Name ')
        self.usernameLabel.grid(row=0,column=0)

        self.username = StringVar()
        self.usernameEntry = Entry(self,textvariable=self.username)
        self.usernameEntry.grid(row=0,column=1)



        self.passLabel = Label(self,text='Password ')
        self.passLabel.grid(row=1,column=0)

        self.password = StringVar()
        self.passEntry = Entry(self,textvariable=self.password,show='*')
        self.passEntry.grid(row=1,column=1)

        self.loginButton = Button(self,text='Login',justify=CENTER,command=self.approvalMsg)
        self.loginButton.grid(row=2,column=1)
    def approvalMsg(self):
        username = self.usernameEntry.get()
        password = self.passEntry.get()
        login = 'login;' + username + ';' + password
        self.cSocket.send(login.encode())
        self.serverMessage = self.cSocket.recv(1024).decode()
        print(self.serverMessage)
        if 'loginfailure' in self.serverMessage:
            messagebox.showerror('Login', 'Username/Password is incorrect!\n')
            self.master.destroy()
        elif 'loginsuccess' in self.serverMessage:
            if 'librarian' in self.serverMessage:
                self.master.showScreen('librarian')
            elif 'manager' in self.serverMessage:
                self.master.showScreen('manager')

# librarian screen completed
class LibrarianScreen(Frame):
    def __init__(self,cSocket,master,librarianName):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.librarianName = librarianName
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
            book[1].set(False)
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

        self.closeButton = Button(self, text='Close',command=self.master.destroy)
        self.closeButton.grid(row=rowindex + 3, column=2, columnspan=1)

    def rentOperation(self):
        selectedBooks = []
        for i in range(10):
            if self.bookNames[i][1].get():
                selectedBooks.append(i+1)
        renterName = self.clientEntry.get()
        date = self.dateEntry.get()
        clientMsg = f'rent;{self.librarianName};{renterName};{date}'
        for i in selectedBooks:
            clientMsg +=f'{i};'
        self.cSocket.send(clientMsg.encode())

        serverMsg = self.cSocket.recv(1024).decode()
        serverMsg = serverMsg.split(';')
        if 'availabilityerror' in serverMsg:
            messagebox.showerror('Availability Error', serverMsg[1:])
            self.master.destroy()
        elif 'renterror' in serverMsg:
            messagebox.showerror('Rent Error',f'The following books should be returned first: {serverMsg[1:]}')
            self.master.destroy()
        elif 'rentsuccess' in serverMsg:
            messagebox.showinfo('Rent Detail','Rent operation has been done successfully!')
            self.master.destroy()
    def returnOperation(self):
        selectedBooks = []
        for i in range(10):
            if self.bookNames[i][1].get():
                selectedBooks.append(i + 1)

        renterName = self.clientEntry.get()
        date = self.dateEntry.get()

        clientMsg = f'rent;{self.librarianName};{renterName};{date}'
        for i in selectedBooks:
            clientMsg += f'{i};'
        clientMsg = clientMsg.encode()
        self.cSocket.send(clientMsg)

        serverMsg = self.cSocket.recv(1024).decode()
        serverMsg = serverMsg.split(';')
        if 'returnerror' in serverMsg:
            messagebox.showerror('Return Error','Please check the selected book(s) again!')
        else:
            messagebox.showinfo('Return Detail',serverMsg)
            self.master.destroy()
# Manager Completed
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
            "(1) What is the most rented book overall?",
            "(2) Which librarian has the highest number of operations?",
            "(3) What is the total generated revenue by the library?",
            "(4) What is the average rental period for the 'Harry Potter' book?"
        ]
        self.reportVariable = StringVar()
        self.reportVariable.set(self.reports[0])
        rowindex = 1
        for r in self.reports:
            self.report = Radiobutton(self, text=r, value=r, variable=self.reportVariable, height=2)
            self.report.grid(row=rowindex, column=0, columnspan=4, sticky=W)
            rowindex += 1

        self.createButton = Button(self, text='Create', command=self.createReportOperation,width=30)
        self.createButton.grid(row=rowindex + 1, column=0, columnspan=2,sticky=W)
        self.createButton.columnconfigure(0,weight=4)
        self.createButton.rowconfigure(rowindex + 1, weight=4)

        self.closeButton = Button(self, text='Close', command=self.master.destroy,width=15)
        self.closeButton.grid(row=rowindex + 1, column=2, columnspan=1, sticky=E)

    def createReportOperation(self):
        print('test 1')
        try:
            reportNo = self.reportVariable.get()[1:2]
            clientMsg = f'report{reportNo}'.encode()
            self.cSocket.send(clientMsg)
            print('test 2')
            serverMsg = self.cSocket.recv(1024).decode()
            messagebox.showinfo(f'Report {reportNo}', serverMsg)
            self.master.destroy()
        except Exception as e:
            print(e)
        finally:
            self.master.destroy()
class App(Tk):
    def __init__(self, cSocket):
        Tk.__init__(self)

        self.cSocket = cSocket

        self.loginScreen = LoginScreen(self.cSocket,self)
        librarianName = self.loginScreen.usernameEntry.get()
        self.librarianScreen = LibrarianScreen(self.cSocket,self,librarianName)
        self.managerScreen = ManagerScreen(self.cSocket,self)

        #initially show login
        self.showScreen('login')
    def showScreen(self,screen):
        #hide all the screens
        self.loginScreen.grid_forget()
        self.librarianScreen.grid_forget()
        self.managerScreen.pack_forget()

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
    HOST = "127.0.0.1"
    PORT = 6000
    socket = socket(AF_INET, SOCK_STREAM)
    socket.connect((HOST, PORT))
    window = App(socket)
    window.mainloop()
