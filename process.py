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
                            operations[count] = {'opType': operation[0], 'librarianName': operation[1], 'clientName': operation[2], 'date': operation[3], 'cost': float(operation[4]),'items': []} #changed cost type value to float
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

    # report 2
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

    #report 1 "Completed"
    def rentedBooksWithCount(self):
        rented = {}
        for operation in self.operations:
            if self.operations[operation]['opType'] == 'rent':
                for item in self.operations[operation]['items']:
                    if item not in rented.keys():
                        rented[item] = 1
                    elif item in rented.keys():
                        rented[item] +=1
        return rented

    def MaxRentedBook(self):
        allRented = self.rentedBooksWithCount()
        maxRented = 0
        maxBook = []

        for book in allRented:
            if allRented[book] > maxRented:
                maxRented = allRented[book]
        for book in allRented:
            if allRented[book] == maxRented:
                maxBook.append((f"book ID: {book}",f"Maximum rent: {maxRented}"))
        return maxBook




    #report 3 completed
    def TotalRevenue(self):
        cost = 0
        for operation in self.operations:
            if self.operations[operation]['opType'] == 'return':
                cost += self.operations[operation]['cost']
        return cost
    # report 4 "Completed"
    def avgRentalHelper(self,bookID):
        rentReturn = {}
        for operation in self.operations:
            if bookID in self.operations[operation]['items'] and self.operations[operation]['clientName'] not in rentReturn.keys() and self.operations[operation]['opType']=='rent':
                rentReturn[self.operations[operation]['clientName']] = [self.operations[operation]['date'],0]
            elif self.operations[operation]['clientName'] in rentReturn.keys() and self.operations[operation]['opType'] == 'return':
                rentReturn[self.operations[operation]['clientName']][1] = self.operations[operation]['date']
        return rentReturn
    def averageRentalPeriod(self,bookID):
        rentReturn = self.avgRentalHelper(bookID)
        date_format = '%d.%m.%Y'
        sum =0
        for date in rentReturn.values():
            rentDate = datetime.strptime(date[0], date_format)
            returnDate = datetime.strptime(date[1], date_format)
            sum += (returnDate - rentDate).days
        return sum/len(rentReturn.keys())



class Statistics:
    def __init__(self, library):
        self.report1 = None
        self.report2 = None
        self.report3 = None
        self.report4 = None
        self.library = library

    def generateStatistics(self):
        self.report1 = self.library.MaxRentedBooks()
        self.report2 = self.library.librarianWithMaxOperations()
        self.report3 = self.library.TotalRevenue()
        self.report4 = self.library.averageRentalPeriod()

def main():
    # testing library
    library = Library()
    library.addUsers()
    library.addBooks()
    library.checkOperations()

    # print(library.books)
    # print(library.users)
    # print(library.operations)
    print(library.MaxRentedBook()) #2 functions completed
    print(library.TotalRevenue())
    print(library.avgRentalHelper(5))
    print(library.averageRentalPeriod(5))
    # print(library.librarianWithMaxOperations())
    # print(library.clientRentReturnCounter())
    #
    # # more testing
    # print(library.booksRented("john"))
    # print(library.booksReturned("john"))
    # print(library.getBookstoBeReturned("john"))
    #
    # print(library.booksRented("ali"))
    # print(library.booksReturned("ali"))
    # print(library.getBookstoBeReturned("ali"))
    #
    # # COST CALCULATION TEST
    # print(library.costCalculation("ali", [4], "15.11.2023"))


if __name__ == "__main__":
    main()