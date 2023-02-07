import sqlite3
db = sqlite3.connect('data/ebookstore')
cursor = db.cursor()

# This is where a table in the ebookstore database is created.
# The table must not already exist
# The paramaters for each column is set here.
cursor.execute('''CREATE TABLE IF NOT EXISTS books(
                  id INTEGER PRIMARY KEY,
                  title TEXT,
                  author TEXT,
                  qty INTEGER DEFAULT 0,
                  UNIQUE(id, title),
                  CHECK(length(id) = 4 AND qty >= 0))''')
db.commit()


def new_book ():
    '''
    This function allows users to add a book to the database.
    It asks the user to enter the book information then tries to insert it into the database.
    If the insertion fails, an error message is shown telling the user to try again
    making sure the data is valid.
    '''
    print("Please enter the following information about the book:\n\n")
    new_book_id = input("4-digit ID:  ")
    new_book_title = input("Title:  ")
    new_book_author = input("Author:  ")
    new_book_qty = input("Quantity in stock:  ")
    try:
        cursor.execute('''INSERT INTO books(id, title, author, qty)
                          VALUES(?,?,?,?)''',
                          (new_book_id, new_book_title, new_book_author, new_book_qty))
        db.commit()
        print("Book added.")
    except Exception:
        print("Oops! Please try again making sure of the following:\n"
              "ID must be a unique number\n"
              "Title must be unique\n"
              "The quantity is a number above 0")
        db.rollback()


def display_book(book_id):
    '''
    This function is used to display books in a easy-to-read format.
    It takes in a book_id argument. If book_id = 'a' then all books in the databsae are displayed.
    When book_id is a single ID or a list thereof, all books in the database with those ID's are displayed.
    If book_id is False an error message is displayed saying no books were found.
    '''
    if book_id == "a":
        cursor.execute('''SELECT * FROM books ''')
        print("ID  :  Title  :  Author  : Quantity ")
        for row in cursor:
            print(f"{row[0]} : {row[1]} : {row[2]}  : {row[3]} ")
    elif not book_id:
        print("Book not found")
    else:
        print("ID  :  Title  :  Author  : Quantity ")
        for id in book_id:
            cursor.execute('''SELECT * FROM books WHERE id = ? ''', (id))
            for row in cursor:
                print(f"{row[0]} : {row[1]} : {row[2]}  : {row[3]} ")



def update_book(book_id):
    '''
    This function is used to update a field of a book in the database.
    It takes in book_id as an argument.
    The book_id must be a list containing only one ID in a tuple. If it is False an error message is displayed.
    The ID is converted into a string containing one ID.
    The user is asked to choose what field they wish to update and what the new value will be.
    The function tries to update the field in the database. If it cannot, an error message is displayed.
    '''
    if book_id:
        book_id = book_id[0][0]
        update_field = input("Enter the field you would like to change: (ID, Title, Author, Quantity) ").lower()
        update_value = input("Enter the new value: ")
        try:
            if update_field == "title":
                cursor.execute('''UPDATE books SET title = ? WHERE id = ?''', (update_value, book_id))
            elif update_field == "author":
                cursor.execute('''UPDATE books SET author = ? WHERE id = ?''', (update_value, book_id))
            elif update_field == "quantity":
                cursor.execute('''UPDATE books SET qty = ? WHERE id = ?''', (update_value, book_id))
            elif update_field == "id":
                cursor.execute('''UPDATE books SET id = ? WHERE id = ?''', (update_value, book_id))
            else:
                print("Invalid field")
            print("Book updated")
            db.commit()
        except Exception as e:
            print("Oops! You can't update a book with those values. ")
            db.rollback()
    else:
        print("Book not found")

def delete_book(book_id):
    '''
    This is a function to delete a book row from the database.
    It takes in a list of tuples containing the book ID.
    If the list is True and contains only one ID, the user is asked if they are sure they wish to delete it.
    If the user is sure the book is deleted, if not it returns the user to the menu.
    If more than one ID is present, the user is shown the matching books and asked to enter only one ID or title.
    '''
    if book_id and len(book_id) == 1:
        display_book(book_id)
        book_id = book_id[0][0]
        if input(f"Are you sure you want to delete this book? (y/n)  ") == "y":
            cursor.execute('''DELETE FROM books WHERE id = ? ''', (book_id,))
            print("Book deleted")
            db.commit()
        else:
            print("Returning to menu.")
            pass
    elif len(book_id) > 1:
        print("These are the books you are trying to delete:")
        display_book(book_id)
        print("Please only enter the unique ID or title of ONE book you would like to delete")
        delete_book(id_find(input("Enter the ID or title of the book you would like to delete:  ")))
    else:
        print("Book not found")

def search_book(book_id):
    '''
    This function is used to display the book/books found in a search.
    It takes in a list of book IDs and uses the display_book function to display them,
    It then asks the user if they want to search again or update/delete the book.
    '''
    display_book(book_id)
    choice = input("""\nEnter one of the following if you would like to:
s - search for another book/books
d - delete the book 
u - update the book
press the Enter key twice to return to the menu\n""")
    if choice == "d":
        delete_book(book_id)
    elif choice == "u":
        update_book(book_id)
    elif choice == "s":
        search_book(id_find(input("Enter the ID, title, author of the book/books to display:\n")))
    else:
        pass

def restock():
    '''
    This function is used to find and display the 5 books in the database with the lowest quantity.
    '''
    lowest_stock = cursor.execute('''SELECT id FROM books ORDER BY qty ASC''').fetchmany(size=5)
    print("These are the five books with the lowest quantity in stock:")
    display_book(lowest_stock)
    print("If you would like to restock a book use the update function from the menu to do so.")

def id_find(value):
    '''
    This function is integral in the functioning of the program.
    It takes in value as the argument. This value is the search term used to find the matching fields
    in the database and returns their respective IDs in a list of tuples.
    It tries to convert the value into an int to check if it is the ID of the book.
    If it cannot convert it, the value is searched for in the title and author fields.
    If no matching field is found, the function returns False.
    '''
    try:
        value = int(value)
        cursor.execute('''SELECT id FROM books WHERE ? IN (id)''',(value,))
        id = cursor.fetchall()
    except:
        cursor.execute('''SELECT id FROM books WHERE ? IN (title, author)''', (value,))
        id = cursor.fetchall()
    finally:
        if len(id) > 0:
            return id
        else:
            return False

# This is the menu used to guide the users options in the program.
# It allows the user to choose from different functions regarding the book store database.
while True:
    print("\n==========Main Menu=============\nPlease enter one of the following numbers:\n")
    menu_choice = input("""
1 - Enter a new book
2 - Update book
3 - Delete book
4 - Search books
5 - View all books
6 - View books with lowest stock
0 - Exit\n""")
    if menu_choice == "1":
        new_book()
    elif menu_choice == "2":
        update_book(id_find(input("Enter the ID or title of the book you would like to update:  ")))
    elif menu_choice == "3":
        delete_book(id_find(input("Enter the ID or title of the book you would like to delete:  ")))
    elif menu_choice == "4":
        search_book(id_find(input("Enter the ID, title, author of the book/books to display:\n")))
    elif menu_choice == "5":
        display_book("a")
    elif menu_choice == "6":
        restock()
    elif menu_choice == "0":
        db.close()
        exit()
    else:
        print("Invalid choice")