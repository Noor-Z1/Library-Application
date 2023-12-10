from datetime import *
from threading import RLock

'''
This is the dataProcessor class, which will be used to 
read and write data from the specific files 
of our Library Management System.
'''


class DataProcessor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.Rlock = RLock()

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
                            operations[count] = {'opType': operation[0], 'librarianName': operation[1],
                                                 'clientName': operation[2], 'date': operation[3], 'items': []}
                            # since items could be multiple
                            # we need to store them in a list
                            for val in operation[4:]:
                                operations[count]['items'].append(int(val))

                        elif operation[0] == 'return':
                            operations[count] = {'opType': operation[0], 'librarianName': operation[1],
                                                 'clientName': operation[2], 'date': operation[3],
                                                 'cost': float(operation[4]),
                                                 'items': []}  # changed cost type value to float
                            for val in operation[5:]:
                                operations[count]['items'].append(int(val))
                        count += 1

                return operations

    '''
    This method is used to write data to the
    operations.txt file
    '''

    def writeoperations(self, data):
        with self.Rlock:
            with open(self.filepath, 'a') as file:
                # the data we have is a string so we need to just write it directly
                file.write(data)

    '''
    This method is used to write data to the
    books.txt file
    '''

    def writebooks(self, booksDict):
        # need to write the booksDict back to the books.txt
        with self.Rlock:
            with open(self.filepath, 'w') as file:
                for bookID in booksDict:
                    file.write(str(bookID) + ";" + booksDict[bookID]['title'] + ";" + booksDict[bookID][
                        'authorName'] + ";" + str(booksDict[bookID]['pricePerDay']) + ";" + str(
                        booksDict[bookID]['copiesAvailable']))
                    if bookID != list(booksDict.keys())[-1]:
                        file.write("\n")


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
        data_processor = DataProcessor("users.txt")
        self.users = data_processor.read()

    def addBooks(self):
        data_processor = DataProcessor("books.txt")
        self.books = data_processor.read()

    def addOperations(self):
        data_processor = DataProcessor("operations.txt")
        self.operations = data_processor.read()

    def updateOperations(self, data):
        data_processor = DataProcessor("operations.txt")
        data_processor.writeoperations(data)
        self.addOperations()

    def updatebooks(self):
        data_processor = DataProcessor("books.txt")
        data_processor.writebooks(self.books)

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
                    clientOps[self.operations[operation]['clientName']] = {
                        'rentCount': len(self.operations[operation]['items']), 'returnCount': 0}
                elif self.operations[operation]['opType'] == 'return':
                    clientOps[self.operations[operation]['clientName']]['returnCount'] += len(
                        self.operations[operation]['items'])
        return clientOps

    def rentReturnValidation(self, clientName):
        # has the client returned previously rented books?
        clientOps = self.clientRentReturnCounter()
        print(clientOps)
        for client in clientOps:
            if client == clientName:
                if clientOps[client]['returnCount'] == clientOps[client]['rentCount']:
                    return True
                else:
                    return False
        return True

    def booksRented(self, clientName):
        books = []
        for operation in self.operations:
            if (self.operations[operation]['clientName'] == clientName and self.operations[operation][
                'opType'] == 'rent'):
                books.extend(self.operations[operation]['items'])
        return books

    def booksReturned(self, clientName):
        books = []
        for operation in self.operations:
            if (self.operations[operation]['clientName'] == clientName and self.operations[operation][
                'opType'] == 'return'):
                books.extend(self.operations[operation]['items'])
        if len(books) == 0:
            return []
        else:
            return books

    def getBookstoBeReturned(self, clientName):
        rented_books = self.booksRented(clientName)
        returned_books = self.booksReturned(clientName)
        toBeReturned = []
        for book in rented_books:
            if returned_books.count(book) != rented_books.count(book) and (self.getBookTitle(book)) not in toBeReturned:
                toBeReturned.append(self.getBookTitle(book))
        return toBeReturned

    def rentedDaysCount(self, clientName, book, returnDate):
        # need to convert the dates to datetime format to calculate days
        date_format = '%d.%m.%Y'

        returnDate2 = datetime.strptime(returnDate, date_format)

        for operation in self.operations:
            if (self.operations[operation]['clientName'] == clientName
                    and self.operations[operation]['opType'] == 'rent'
                    and book in self.operations[operation]['items']):
                rentDate = datetime.strptime(self.operations[operation]['date'], date_format)
                if rentDate <= returnDate2:
                    # issueDate = datetime.strptime(self.operations[operation]['date'], date_format)
                    days = (returnDate2 - rentDate).days
                else:
                    return -1
        return days

    def costCalculation(self, clientName, returnedBooks, returnDate):
        cost = 0
        for book in returnedBooks:
            cost += self.getBookPrice(book) * self.rentedDaysCount(clientName, book, returnDate)
        return cost

    # report 1 "Completed"
    def rentedBooksWithCount(self):
        rented = {}
        for operation in self.operations:
            if self.operations[operation]['opType'] == 'rent':
                for item in self.operations[operation]['items']:
                    if item not in rented.keys():
                        rented[item] = 1
                    elif item in rented.keys():
                        rented[item] += 1
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
                maxBook.append(self.getBookTitle(book))
        return maxBook

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

    # report 3 completed
    def TotalRevenue(self):
        cost = 0
        for operation in self.operations:
            if self.operations[operation]['opType'] == 'return':
                cost += self.operations[operation]['cost']
        return cost

    # report 4 "Completed"
    def avgRentalHelper(self):
        rentReturn = {}
        harryPotterID = 3
        for operation in self.operations:
            if (harryPotterID in self.operations[operation]['items'] and self.operations[operation]['clientName']
                    not in rentReturn.keys() and self.operations[operation]['opType'] == 'rent'):
                rentReturn[self.operations[operation]['clientName']] = [self.operations[operation]['date'], 0]
            elif self.operations[operation]['clientName'] in rentReturn.keys() and self.operations[operation][
                'opType'] == 'return':
                rentReturn[self.operations[operation]['clientName']][1] = self.operations[operation]['date']
        return rentReturn

    def averageRentalPeriod(self):
        rentReturn = self.avgRentalHelper()

        if len(rentReturn) == 0:
            return 0

        date_format = '%d.%m.%Y'
        sum = 0
        valid_keys = 0
        for date in rentReturn.values():
            rentDate = datetime.strptime(date[0], date_format)
            if date[1] == 0:
                continue  # skip any rents without a return
            else:
                returnDate = datetime.strptime(date[1], date_format)
                sum += (returnDate - rentDate).days
                valid_keys += 1
        return sum / valid_keys
