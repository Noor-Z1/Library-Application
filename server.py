from socket import *
from threading import *
from process import *


"""
This class is used to handle client requests
incoming to the server

"""

class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket):
        Thread.__init__(self)
        self.cSocket = clientsocket
        self.address = clientAddress
        self.library = Library()  # create library object for this client

    def run(self):
        print("New connection added: ", self.address)  # print the address of the client on console
        self.cSocket.send("connectionsuccess".encode())  # send a message to the client so it can run the application
        self.library.addUsers()  # add users to the library -> this is not the critical section

        # we used try and except block for debugging and exception handling
        while True:   # keep checking for messages from the client
            try:
                clientMsg = self.cSocket.recv(1024).decode()
                print(clientMsg)  # print the message from the client on console
                if 'login' in clientMsg:
                    self.login(clientMsg)
                if 'rent' in clientMsg:
                    self.library.addBooks()         # these are the critical section operations
                    self.library.addOperations()    # these are the critical section operations
                    self.rent(clientMsg)
                if 'return' in clientMsg:
                    self.library.addBooks()
                    self.library.addOperations()
                    self.returnBook(clientMsg)
                if 'report' in clientMsg:
                    self.library.addBooks()
                    self.library.addOperations()
                    self.report(clientMsg)
                if 'close' in clientMsg:            # break the loop and close the connection
                    self.cSocket.close()
                    print("Client at", self.address, "disconnected")
                    break
            except Exception as e:
                print("Exception occurred: ", e)
                break

    def login(self, clientMsg):
        _, username, password = clientMsg.split(";")
        role = self.library.checkUserRole(username)  # check user role as it needs to be sent to the client

        if self.library.checkUserPassword(username, password):  # check user password
            msg = "loginsuccess" + ";" + username + ";" + role
            self.cSocket.send(msg.encode())
        else:
            self.cSocket.send("loginfailure".encode())

    def rent(self, clientMsg):
        _, librarianName, clientName, date = clientMsg.split(";")[0:4]
        items = clientMsg.split(";")[4:]

        # check availability
        available = True
        message = "availabilityerror"
        items = [int(i) for i in items]    # convert string to int for ease

        # validation 1: check if all the books are available
        for item in items:
            if not self.library.checkBookAvailability(item):
                message += ";" + self.library.getBookTitle(item) + ";" + self.library.getBookAuthor(item)
                available = False

        if not available:
            self.cSocket.send(message.encode())    # send the availability error message

        else:      # validation 2: check if all the books are returned or not
            if self.library.rentReturnValidation(clientName):

                self.library.updateOperations("\n" + clientMsg)   # need to write to the operations file
                for item in items:                                # update the books
                    self.library.books[item]['copiesAvailable'] -= 1

                self.library.updatebooks()                       # update the books.txt file
                self.cSocket.send("rentsuccess".encode())
            else:
                message = "renterror"                            # rentreturn validation failed
                # renterror will be formatted as renterror;book1;book2;book3....

                for books in self.library.getBookstoBeReturned(clientName):
                    message += ";" + books
                self.cSocket.send(message.encode())

    def returnBook(self, clientMsg):
        _, librarianName, clientName, date = clientMsg.split(";")[0:4]
        items = clientMsg.split(";")[4:]

        returned_books = self.library.booksReturned(clientName)
        rented_books = self.library.booksRented(clientName)

        items = [int(i) for i in items]   # convert items list to int for ease
        error = False

        for book in items:
            if book not in rented_books:   # validation 1: check if book was rented
                error = True
            elif returned_books.count(book) == rented_books.count(book):
                error = True
            elif self.library.rentedDaysCount(clientName, book, date) == -1:
                error = True

        if error:
            self.cSocket.send("returnerror".encode())

        if not error:
            # calculate the cost
            cost = self.library.costCalculation(clientName, items, date)
            # send success message
            msg = "returnsuccess" + ";" + str(cost)

            # need to alter the client message to include the cost before storing in operations.txt
            data_to_write = "\n" + "return" + ";" + librarianName + ";" + clientName + ";" + date + ";" + str(cost)
            for book in items:
                data_to_write += ";" + str(book)
                self.library.books[book]['copiesAvailable'] += 1  # update the books

            self.library.updateOperations(data_to_write)     # update the operations.txt file
            self.library.updatebooks()                       # update the books.txt file
            self.cSocket.send(msg.encode())

    def report(self, clientMsg):

        if "report1" in clientMsg:
            maxRented = self.library.MaxRentedBook()
            serverMsg = "report1"

            for i in maxRented:
                serverMsg += ";" + i     # making format is as specified in the assignment
            self.cSocket.send(serverMsg.encode())

        elif "report2" in clientMsg:
            librarians = self.library.librarianWithMaxOperations()
            serverMsg = "report2"
            for i in librarians:
                serverMsg += ";" + i
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


if __name__ == "__main__":
    main()
