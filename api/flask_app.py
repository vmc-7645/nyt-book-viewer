"""

"""

# Imports Section


from flask import Flask, request, jsonify, render_template, make_response
from flask_cors import CORS
from flask_restful import Api

# Pymongo
import pymongo


from werkzeug.serving import WSGIRequestHandler

import base64

import datetime

from re import match
import random, string

from numpy import asarray
import cv2

# Local imports
import nyt
from timeout import timeout


@timeout(5)
def url_to_image(url):
    import urllib
    resp = urllib.request.urlopen(url)
    image = asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return image

def UtcNow():
    now = datetime.datetime.utcnow()
    return now

# File management

def getkey(loc:str=".key"):
    """
    Gets key from file.
    
    Parameters
    ----------
    loc: location of .key file.

    Return
    ----------
    Returns contents of location specified by loc.
    """
    try:
        with open(loc, 'r') as file:
            data = file.read().rstrip()
            return data
    except:
        # TODO add error message
        return False

# String processing

def is_valid_email(
        email:str=""
    ):
    """
    Checks whether input string is a valid email.
    
    Parameters
    ----------
    email: input to be tested as to whether it is a valid email or not.
    
    Return
    ----------
    Returns whether or not input string is a valid email address.
    """
    return bool(match(r"^.+@(\[?)[a-zA-Z0-9-.]+\.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$", email))

def is_valid_uname(
        uname:str=""
    ):
    """
    Username requirements:
    - The password should be between 5 and 20 characters in length.
    - It may contain special characters, '-', '_' or '.'.

    Parameters
    ----------
    uname: string being tested for whether it is a valid username or not

    Returns
    ----------
    boolean that is true if input string is a valid username
    """
    return bool(match(r"^[a-zA-Z0-9_.-]{5,20}$", uname))

def is_valid_password(
        pword:str=""
    ):
    """
    Password requirements:
    - The password should be between 8 and 20 characters in length.
    - It should contain at least one uppercase letter.
    - It should contain at least one lowercase letter.
    - It should contain at least one digit.    
    - It may contain special characters, '-', '_' or '.'.

    Parameters
    ----------
    pword: string being tested for whether it is a valid password or not

    Returns
    ----------
    boolean that is true if input string is a valid password

    """
    return bool(match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z0-9_.-]{8,20}$", pword))


def randomword(length:int=6):
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(length))


# Database management
"""
Formats:

user:
{
    'uname': string descibed in is_valid_uname
    'pword': string descibed in is_valid_pword
    'akeys:[
        'key',
        'key',
        'etc'
    ]
}

book:
{
    'isbn':
    'name':
    'author':
    'num_reviews': integer value
    'rating': 
    'fulldata':{
        *RETURNED DATA FROM NYT*
    }
    'reviews':[
        *review*
    ]
}

review:
{
    'uname': username of user who gave review
    'rating':integer 1-10
    'review':string under 512 chars in length
    'comments': ## NOTE that these are linearly ordered ## 
        [
            *comment*
        ]
}

comment:
{
    'uname': username of user who gave comment
    'comment': string under 512 chars in length
}

"""

def get_database():
    """
    Get connection to database.
    
    Parameters
    ----------
    none

    Return
    ----------
    connection
    """
    
    # Provide the mongodb atlas url to connect python to mongodb using pymongo EX: CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>"
    CONNECTION_STRING = getkey('mongo.key')

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = pymongo.MongoClient(CONNECTION_STRING, connect=False)
    
    # Create the database for our example (we will use the same database throughout the tutorial
    # print(client.list_database_names())

    return client['nyt']

def bookexists(
        isbn:str
    ):
    """
    Determines if a book exists in our database or not.

    Parameters
    ----------
    isbn (str): isbn code in string format

    Return
    ----------
    Determines if an book exists already on our list
    """
    
    # Get the database
    dbname = get_database()

    # Get the collection
    collection = dbname['books']

    # Get the books with isbn
    books_with_isbn = collection.find({"isbn": isbn})

    # Convert the books to a list
    books_with_isbn = list(books_with_isbn)

    if len(books_with_isbn)!=0:
        return books_with_isbn[0]

    return False

def unameexists(
        uname:str = ""
    ):
    """
    Checks whether a username exists or not.
    
    Parameters
    ----------
    uname: string representing username to search for.

    Return
    ----------
    Return true if username exists.
    """
    
    # Get the database
    dbname = get_database()

    # Get the collection
    collection = dbname['users']

    # Get the users with name
    users_with_name = collection.find({"uname": uname})

    # Convert the users to a list
    users_with_name = list(users_with_name)

    if len(users_with_name)!=0:
        return users_with_name[0]

    return False

def add_book(
        isbn:str,
        name:str,
        author:str,
        num_reviews:int=0,
        rating:int=0,
        fulldata:dict={},
        reviews:str=[]
    ):
    """
    Add book in format the following 
    {
        'isbn':
        'name':
        'author':
        'num_reviews': integer value
        'rating': 
        'fulldata':{
            *RETURNED DATA FROM NYT*
        }
        'reviews':[
            *review*
        ]
    }
    
    Parameters
    ----------
    isbn (str):
    name (str):
    author (str):
    num_reviews (int):
    rating (int):
    reviews (str):

    Returns
    ----------
    bool: added succesfully or not
    """

    dbname = get_database()
    added_book = dbname.books.insert_one(
        {
        'isbn':isbn,
        'name':name,
        'author':author,
        'num_reviews': num_reviews,
        'rating': rating,
        'fulldata':fulldata,
        'reviews':reviews
        }
    )

    return True

def add_user(
        uname:str,
        pword:str
    ):
    """
    Creates a user with the given username and password.
    
    Parameters
    ----------
    uname: string representing username.
    pword: string representing password.

    Return
    ----------
    Return key if valid, false if not valid.
    """

    # Check validity

    # Check if valid uname
    if not is_valid_uname(uname):
        return jsonify({'type':'error', 'message':'Username is invalid.'})
    
    # Check if valid password
    if not is_valid_password(pword):
        return jsonify({'type':'error', 'message':'Password is invalid.'})

    # Check if uname already exists
    if unameexists(uname):
        return jsonify({'type':'error', 'message':'Username already exists.'})

    # Create auth key
    auth_key = randomword(16)

    dbname = get_database()
    added_user = dbname.users.insert_one(
        {
            'uname':uname,
            'pword':pword,
            'akeys':[
                auth_key
            ]
        }
    )

    return jsonify({'type':'authkey','message':'Successful user creation.','key':auth_key})

def auth_user(
        uname:str,
        pword:str
    ):
    """
    Checks whether a password matches the username, if so return a key for action authentication.
    
    Parameters
    ----------
    uname: string representing username to test password on.
    pword: string representing password.

    Return
    ----------
    Return key if valid, false if not valid.
    """

    # Check if valid uname
    if not is_valid_uname(uname):
        return jsonify({'type':'error', 'message':'Username is invalid.'})
    
    # Check if valid password
    if not is_valid_password(pword):
        return jsonify({'type':'error', 'message':'Password is invalid.'})

    # Check if uname already exists
    user = unameexists(uname)
    if not user:
        return jsonify({'type':'error', 'message':'Username does not exist.'})

    # Create auth key
    auth_key = randomword(16)

    # Ensure password matches
    if user['uname']==uname and user['pword']==pword:

        # Add authkey
        user['akeys'] += auth_key
        
        # If large amount of authorized key
        if len(user['akeys'])>10:
            user['akeys'].pop(0)

        # Get connected
        dbname = get_database()

        # Update authorized keys
        dbname.users.update_one(
            {"uname":uname},
            {
                "$set":{
                    "akeys":user['akeys']
                }
            }
        )
        
        return jsonify({'type':'authkey','message':'Successful user authentication.','key':auth_key})
    else:
        return jsonify({'type':'error','message':'Submitted password does not match username.'})

def auth_action(
        uname:str,
        akey:str
    ):
    
    """
    Checks whether an authentication key matches the username, if so return true.
    
    Parameters
    ----------
    uname: string representing username to test password on.
    akey: string representing authentication key.

    Return
    ----------
    Return true if valid.
    """

    # Check if valid uname
    if not is_valid_uname(uname):
        return False
    
    # Check if uname already exists
    user = unameexists(uname)
    if not user:
        return False

    # Ensure password matches
    if user['uname']==uname and akey in user['akeys']:
        return True
    else:
        return False


#####

WSGIRequestHandler.protocol_version = "HTTP/1.1"

app = Flask(__name__, template_folder='frontend')
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#####

# Default route/test
@app.route('/')
def index():
    return jsonify({'db':str(get_database()['users'])})

# Api

# TODO Default route/test
@app.route('/api/help/')
def h():
    return '''
<html>
<h1>API Help</h1>

<h2>Auth</h2>
<h3>Signup</h3>
<p>/api/signup/</p>
<ul>
    <li>uname: username</li>
    <li>pword: password</li>
</ul>
<p>Returns with response relating whether there was a successful signup. Additionally, if a successful signup occured the user will atain an authentication key.</p>
<h3>Login</h3>
<p>/api/login/</p>
<ul>
    <li>uname: username</li>
    <li>pword: password</li>
</ul>
<p>Returns with response relating whether there was a successful login. Additionally, if a successful login occured the user will atain an authentication key.</p>

<h2>Explore</h2>
<h3>Explore</h3>
<p>/api/explore/</p>
<ul>
    <li>page_number: integer you are requesting</li>
    <li>category: category being requested</li>
</ul>
<p>Returns with response relating whether addition of rating occured or not.</p>

<h2>Review</h2>
<h3>Rate</h3>
<p>/api/rate/</p>
<ul>
    <li>uname: username</li>
    <li>akey: authentication key</li>
    <li>isbn: isbn number of book your review under it</li>
    <li>review: string with intended review in it</li>
    <li>rating: integer between 1 and 10</li>
</ul>
<p>Returns with response relating whether addition of rating occured or not.</p>

<h3>Delete Rating</h3>
<p>/api/deleterating/</p>
<ul>
    <li>uname: username</li>
    <li>akey: authentication key</li>
    <li>isbn: isbn number of book your review under it</li>
</ul>
<p>Returns with response relating whether deletion of rating occured or not.</p>

<h2>Comment</h2>
<h3>Comment</h3>
<p>/api/comment/</p>
<ul>
    <li>uname: username</li>
    <li>akey: authentication key</li>
    <li>isbn: isbn number of book with comment of review under it</li>
    <li>review_uname: username of reviewer you commented under</li>
    <li>comment: comment content you are adding</li>
</ul>
<p>Returns with response relating whether deletion occured or not.</p>

<h3>Delete Comment</h3>
<p>/api/deletecomment/</p>
<ul>
    <li>uname: username</li>
    <li>akey: authentication key</li>
    <li>isbn: isbn number of book with comment of review under it</li>
    <li>review_uname: username of reviewer you commented under</li>
    <li>comment: comment content you are deleting</li>
</ul>
<p>Returns with response relating whether deletion occured or not.</p>

<h3>Alter Comment</h3>
<p>/api/altercomment/</p>
<p>Headers:</p>
<ul>
    <li>uname: username</li>
    <li>akey: authentication key</li>
    <li>isbn: isbn number of book with comment of review under it</li>
    <li>review_uname: username of reviewer you commented under</li>
    <li>comment: comment content you are altering</li>
    <li>updated_comment: updated comment content you are altering too</li>
</ul>
<p>Returns with response relating whether success occured or not.</p>

<h2>Other</h2>
<h3>Ping</h3>
<p>/api/ping/</p>
<p>pong</p>
</html>
'''

# ping
@app.route('/api/ping/', methods=['GET'])
def get_example_picture():
    return "pong"


# User Authentication

# Signup
@app.route('/api/signup/', methods=['POST'])
def signup():
    
    # TODO add encryption
    
    # Get data
    post_data = request.get_json()

    # Login information
    uname = post_data['uname']
    pword = post_data['pword']

    # Add user to database
    return add_user(uname, pword)


# Login
@app.route('/api/login/', methods=['POST'])
def login():
    # TODO add encryption
    
    # Get data
    post_data = request.get_json()

    # Login information
    uname = post_data['uname']
    pword = post_data['pword']

    # Check validity
    return auth_user(uname, pword)

# Explore
@app.route('/api/explore/', methods=['POST'])
def explore():
    
    # Get data
    post_data = request.get_json()

    # page
    page_number = post_data['page_number']
    category    = post_data['category']

    # get data
    books = nyt.bestsellers(
        getkey('nyt.key'),
        "current",
        category, #"full-overview",
        int(page_number)*20
    )["results"]["books"]
    # print(books.keys())

    # go through books, if a book is not in our database, add it
    for book in books:
        book_isbn = book["primary_isbn13"]
        # print(book)
        if not bookexists(book_isbn):
            add_book(
                isbn=book_isbn,
                name=book['title'],
                author=book['author'],
                rating=0,
                fulldata=book,
                reviews=[]
            )
    
    return books

# Explore
@app.route('/api/getbook/', methods=['POST'])
def getbook():
    
    # Get data
    post_data = request.get_json()

    # page
    isbn = post_data['isbn']

    # TODO GET BOOK, REVIEWS, AND COMMENTS FROM OUR DATABASE
    return

# Rate a book
@app.route('/api/rate/', methods=['POST'])
def rate():
    
    # Get data
    post_data = request.get_json()
    print(post_data)

    # User information
    uname  = post_data['uname']
    akey   = post_data['akey']

    # Book
    isbn   = post_data['isbn']

    # Action
    review = post_data['review']
    rating = post_data['rating']

    # If account action is authorized
    authorized = auth_action(uname,akey)
    if not authorized:
        return jsonify({'type':'error','message':'Auth key does not match username.'})
    
    # If book exists on our database, add review
    book = bookexists(isbn)
    if book:
        dbname = get_database()

        num_reviews = book['num_reviews']+1
        book_reviews = book['reviews']
        try:
            for review in book_reviews:
                if review['uname'] == uname:
                    del(review['uname'])
        except:
            pass
        if type(book_reviews)==type(None):
            book_reviews=[]
        book_reviews = book_reviews+[
            {
                'uname': uname,
                'rating':rating,
                'review':review,
                'comments':[]
            }
        ]
    
        try:
            totalscoreundivided =sum([int(i['rating']) for i in book['reviews']])
        except:
            totalscoreundivided=rating
        print(book_reviews)
        # Update authorized keys
        dbname.books.update_one(
            {"isbn":isbn},
            {
                "$set":{
                    "num_reviews":int(num_reviews),
                    "rating":int(totalscoreundivided/int(num_reviews)),
                    "reviews":book_reviews
                }
            }
        )
        
        return jsonify({'type':'success','message':'Review successfully posted.'})

    # If book does not exist
    if not nyt.bookexists(getkey('nyt.key'),isbn):
        return jsonify({'type':'error','message':'Book rating failed. ISBN not found.'})
    return jsonify({'type':'error','message':'Book rating failed. Book not found in database despite ISBN existing.'})


# Deleting a rating of a book
@app.route('/api/deleterating/', methods=['POST'])
def deleterating():
    
    # Get data
    post_data = request.get_json()

    # User information
    uname  = post_data['uname']
    akey   = post_data['akey']

    # Book
    isbn   = post_data['isbn']

    # If account action is authorized
    authorized = auth_action(uname,akey)
    if not authorized:
        return jsonify({'type':'error','message':'Auth key does not match username.'})
    
    # If book exists on our database, add review
    book = bookexists(isbn)
    if book:
        dbname = get_database()

        num_reviews = book['num_reviews']-1
        book_reviews = book['reviews']
        
        for review in book_reviews:
            if review['uname'] == uname:
                del(review['uname'])
        
        totalscoreundivided =sum([int(i['rating']) for i in book['reviews']])
        
        # Update authorized keys
        dbname.books.update_one(
            {"isbn":isbn},
            {
                "$set":{
                    "num_reviews":int(num_reviews),
                    "rating":int(totalscoreundivided/int(num_reviews)),
                    "reviews":book_reviews
                }
            }
        )
        
        return jsonify({'type':'success','message':'Review successfully posted.'})

    # If book does not exist
    if not nyt.bookexists(getkey('nyt.key'),isbn):
        return jsonify({'type':'error','message':'Book rating failed. ISBN not found.'})
    return jsonify({'type':'error','message':'Book rating failed. Book not found in database despite ISBN existing.'})

# Add comment
@app.route('/api/comment/', methods=['POST'])
def comment():
    
    # Get data
    post_data = request.get_json()
    print(post_data)

    # User information
    uname  = post_data['uname']
    akey   = post_data['akey']

    # Book and post
    isbn   = post_data['isbn']
    review_uname  = post_data['review_uname']
    comment = post_data['comment']

    # If account action is authorized
    authorized = auth_action(uname,akey)
    if not authorized:
        return jsonify({'type':'error','message':'Auth key does not match username.'})
    
    # If book exists on our database, add comment
    book = bookexists(isbn)
    if book:

        book_reviews = book['reviews']
        # print(book)

        if type(book_reviews) != type(None):
            for index, review in enumerate(book_reviews):
                if review['uname'] == review_uname:
                    print(review)
                    # Update authorized keys
                    dbname = get_database()
                    # Update comments
                    book_reviews[index]["comments"].append(
                        {
                            "uname":uname,
                            "comment":comment
                        }
                    )
                    dbname.books.update_one(
                        {"isbn":isbn},
                        {
                            "$set":{
                                "reviews":book_reviews
                            }
                        }
                    )

                    return jsonify({'type':'success','message':'Comment posted.'})
            return jsonify({'type':'error','message':'Comment not posted. Reviews found but not review needed for comment.'})
        return jsonify({'type':'error','message':'Comment not posted. No reviews were found.'})

    # If book does not exist
    if not nyt.bookexists(getkey('nyt.key'),isbn):
        return jsonify({'type':'error','message':'Book rating failed. ISBN for book not found.'})
    return jsonify({'type':'error','message':'Book rating failed. Book not found in database despite ISBN existing.'})

@app.route('/api/deletecomment/', methods=['POST'])
def deletecomment():
    
    # Get data
    post_data = request.get_json()

    # User information
    uname  = post_data['uname']
    akey   = post_data['akey']

    # Book and post
    isbn   = post_data['isbn']
    review_uname  = post_data['review_uname']
    comment = post_data['comment']

    # If account action is authorized
    authorized = auth_action(uname,akey)
    if not authorized:
        return jsonify({'type':'error','message':'Auth key does not match username.'})
    
    # If book exists on our database, add comment
    book = bookexists(isbn)
    review = book["uname"]
    if book:

        book_reviews = book['reviews']

        for review in book_reviews:
            if review['uname'] == review_uname:
                for comment in review['uname']['comments']:
                    if comment['uname'] == uname and comment['comment'] == comment:
                        
                        # Removes comment
                        del(comment)

                        # Update authorized keys
                        dbname = get_database()
                        dbname.books.update_one(
                            {"isbn":isbn},
                            {
                                "$set":{
                                    "reviews":book_reviews
                                }
                            }
                        )
                        return jsonify({'type':'success','message':'Comment deleted.'})

                return jsonify({'type':'error','message':'Comment not deleted despite review it was under being found.'})
        
        return jsonify({'type':'error','message':'Comment not deleted. Review not found.'})

    # If book does not exist
    if not nyt.bookexists(getkey('nyt.key'),isbn):
        return jsonify({'type':'error','message':'Comment deletion failed. ISBN for book not found.'})
    return jsonify({'type':'error','message':'Comment deletion failed. Book not found in database despite ISBN existing.'})


@app.route('/api/altercomment/', methods=['POST'])
def altercomment():
    
    # Get data
    post_data = request.get_json()

    # User information
    uname  = post_data['uname']
    akey   = post_data['akey']

    # Book and post
    isbn   = post_data['isbn']
    review_uname  = post_data['review_uname']
    comment = post_data['comment']
    updated_comment = post_data['updated_comment']

    # If account action is authorized
    authorized = auth_action(uname,akey)
    if not authorized:
        return jsonify({'type':'error','message':'Auth key does not match username.'})
    
    # If book exists on our database, add comment
    book = bookexists(isbn)
    review = book["uname"]
    if book:

        book_reviews = book['reviews']

        for review in book_reviews:
            if review['uname'] == review_uname:
                for comment in review['uname']['comments']:
                    if comment['uname'] == uname and comment['comment'] == comment:
                        
                        comment = updated_comment #TOD make sure this works

                        # Update authorized keys
                        dbname = get_database()
                        dbname.books.update_one(
                            {"isbn":isbn},
                            {
                                "$set":{
                                    "reviews":book_reviews
                                }
                            }
                        )
                        return jsonify({'type':'success','message':'Comment edited.'})

                return jsonify({'type':'error','message':'Comment not edited despite review it was under being found.'})
        
        return jsonify({'type':'error','message':'Comment not edited. Review not found.'})

    # If book does not exist
    if not nyt.bookexists(getkey('nyt.key'),isbn):
        return jsonify({'type':'error','message':'Comment edited failed. ISBN for book not found.'})
    return jsonify({'type':'error','message':'Comment edited failed. Book not found in database despite ISBN existing.'})

# Frontend

@app.route('/main/', methods=['GET'])
def main():
    import os
    exists = os.path.exists('frontend/main.html')
    if not exists: 
        return '404 NOT FOUND, NEWSLETTER DOES NOT EXIST.'
    resp = make_response(render_template('main.html'))
    # resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Errors

# TODO Implement correctly
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'type':'error','message':'404 data not found'})


if __name__ == '__main__':
    app.run(debug=True)