import socket
from threading import *

'''
This is the dataProcessor class, which will be used to 
read and write data from the specific files 
of our Library Management System.
'''


class dataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath

    def read(self):
        with open(self.filepath, 'r') as file:
            data = file.read()

            if self.filepath == "users.txt":
                users = {}
                for line in data.split('\n'):
                    if line != '':
                        username, password, role = line.split(';')
                        users[username] = {'password': password, 'role': role}
                file.close()
                return users

            elif self.filepath == "books.txt":
                books = {}
                for line in data.split('\n'):
                    if line != '':
                        bookID, title, authorName, pricePerDay, copiesAvailable = line.split(';')
                        books[int(bookID)] = {'title': title, 'authorName': authorName,
                                              'pricePerDay': float(pricePerDay),
                                              'copiesAvailable': int(copiesAvailable)}
                file.close()
                return books

            elif self.filepath == "operations.txt":
                operations = {}
                for line in data.split('\n'):
                    if line != '':
                        operation = line.split(';')
                        if operation[0] == 'rent':
                            operations[operation[0]] = {'librarianName': operation[1], 'clientName': operation[2],
                                                        'date': operation[3],
                                                        'items': []}
                            # since items could be multiple
                            # we need to store them in a list
                            for val in operation[4:]:
                                operations[operation[0]]['items'].append(int(val))

                        elif operation[0] == 'return':
                            operations[operation[0]] = {'librarianName': operation[1], 'clientName': operation[2],
                                                        'date': operation[3],
                                                        'cost': float(operation[4]),
                                                        'items': []}
                            for val in operation[5:]:
                                operations[operation[0]]['items'].append(int(val))

                file.close()
                return operations

    '''
    This method is used to write data to the
    operations.txt file
    '''

    def write(self, data):
        with open(self.filepath, 'a') as file:
            # write data separated by ;
            for item in data:
                file.write(str(item) + ';')

        file.close()


'''
This is the Library class, which will be used to
to manage the data of the Library Management System
and to perform operations on it
'''
class Library:
    def __init__(self):
        self.books = {}
        self.users = {}
        self.operations = {}
        self.statistics = {}

    def addUsers(self):
        data_processor = dataProcessor("users.txt")
        self.users = data_processor.read()

    def addBooks(self):
        data_processor = dataProcessor("books.txt")
        self.books = data_processor.read()

    def checkOperations(self):
        data_processor = dataProcessor("operations.txt")
        self.operations = data_processor.read()

    def addOperations(self, data):
        data_processor = dataProcessor("operations.txt")
        data_processor.write(data)
        self.checkOperations()

    def checkBookAvailability(self, bookID):
        if bookID in self.books:
            if self.books[bookID]['copiesAvailable'] > 0:
                return True
            else:
                return False
        else:
            return False

    def checkUserPassword(self, username, password):
        if username in self.users:
            if self.users[username]['password'] == password:
                return True
            else:
                return False
        else:
            return False

    def checkUserRole(self, username):
        if username in self.users:
            return self.users[username]['role']
        else:
            return None

    def getBookPrice(self, bookID):
        if bookID in self.books:
            return self.books[bookID]['pricePerDay']
        else:
            return None

    def getBookTitle(self, bookID):
        if bookID in self.books:
            return self.books[bookID]['title']
        else:
            return None

    def rentedBooksWithCount(self):
        rented = {}
        for operation in self.operations:
            if operation['operationType'] == 'rent':
                items = operation['itemID']
                for item in items:
                    if item in rented:
                        rented[self.getBookTitle(item)] += 1
                    else:
                        rented[self.getBookTitle(item)] = 1

        return rented

    def getMaxRentedBook(self):
        allRented = self.rentedBooksWithCount()
        maxRented = 0
        maxBook = []

        for book in allRented:
            if allRented[book] > maxRented:
                maxRented = allRented[book]
                maxBook = [book]
            elif allRented[book] == maxRented:
                maxBook.append(book)

        return maxBook

    def librarianOperationsCounter(self):
        librarianOps = {}
        for operation in self.operations:
            if operation['librarianName'] in librarianOps:
                librarianOps[operation['librarianName']] += 1
            else:
                librarianOps[operation['librarianName']] = 1

        return librarianOps

    def librarianWithMaxOperations(self):
        allLibrarians = self.librarianOperationsCounter()
        maxOperations = 0
        maxLibrarian = []

        for librarian in allLibrarians:
            if allLibrarians[librarian] > maxOperations:
                maxOperations = allLibrarians[librarian]
                maxLibrarian = [librarian]
            elif allLibrarians[librarian] == maxOperations:
                maxLibrarian.append(librarian)

        return maxLibrarian



    def getTotalRevenue(self):
        revenue = 0
        for operation in self.operations:
            if operation['operationType'] == 'return':
                revenue += operation['cost']

        return revenue

    def calculateAvgRentalPeriod(self):
        pass


class Statistics:
    def __init__(self, library):
        self.report1 = None
        self.report2 = None
        self.report3 = None
        self.report4 = None
        self.library = library

    def generateStatistics(self):
        self.report1 = self.library.getMostRentedBooks()
        self.report2 = self.library.librarianWithMaxOperations()
        self.report3 = self.library.getTotalRevenue()
        self.report4 = self.library.averageRentalPeriod()


class ClientThread(Thread):
    def __init__(self, clientAddress, clientsocket, library):
        Thread.__init__(self)
        self.csocket = clientsocket
        self.address = clientAddress
        self.library = library
        print("New connection added: ", clientAddress)

        def run(self):
            serverMsg = "SERVER>>CONNECTION SUCCESSFUL".encode()
            self.cSocket.send(serverMsg)
            clientMsg = self.cSocket.recv(1024).decode()

            if clientMsg[0:5] == "login":
                _, username, password = clientMsg.split(";")
                role = self.library.checkUserRole(username)
                if self.library.checkUserPassword(username, password):
                    self.cSocket.send("loginsucess;" + username + role.encode())
                else:
                    self.cSocket.send("loginfailure".encode())

            # recheck
            # Another validation, that must be completed prior to rent operation, is that the server should make
            # sure that the user has already returned all the books that s/he has rented previously. If the user has
            # not returned all the books, then the error message (renterror) should be sent back to client and the
            # appropriate error message should be displayed once again, stating the names of the books, that have
            # to be returned first. Therefore, the operation will be cancelled once again, and no operation will be
            # added to the operations.txtfile.

            elif clientMsg[0:4] == "rent":
                _, librarianName, clientName, date = clientMsg.split(";")[0:4]
                items = clientMsg.split(";")[4:]

                # check availability
                for item in items.split(","):
                    if item in self.library.books:
                        if self.library.books[item]['copiesAvailable'] == 0:
                            self.cSocket.send("booknotavailable".encode())


            elif clientMsg[0:5] == "return":
                _, librarianName, clientName, date, cost = clientMsg.split(";")[0:5]
                items = clientMsg.split(";")[5:]

                # need to check if the book has been already returned or if there is no need to return the book,
                # since it has not been rented at all by the client. In this case the error message (returnerror)
                # should be sent to the client side and the appropriate error message should be displayed in the
                # message box


def main():
    # testing library
    library = Library()
    library.addUsers()
    library.addBooks()

    print(library.books)
    print(library.users)


if __name__ == "__main__":
    main()
