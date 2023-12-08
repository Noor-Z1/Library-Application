from socket import *
from threading import *
from process import *

"""
This class is used to handle client requests
from the server
"""

class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket, library):
        Thread.__init__(self)
        self.cSocket = clientsocket
        self.address = clientAddress
        self.library = library
        print("New connection added: ", clientAddress)

    def run(self):

        clientMsg = self.cSocket.recv(1024).decode()

        self.login(clientMsg)
        self.rent(clientMsg)
        self.returnBook(clientMsg)

        # to be completed by Shemin!!
        self.report(clientMsg)

    def login(self, clientMsg):

        if "login" in clientMsg:
            _, username, password = clientMsg.split(";")
            role = self.library.checkUserRole(username)
            if self.library.checkUserPassword(username, password):
                msg = "loginsuccess" + ";" + username + ";" + role
                self.cSocket.send(msg.encode())
            else:
                print("loginfailure")
                self.cSocket.send("loginfailure".encode())

    def rent(self, clientMsg):

        if clientMsg[0:4] == "rent":
            _, librarianName, clientName, date = clientMsg.split(";")[0:4]
            items = clientMsg.split(";")[4:]

            # check availability
            available = True

            for item in items:
                if item in self.library.books:
                    message = "availabilityerror"
                    if self.library.books[item]['copiesAvailable'] == 0:
                        message += ";" + self.library.getBookTitle(item) + ";" + self.library.getBookAuthor(item)
                        available = False

            if not available:
                self.cSocket.send(message.encode())
            else:
                # check if user has returned all the books that s/he has rented previously
                if (self.library.rentReturnValidation(clientName)):
                    available2 = True
                else:
                    available2 = False
                    message = "renterror"
                    for books in self.library.getBookstoBeReturned(clientName):
                        message += ";" + books
                    self.cSocket.send(message.encode())
                if available2:
                    self.cSocket.send("rentsuccess".encode())
                    self.library.addOperations(clientMsg)

    def returnBook(self, clientMsg):
        if clientMsg[0:5] == "return":
            _, librarianName, clientName, date = clientMsg.split(";")[0:4]
            items = clientMsg.split(";")[4:]

            returned_books = self.library.booksReturned(clientName)
            rented_books = self.library.booksRented(clientName)
            error = False

            for book in items:
                if book not in rented_books:
                    error = True
                    self.cSocket.send("returnerror".encode())
                elif book in returned_books:
                    error = True
                    self.cSocket.send("returnerror".encode())

            if not error:
                cost = self.library.costCalculation(clientName, items, date)
                msg = "returnsuccess" + ";" + cost
                # need to alter the client message to include the cost before storing in operations.txt
                data_to_write = clientMsg[0:4] + ";" + cost + clientMsg[4:]
                self.library.addOperations(data_to_write)
                self.cSocket.send(msg.encode())

    # to be completed by Shemin
    def report(self, clientMsg):
        if clientMsg[0:6] == "report":
            statistics = Statistics(self.library)
            statistics.generateStatistics()

            if clientMsg[0:7] == "report1":
                pass
            elif clientMsg[0:7] == "report2":
                pass
            elif clientMsg[0:7] == "report3":
                pass
            elif clientMsg[0:7] == "report4":
                pass
            else:
                pass


def main():
    # testing library
    library = Library()
    library.addUsers()
    library.addBooks()
    library.checkOperations()

    # let's have a client thread
    HOST = "127.0.0.1"
    PORT = 6000

    mySocket = socket(AF_INET, SOCK_STREAM)
    mySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    mySocket.bind((HOST, PORT))

    while True:
        mySocket.listen()
        cSocket, cAddress = mySocket.accept()
        newClient = ClientThread(cAddress, cSocket, library)
        newClient.start()
        newClient.join()


if __name__ == "__main__":
    main()
