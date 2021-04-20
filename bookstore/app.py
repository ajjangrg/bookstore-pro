from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from helpers.database import DatabaseHelper

app = Flask(__name__, static_url_path='',
            static_folder='static', template_folder='templates')

# Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bookstore'

mysql = MySQL(app)

# Db Migrations
dbHelper = DatabaseHelper(mysql)


def createTables():
    cur = mysql.connection.cursor()

    # First Check if tables are already created
    resultValue = cur.execute("SHOW TABLES LIKE 'author'")
    if resultValue == 0:
        # Publisher
        cur.execute("CREATE TABLE Publisher(PublisherName VARCHAR(80) PRIMARY KEY, City VARCHAR(60), Country VARCHAR(40), President VARCHAR(40), YearFounded INT(4))")
        # Book
        createBookTableQuery = "CREATE TABLE Book(BookNumber INT PRIMARY KEY AUTO_INCREMENT, BookName VARCHAR(40), PublicationYear INT(4), Pages INT, PublisherName VARCHAR(80), FOREIGN KEY (PublisherName) REFERENCES Publisher(PublisherName))"
        cur.execute(createBookTableQuery)
        # Customer
        createCustomerTableQuery = "CREATE TABLE Customer(CustomerNumber INT PRIMARY KEY AUTO_INCREMENT, CustomerName VARCHAR(40), Street VARCHAR(40), City VARCHAR(40), State VARCHAR(40), Country VARCHAR(40))"
        cur.execute(createCustomerTableQuery)
        # Author
        createAuthorTableQuery = "CREATE TABLE Author(AuthorNumber INT PRIMARY KEY AUTO_INCREMENT, AuthorName VARCHAR(60), YearBorn INT(4), YearDied INT(4))"
        cur.execute(createAuthorTableQuery)
        # Wrote
        createWroteTableQuery = "CREATE TABLE Wrote(BookNumber INT, AuthorNumber INT, FOREIGN KEY(BookNumber) REFERENCES Book(BookNumber), FOREIGN KEY(AuthorNumber) REFERENCES Author(AuthorNumber), PRIMARY KEY(BookNumber, AuthorNumber))"
        cur.execute(createWroteTableQuery)
        # Sale
        createSaleTableQuery = "CREATE TABLE Sale(BookNumber INT, FOREIGN KEY(BookNumber) REFERENCES Book(BookNumber), CustomerNumber INT, FOREIGN KEY(CustomerNumber) REFERENCES Customer(CustomerNumber), Date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, Price INT, Quantity INT)"
        cur.execute(createSaleTableQuery)
        cur.connection.commit()
        cur.close()

######################################################


@app.route('/')
def index():
    createTables()
    return redirect(url_for('books'))


@app.route('/404')
def notFound():
    return render_template('404.html')

# Books


@app.route('/book')
def books():
    books = dbHelper.select('SELECT book.BookNumber, book.BookName, book.PublicationYear, book.Pages, book.PublisherName, author.AuthorName FROM book LEFT OUTER JOIN WROTE ON book.BookNumber = wrote.BookNumber LEFT OUTER JOIN author ON wrote.AuthorNumber = author.AuthorNumber')
    return render_template('book/index.html', books=books, title="Books")


@app.route('/book/create', methods=["GET", "POST"])
def createBook():
    if request.method == 'GET':
        publishers = dbHelper.select('SELECT * FROM Publisher')
        authors = dbHelper.select("SELECT * FROM Author")
        return render_template('book/create.html', publishers=publishers, authors=authors, title="Add a Book")
    else:
        bookName = request.form['bookName']
        publicationYear = request.form['publicationYear']
        pages = request.form['pages']
        publisherName = request.form['publisher']
        authorId = request.form['author']

        book = dbHelper.insert("INSERT INTO Book(BookName, PublicationYear, Pages, PublisherName) VALUES(%s,%s,%s,%s)", [
                               bookName, publicationYear, pages, publisherName])

        # Add to Wrote
        bookId = dbHelper.select("SELECT LAST_INSERT_ID()")
        wrote = dbHelper.insert(
            "INSERT INTO Wrote(BookNumber, AuthorNumber) VALUES(%s,%s)", [bookId, authorId])

        return redirect(url_for('books'))


@app.route('/book/edit/<bookId>', methods=['GET', 'POST'])
def editBook(bookId):
    book = dbHelper.selectOne(
        'SELECT book.BookNumber, book.BookName, book.PublicationYear, book.Pages, book.PublisherName, author.AuthorNumber FROM book LEFT OUTER JOIN WROTE ON book.BookNumber = wrote.BookNumber LEFT OUTER JOIN author ON wrote.AuthorNumber = author.AuthorNumber WHERE book.BookNumber=%s ', [bookId])
    if(book):
        if request.method == 'GET':

            publishers = dbHelper.select("SELECT * FROM publisher")
            authors = dbHelper.select("SELECT * FROM author")
            return render_template('book/edit.html', book=book, publishers=publishers, authors=authors, title="Edit Book")
        elif request.method == 'POST':

            bookName = request.form['bookName']
            publicationYear = request.form['publicationYear']
            pages = request.form['pages']

            authorNumber = request.form['author']

            publisherName = request.form['publisher']

            # Update Wrote
            dbHelper.update("UPDATE wrote SET AuthorNumber = %s WHERE BookNumber = %s", [
                            authorNumber, bookId])
            # Update Book
            dbHelper.update("UPDATE book SET BookName = %s, PublicationYear = %s, Pages = %s, PublisherName = %s WHERE BookNumber = %s", [
                            bookName, publicationYear, pages, publisherName, bookId])
            return redirect(url_for('books'))
    else:
        return redirect(url_for('notFound'))


@app.route('/book/delete/<bookId>')
def deleteBook(bookId):
    book = dbHelper.selectOne(
        "SELECT * FROM book WHERE BookNumber = %s", [bookId])
    if(book):
        deleteEverythingAssociatedToBook(bookId)
        return redirect(url_for('books'))
    else:
        return redirect(url_for('notFound'))


def deleteEverythingAssociatedToBook(bookId):
    # Delete Wrote
    dbHelper.delete("DELETE FROM wrote WHERE BookNumber = %s ", [bookId])
    # Delete Sales
    dbHelper.delete("DELETE FROM sale WHERE BookNumber = %s", [bookId])
    # Delete Book
    dbHelper.delete("DELETE FROM book WHERE BookNumber = %s", [bookId])

##########################################################

# Publisher


@app.route('/publisher')
def publisher():
    publishers = dbHelper.select("SELECT * FROM publisher")
    return render_template('publisher/index.html', publishers=publishers, title="Publishers")


@app.route('/publisher/create', methods=['GET', 'POST'])
def createPublisher():
    if request.method == 'GET':
        return render_template('publisher/create.html', title="Add a Publisher")
    elif request.method == 'POST':
        publisherName = request.form['publisherName']
        city = request.form['city']
        country = request.form['country']
        president = request.form['president']
        yearFounded = request.form['yearFounded']

        dbHelper.insert("INSERT INTO Publisher(PublisherName, City, Country, President, YearFounded) VALUES(%s,%s,%s,%s,%s)", [
                        publisherName, city, country, president, yearFounded])

        return redirect(url_for('publisher'))


@app.route('/publisher/edit/<publisherName>', methods=['GET', 'POST'])
def editPublisher(publisherName):

    publisher = dbHelper.selectOne(
        "SELECT * FROM publisher WHERE PublisherName = %s", [publisherName])

    if(publisher):
        if(request.method == 'GET'):
            return render_template('publisher/edit.html', publisher=publisher, title="Edit Publisher")
        elif(request.method == 'POST'):
            publisherName = request.form['publisherName']
            city = request.form['city']
            country = request.form['country']
            president = request.form['president']
            yearFounded = request.form['yearFounded']

            dbHelper.update("UPDATE publisher SET PublisherName = %s, City = %s, Country = %s, President = %s, YearFounded = %s WHERE PublisherName = %s", [
                            publisherName, city, country, president, yearFounded, publisherName])

            return redirect(url_for('publisher'))
    else:
        return redirect(url_for('notFound'))


@app.route('/publisher/delete/<publisherName>')
def deletePublisher(publisherName):
    publisher = dbHelper.selectOne(
        "SELECT * FROM publisher WHERE PublisherName = %s", [publisherName])
    if(publisher):

        # First we have to delete the associated book sale
        deletePublisherAssociatedBookSales(publisherName)

        dbHelper.delete(
            'DELETE FROM publisher WHERE PublisherName = %s', [publisherName])
        return redirect(url_for('publisher'))
    else:
        return redirect(url_for('notFound'))


def deletePublisherAssociatedBookSales(publisherName):
    books = dbHelper.select(
        "SELECT * FROM book WHERE PublisherName = %s", [publisherName])
    print(books)
    for book in books:
        bookId = book[0]
        deleteEverythingAssociatedToBook(bookId)

#####################################################################


# Author


@app.route('/author')
def author():
    authors = dbHelper.select("SELECT * FROM author")
    return render_template('author/index.html', authors=authors, title="Authors")


@app.route('/author/create', methods=['GET', 'POST'])
def createAuthor():
    if request.method == 'GET':
        return render_template('author/create.html', title="Add an Author")
    elif request.method == 'POST':
        authorName = request.form['authorName']
        yearBorn = request.form['yearBorn']
        yearDied = request.form['yearDied']

        author = dbHelper.insert("INSERT INTO Author(AuthorName, YearBorn, YearDied) VALUES(%s,%s,%s)", [
                                 authorName, yearBorn, yearDied])
        return redirect(url_for('author'))


@app.route('/author/edit/<authorNumber>', methods=['GET', 'POST'])
def editAuthor(authorNumber):
    author = dbHelper.selectOne(
        "SELECT * FROM Author WHERE AuthorNumber = %s", [authorNumber])
    if(author):
        if(request.method == 'GET'):
            return render_template('author/edit.html', author=author, title="Edit Author")
        elif(request.method == 'POST'):
            authorName = request.form['authorName']
            yearBorn = request.form['yearBorn']
            yearDied = request.form['yearDied']

            dbHelper.update("UPDATE Author SET AuthorName = %s, YearBorn = %s, YearDied = %s WHERE AuthorNumber = %s", [
                            authorName, yearBorn, yearDied, authorNumber])
            return redirect(url_for('author'))
    else:
        return redirect(url_for('notFound'))


@app.route('/author/delete/<authorNumber>')
def deleteAuthor(authorNumber):
    author = dbHelper.selectOne(
        "SELECT * FROM Author WHERE AuthorNumber = %s", [authorNumber])
    if(author):

        # Delete Associated Books
        deleteAuthorAssociatedBooks(authorNumber)
        # Delete Wrote
        dbHelper.delete(
            "DELETE FROM wrote WHERE AuthorNumber = %s ", [authorNumber])
        dbHelper.delete(
            "DELETE FROM Author WHERE AuthorNumber = %s", [authorNumber])
        return redirect(url_for('author'))
    else:
        return redirect(url_for('notFound'))


def deleteAuthorAssociatedBooks(authorID):
    books = dbHelper.select(
        "SELECT book.BookNumber FROM book JOIN wrote ON wrote.BookNumber = book.BookNumber JOIN author ON wrote.AuthorNumber = author.AuthorNumber WHERE author.AuthorNumber = %s", [authorID])
    for book in books:
        deleteEverythingAssociatedToBook(book[0])
################################################################

# Customers


@app.route('/customer')
def customer():
    customers = dbHelper.select("SELECT * FROM Customer")
    return render_template('customer/index.html', customers=customers, title="Customers")


@app.route('/customer/create', methods=['GET', 'POST'])
def createCustomer():
    if request.method == 'GET':
        return render_template('customer/create.html', title="Add a Customer")
    elif request.method == 'POST':
        customerName = request.form['customerName']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']

        customer = dbHelper.insert("INSERT INTO Customer(CustomerName, Street, City, State, Country) VALUES(%s,%s,%s,%s,%s)", [
                                   customerName, street, city, state, country])
        return redirect(url_for('customer'))


@app.route('/customer/edit/<customerNumber>', methods=['GET', 'POST'])
def editCustomer(customerNumber):
    customer = dbHelper.selectOne(
        "SELECT * FROM Customer WHERE CustomerNumber = %s", [customerNumber])
    if(customer):
        if(request.method == 'GET'):
            return render_template('customer/edit.html', customer=customer, title="Edit Customer")
        elif(request.method == 'POST'):
            customerName = request.form['customerName']
            street = request.form['street']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']

            customer = dbHelper.update("UPDATE INTO Customer SET CustomerName = %s, Street = %s, City = %s, State = %s, Country = %s WHERE CustomerNumber = %s", [
                                       customerName, street, city, state, country, customerNumber])

            return redirect(url_for('customer'))
    else:
        return redirect(url_for('notFound'))


@app.route('/customer/delete/<customerNumber>')
def deleteCustomer(customerNumber):
    customer = dbHelper.selectOne(
        "SELECT * FROM Customer WHERE CustomerNumber = %s", [customerNumber])
    if(customer):
        # Delete sale
        dbHelper.delete(
            "DELETE FROM sale WHERE CustomerNumber = %s", [customerNumber])
        dbHelper.delete(
            "DELETE FROM Customer WHERE CustomerNumber = %s", [customerNumber])
        return redirect(url_for('customer'))
    else:
        return redirect(url_for('notFound'))

############################################################

# Sale
@app.route('/sale')
def sale():
    sales = dbHelper.select(
        "SELECT Sale.CustomerNumber, Sale.BookNumber, Book.BookName, Customer.CustomerName, Sale.Price, Sale.Quantity, Sale.Date FROM Sale JOIN Customer ON Customer.CustomerNumber = Sale.CustomerNumber JOIN Book ON Book.BookNumber = Sale.BookNumber")
    print(sales)
    return render_template('sale/index.html', sales=sales, title="Add a Sale")


@app.route('/sale/create', methods=['GET', 'POST'])
def createSale():
    if request.method == 'GET':
        customers = dbHelper.select("SELECT * FROM Customer")
        books = dbHelper.select("SELECT * FROM Book")
        return render_template('sale/create.html', customers=customers, books=books, title="Add a Sale")
    elif request.method == 'POST':
        bookId = request.form['book']
        customerId = request.form['customer']
        price = request.form['price']
        quantity = request.form['quantity']

        sale = dbHelper.insert("INSERT INTO Sale(BookNumber, CustomerNumber, Price, Quantity) VALUES(%s,%s,%s,%s)", [
                               bookId, customerId, price, quantity])
        return redirect(url_for('sale'))


@app.route('/sale/delete/<customerNumber>/<bookNumber>')
def deleteSale(customerNumber, bookNumber):
    customer = dbHelper.selectOne(
        "SELECT * FROM sale WHERE (CustomerNumber,BookNumber) = (%s,%s)", [customerNumber, bookNumber])
    if(customer):
        # Delete sale
        dbHelper.delete(
            "DELETE FROM sale WHERE (CustomerNumber,BookNumber) = (%s,%s)", [customerNumber, bookNumber])
        return redirect(url_for('sale'))
    else:
        return redirect(url_for('notFound'))
