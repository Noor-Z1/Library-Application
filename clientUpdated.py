from tkinter import *
from tkinter import messagebox
from socket import *
from datetime import *

class LoginScreen(Frame):
    def __init__(self, cSocket, master):
        Frame.__init__(self)
        self.serverMessage = None
        self.cSocket = cSocket
        self.master = master

        # to make the frame expand
        self.master.rowconfigure(0, weight=4)
        self.master.columnconfigure(0, weight=4)

        self.usernameLabel = Label(self, text='User name ', justify=CENTER)
        self.usernameLabel.grid(row=0, column=0, padx=10, pady=10)

        self.username = StringVar()
        self.usernameEntry = Entry(self, textvariable=self.username, justify=LEFT)
        self.usernameEntry.grid(row=0, column=1, padx=10, pady=10)

        self.passLabel = Label(self, text='Password ')
        self.passLabel.grid(row=1, column=0, padx=10, pady=10)

        self.password = StringVar()
        self.passEntry = Entry(self, textvariable=self.password, show='*', justify=LEFT)
        self.passEntry.grid(row=1, column=1, padx=5, pady=5)

        self.loginButton = Button(self, text='Login', justify=CENTER, command=self.approvalMsg)
        self.loginButton.grid(row=2, column=1, padx=5, pady=5)

    def approvalMsg(self):
        username = self.usernameEntry.get()
        password = self.passEntry.get()
        if username == '' or password == '':
            messagebox.showerror('Error', 'All fields are required!')
            return
        login = 'login;' + username + ';' + password
        self.cSocket.send(login.encode())
        self.serverMessage = self.cSocket.recv(1024).decode()

        if 'loginfailure' in self.serverMessage:
            messagebox.showerror('Login', 'Username/Password is incorrect!\n')
            self.master.destroy()
        elif 'loginsuccess' in self.serverMessage:
            if 'librarian' in self.serverMessage:
                self.master.librarianName = username
                self.master.showScreen('librarian')
            elif 'manager' in self.serverMessage:
                self.master.manager = username
                self.master.showScreen('manager')


class LibrarianScreen(Frame):
    def __init__(self, cSocket, master):
        Frame.__init__(self)
        self.cSocket = cSocket
        self.librarianName = self.master.librarianName
        self.master = master
        self.master.rowconfigure(1, weight=1)
        self.master.columnconfigure(0, weight=1)

        for i in range(0, 13):
            self.rowconfigure(i, weight=1)
        for i in range(0, 5):
            self.columnconfigure(i, weight=1)

        self.bookLabel = Label(self, text="Books", justify=CENTER, font='Bold', padx=5, pady=5)
        self.bookLabel.grid(columnspan=4, sticky=W + E + N + S)

        self.bookNames = [("A Tale of Two Cities by C.Dickens", BooleanVar()),
                          ("The Little Prince by A.Exupery", BooleanVar()),
                          ("Harry Potter by J.K.Rowling", BooleanVar()),
                          ("And Then The Were None by A.Christie", BooleanVar()),
                          ("Dream of the Red Chamber by C.Xueqin", BooleanVar()),
                          ("The Hobbit by J.Tolkien", BooleanVar()),
                          ("She: A History of Adventure by H.Haggard", BooleanVar()),
                          ("Vardi Wala Gunda by V.Sharma", BooleanVar()),
                          ("The Da Vinci Code by D.Brown", BooleanVar()),
                          ("The Alchemist by P.Coelho", BooleanVar())]
        rowindex = 1
        for book in self.bookNames:
            book[1].set(False)
            self.books = Checkbutton(self, text=book[0], variable=book[1], height=2)
            self.books.grid(row=rowindex, column=0, columnspan=4, sticky=W)
            rowindex += 1

        self.dateLabel = Label(self, text="Date(dd.mm.yyyy):", justify=LEFT, padx=5, pady=5)
        self.dateLabel.grid(row=rowindex + 1, column=0, columnspan=1, sticky=W)

        self.dateEntry = Entry(self, justify=LEFT)
        self.dateEntry.grid(row=rowindex + 1, column=1, columnspan=1, sticky=W, padx=5, pady=5)

        self.clientLabel = Label(self, text="Client's name:", justify=LEFT, padx=5, pady=5)
        self.clientLabel.grid(row=rowindex + 2, column=0, columnspan=1, sticky=W, padx=5, pady=5)

        self.clientEntry = Entry(self, justify=LEFT)
        self.clientEntry.grid(row=rowindex + 2, column=1, columnspan=1, sticky=W, padx=5, pady=10)

        self.rentButton = Button(self, text='Rent', command=self.rentOperation, padx=5, pady=5)
        self.rentButton.grid(row=rowindex + 3, column=0, columnspan=1)

        self.returnButton = Button(self, text='Return', command=self.returnOperation, padx=5, pady=5)
        self.returnButton.grid(row=rowindex + 3, column=1, columnspan=1)

        self.closeButton = Button(self, text='Close', command=self.closeOperation, padx=5, pady=5)
        self.closeButton.grid(row=rowindex + 3, column=2, columnspan=1)

    def rentOperation(self):
        selectedBooks = []
        for i in range(10):
            if self.bookNames[i][1].get():
                selectedBooks.append(i + 1)
        renterName = self.clientEntry.get()
        date = self.dateEntry.get()

        if len(date) != 10 or date[2] != '.' or date[5] != '.':
            messagebox.showerror('Error', 'Date should be in the following format "dd.mm.yyyy"!Please write leading zeros as: 01.01.2000')
            return

        if renterName == '' or date == '' or len(selectedBooks) == 0:
            messagebox.showerror('Error', 'All fields are required!')
            return
        clientMsg = f'rent;{self.librarianName};{renterName};{date};'
        for i in selectedBooks:
            clientMsg += f'{i}'
            if i != selectedBooks[-1]:
                clientMsg += ';'
        print(clientMsg)
        self.cSocket.send(clientMsg.encode())
        serverMsg = self.cSocket.recv(1024).decode()
        print(serverMsg)
        serverMsg = serverMsg.split(';')
        if 'availabilityerror' in serverMsg:
            messagebox.showerror('Availability Error', serverMsg[1:])
        elif 'renterror' in serverMsg:
            messagebox.showerror('Rent Error', f'The following books should be returned first: {serverMsg[1:]}')
        elif 'rentsuccess' in serverMsg:
            messagebox.showinfo('Rent Detail', 'Rent operation has been done successfully!')

    def returnOperation(self):
        selectedBooks = []
        for i in range(10):
            if self.bookNames[i][1].get():
                selectedBooks.append(i + 1)

        renterName = self.clientEntry.get()
        date = self.dateEntry.get()

        if len(date) != 10 or date[2] != '.' or date[5] != '.':
            messagebox.showerror('Error','Date should be in the following format "dd.mm.yyyy"!Please write leading zeros as: 01.01.2000')
            return

        if renterName == '' or date == '' or len(selectedBooks) == 0:
            messagebox.showerror('Error', 'All fields are required!')
            return
        clientMsg = f'return;{self.librarianName};{renterName};{date};'

        for i in selectedBooks:
            clientMsg += f'{i}'
            if i != selectedBooks[-1]:
                clientMsg += ';'

        clientMsg = clientMsg.encode()
        self.cSocket.send(clientMsg)
        serverMsg = self.cSocket.recv(1024).decode()
        serverMsg = serverMsg.split(';')
        print(serverMsg)
        if 'returnerror' in serverMsg:
            messagebox.showerror('Return Error', 'Please check the selected book(s) again!')
        elif 'availabilityerror' in serverMsg:
            messagebox.showerror('Availability Error', serverMsg)
        else:
            messagebox.showinfo('Return Detail', serverMsg)

    def closeOperation(self):
        clientMsg = "close"
        self.cSocket.send(clientMsg.encode())
        self.cSocket.close()
        self.master.destroy()


class ManagerScreen(Frame):
    def __init__(self, cSocket, master):
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
            self.report.grid(row=rowindex, column=0, columnspan=4, sticky=W, padx=5, pady=5)
            rowindex += 1

        self.createButton = Button(self, text='Create', command=self.createReportOperation, width=30)
        self.createButton.grid(row=rowindex + 1, column=0, columnspan=2, sticky=W, padx=5, pady=5)
        self.createButton.columnconfigure(0, weight=4)
        self.createButton.rowconfigure(rowindex + 1, weight=4)

        self.closeButton = Button(self, text='Close', command=self.closeOperation, width=15)
        self.closeButton.grid(row=rowindex + 1, column=2, columnspan=1, sticky=E, padx=5, pady=5)
        self.closeButton.columnconfigure(2, weight=4)
        self.closeButton.rowconfigure(rowindex + 1, weight=4)

    def createReportOperation(self):
        try:
            reportNo = self.reportVariable.get()[1:2]
            clientMsg = f'report{reportNo}'.encode()
            self.cSocket.send(clientMsg)
            serverMsg = self.cSocket.recv(1024).decode()
            messagebox.showinfo(f'Report {reportNo}', serverMsg.split(';')[1:])
        except Exception as e:
            print(e)

    def closeOperation(self):
        clientMsg = "close"
        self.cSocket.send(clientMsg.encode())
        self.cSocket.close()
        self.master.destroy()
class App(Tk):
    def __init__(self, cSocket):
        Tk.__init__(self)
        self.cSocket = cSocket
        # first need to check if connection established then we can show the screen
        self.showScreen('login')


    def showScreen(self, screen):
        if screen == 'login':
            self.loginScreen = LoginScreen(self.cSocket, self)
            self.title('Login')
            self.loginScreen.grid(padx=30, pady=30)

        elif screen == 'librarian':
            self.loginScreen.destroy()
            self.librarianScreen = LibrarianScreen(self.cSocket, self)
            self.title('Librarian Panel')
            self.librarianScreen.grid(padx=10, pady=10)

        elif screen == 'manager':
            self.loginScreen.destroy()
            self.managerScreen = ManagerScreen(self.cSocket, self)
            self.title('Manager Panel')
            self.managerScreen.grid(padx=30, pady=10)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 6000
    socket = socket(AF_INET, SOCK_STREAM)
    socket.connect((HOST, PORT))

    # wait for connection
    serverMsg = socket.recv(1024).decode()
    print(serverMsg)
    if 'connectionsuccess' in serverMsg:
        app = App(socket)
        app.mainloop()
    else:
        messagebox.showerror('Connection Error', serverMsg)
