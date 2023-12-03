import socket
from datetime import *
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
                count = 1

                for line in data.split('\n'):
                    if line != '':
                        operation = line.split(';')
                        if operation[0] == 'rent':
                            operations[count] = {'opType': operation[0], 'librarianName': operation[1], 'clientName': operation[2], 'date': operation[3], 'items': []}
                            # since items could be multiple
                            # we need to store them in a list
                            for val in operation[4:]:
                                operations[count]['items'].append(int(val))

                        elif operation[0] == 'return':
                            operations[count] = {'opType': operation[0], 'librarianName': operation[1], 'clientName': operation[2], 'date': operation[3], 'cost': operation[4],'items': []}
                            for val in operation[5:]:
                                operations[count]['items'].append(int(val))
                        count += 1

                file.close()
                return operations

    '''
    This method is used to write data to the
    operations.txt file
    '''

    def write(self, data):
        with open(self.filepath, 'a') as file:
           # the data we have is a string so we need to just write it directly
           file.write(data + '\n')
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
        return self.books[bookID]['title']

    def getBookAuthor(self, bookID):
        if bookID in self.books:
            return self.books[bookID]['authorName']
        else:
            return None

    def librarianOperationsCounter(self):
        librarianOps = {}

        for operation in self.operations:

            if self.operations[operation]['librarianName'] in librarianOps:
                librarianOps[self.operations[operation]['librarianName']] += 1
            else:
                librarianOps[self.operations[operation]['librarianName']] = 1

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

    def clientRentReturnCounter(self):
        clientOps = {}

        for operation in self.operations:
            if self.operations[operation]['clientName'] in clientOps:
                name = self.operations[operation]['clientName']
                if self.operations[operation]['opType'] == 'rent':
                    clientOps[name]['rentCount'] += len(self.operations[operation]['items'])
                elif self.operations[operation]['opType'] == 'return':
                    clientOps[name]['returnCount'] += len(self.operations[operation]['items'])
            else:
                if self.operations[operation]['opType'] == 'rent':
                    clientOps[self.operations[operation]['clientName']] = {'rentCount': len(self.operations[operation]['items']), 'returnCount': 0}
                elif self.operations[operation]['opType'] == 'return':
                    clientOps[self.operations[operation]['clientName']]['returnCount'] += len(self.operations[operation]['items'])
        return clientOps


    def rentReturnValidation(self, clientName):
        # has the client returned previously rented books?
        clientOps = self.clientRentReturnCounter()
        for clients in clientOps:
            if clientOps['clientName'] == clientName:
                if clientOps['returnCount'] == clients['rentCount']:
                    return True
                else:
                    return False

    def booksRented(self, clientName):
        books = []
        for operation in self.operations:
            if self.operations[operation]['clientName'] == clientName and self.operations[operation]['opType'] == 'rent':
                books.append(self.operations[operation]['items'])
        return books[0]

    def booksReturned(self, clientName):
        books = []
        for operation in self.operations:
            if self.operations[operation]['clientName'] == clientName and self.operations[operation]['opType'] == 'return':
                books.append(self.operations[operation]['items'])
        if len(books) == 0:
            return []
        else:
            return books[0]

    def getBookstoBeReturned(self, clientName):
        rentedBooks = self.booksRented(clientName)
        returnedBooks = self.booksReturned(clientName)
        toBeReturned = []

        for book in rentedBooks:
            if book not in returnedBooks:
                toBeReturned.append(self.getBookTitle(book))
        return toBeReturned


    def rentedDaysCount(self, clientName, book, returnDate):
        # need to convert the dates to datetime format to calculate days

        date_format = '%d.%m.%Y'
        returnDate = datetime.strptime(returnDate, date_format)

        for operation in self.operations:
            if self.operations[operation]['clientName'] == clientName and self.operations[operation]['opType'] == 'rent' and book in self.operations[operation]['items']:
                issueDate = datetime.strptime(self.operations[operation]['date'], date_format)
                return (returnDate - issueDate).days


    def costCalculation(self, clientName, returnedBooks, returnDate):
        cost = 0
        for book in returnedBooks:
            cost += self.getBookPrice(book) * self.rentedDaysCount(clientName, book, returnDate)
        return cost


    # for Shemin to complete :)
    def getTotalRevenue(self):
        pass

    def calculateAvgRentalPeriod(self):
        pass

    def rentedBooksWithCount(self):
        rented = {}
        pass

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
                    msg = "login success"+";"+username+";"+role
                    self.cSocket.send(msg.encode())
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
                    if(self.library.rentReturnValidation(clientName)):
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


            elif clientMsg[0:5] == "return":
                _, librarianName, clientName, date = clientMsg.split(";")[0:4]
                items = clientMsg.split(";")[4:]

                # need to check if the book has been already returned or if there is no need to return the book,
                # since it has not been rented at all by the client. In this case the error message (returnerror)
                # should be sent to the client side and the appropriate error message should be displayed in the
                # message box

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
                    msg  = "returnsuccess" + ";" + cost
                    # need to alter the client message to include the cost before storing in operations.txt
                    data_to_write = clientMsg[0:4] + ";" + cost + clientMsg[4:]
                    self.library.addOperations(data_to_write)
                    self.cSocket.send(msg.encode())



            # to be completed by Shemin
            elif clientMsg[0:6] == "report":
                statistics = Statistics(self.library)
                statistics.generateStatistics()
                # to be completed
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

    print(library.books)
    print(library.users)
    print(library.operations)
    # print(library.getMaxRentedBook())    # function not completed yet
    print(library.librarianWithMaxOperations())
    print(library.clientRentReturnCounter())

    # more testing
    print(library.booksRented("john"))
    print(library.booksReturned("john"))
    print(library.getBookstoBeReturned("john"))

    print(library.booksRented("ali"))
    print(library.booksReturned("ali"))
    print(library.getBookstoBeReturned("ali"))

    # COST CALCULATION TEST
    print(library.costCalculation("ali", [4], "15.11.2023"))


if __name__ == "__main__":
    main()
