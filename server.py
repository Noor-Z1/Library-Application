from socket import *
from threading import *
from process import *

"""
This class is used to handle client requests
from the server
"""

class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)
        self.cSocket = clientsocket
        self.address = clientAddress
        self.library = Library()


    def run(self):
        self.cSocket.send("connectionsuccess".encode())
        self.library.addUsers()
        while True:
            try:
                clientMsg = self.cSocket.recv(1024).decode()
                print(clientMsg)
                if 'login' in clientMsg:
                    self.login(clientMsg)
                if 'rent' in clientMsg:
                    self.library.addBooks()
                    self.library.addOperations()
                    self.rent(clientMsg)
                if 'return' in clientMsg:
                    self.library.addBooks()
                    self.library.addOperations()
                    self.returnBook(clientMsg)
                if 'report' in clientMsg:
                    self.library.addBooks()
                    self.library.addOperations()
                    self.report(clientMsg)
                if 'close' in clientMsg:
                    self.cSocket.close()
                    print("Client at", self.address, "disconnected")
                    break
            except Exception as e:
                print(e)
                break

    def login(self, clientMsg):
        _, username, password = clientMsg.split(";")
        role = self.library.checkUserRole(username)
        if self.library.checkUserPassword(username, password):
            msg = "loginsuccess" + ";" + username + ";" + role
            self.cSocket.send(msg.encode())
        else:
            print("loginfailure")
            self.cSocket.send("loginfailure".encode())

    def rent(self, clientMsg):
        _, librarianName, clientName, date = clientMsg.split(";")[0:4]
        items = clientMsg.split(";")[4:]

        # check availability
        available = True
        message = "availabilityerror"
        items = [int(i) for i in items]
        for item in items:
            if not self.library.checkBookAvailability(item):
                message += ";" + self.library.getBookTitle(item) + ";" + self.library.getBookAuthor(item)
                available = False

        if not available:
            print("here")
            print(message)
            self.cSocket.send(message.encode())
        else:
            # check if user has returned all the books that s/he has rented previously
            if self.library.rentReturnValidation(clientName):
                self.library.updateOperations("\n" + clientMsg)
                for item in items:
                    self.library.books[item]['copiesAvailable'] -= 1
                self.library.updatebooks()
                self.cSocket.send("rentsuccess".encode())
            else:
                message = "renterror"
                print(self.library.getBookstoBeReturned(clientName))
                for books in self.library.getBookstoBeReturned(clientName):
                    message += ";" + books
                self.cSocket.send(message.encode())

    def returnBook(self, clientMsg):
        _, librarianName, clientName, date = clientMsg.split(";")[0:4]
        items = clientMsg.split(";")[4:]

        returned_books = self.library.booksReturned(clientName)
        rented_books = self.library.booksRented(clientName)
        error = False

        # convert items list to int
        items = [int(i) for i in items]
        for book in items:
            if book not in rented_books:
                error = True
            elif returned_books.count(book) == rented_books.count(book):
                error = True
        if error:
            self.cSocket.send("returnerror".encode())

        if not error:
            cost = self.library.costCalculation(clientName, items, date)
            msg = "returnsuccess" + ";" + str(cost)
            # need to alter the client message to include the cost before storing in operations.txt
            data_to_write = "\n" + "return" + ";" + librarianName + ";" + clientName + ";" + date + ";" + str(cost)
            for book in items:
                data_to_write += ";" + str(book)
                self.library.books[book]['copiesAvailable'] += 1
            self.library.updateOperations(data_to_write)
            self.cSocket.send(msg.encode())
            self.library.updatebooks()

    def report(self, clientMsg):
        if "report1" in clientMsg:
            maxRented = self.library.MaxRentedBook()
            serverMsg = "report1"
            for i in maxRented:
                serverMsg += ";" + i
            self.cSocket.send(serverMsg.encode())
        elif "report2" in clientMsg:
            librarians = self.library.librarianWithMaxOperations()
            serverMsg = "report2"
            for i in librarians:
                serverMsg += ";" + i
            print(serverMsg)
            self.cSocket.send(serverMsg.encode())
        elif "report3" in clientMsg:
            Revenue = self.library.TotalRevenue()
            serverMsg = "report3;" + str(Revenue)
            self.cSocket.send(serverMsg.encode())
        elif "report4" in clientMsg:
            rental_period = self.library.averageRentalPeriod()
            serverMsg = "report4;" + str(rental_period)
            self.cSocket.send(serverMsg.encode())


def main():
    # let's have a client thread
    HOST = "127.0.0.1"
    PORT = 6000

    mySocket = socket(AF_INET, SOCK_STREAM)
    mySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    mySocket.bind((HOST, PORT))

    while True:
        mySocket.listen()
        cSocket, cAddress = mySocket.accept()
        newClient = ClientThread(cAddress, cSocket)
        newClient.start()
        # newClient.join()


if __name__ == "__main__":
    main()
