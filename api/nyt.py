"""
Functions used to connect to the nyt books database via API calls

API Documentation: https://developer.nytimes.com/docs/books-product/1/overview
"""


import requests

import json
from re import match


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

def is_valid_date(
        date:str
        ):
    """
    Checks if the submitted date is in the format 'YYYY-MM-DD'.

    Parameters
    ----------
    date (str): The date string to be checked.

    Returns
    ----------
    bool: True if the date is in the correct format, False otherwise.
    """
    return bool(match(r"^\d{4}-\d{2}-\d{2}$", date))


# API Calls

def status(key):
    response = requests.get(f"https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key={key}")
    return (json.loads(response.content)['status'])

def categories(
        key:str,
        form:str="unformated"
    ):
    """
    Returns list of NYT best seller categories.

    Parameters
    ----------
    key
    form

    Return
    ----------
    Depends largely on input. Alway returns categories in some form however.
    """
    
    # If we don't want to call the API and save some valuable network space
    if form=="deadclean":
        return ['combined-print-and-e-book-fiction', 'combined-print-and-e-book-nonfiction', 'hardcover-fiction', 'hardcover-nonfiction', 'trade-fiction-paperback', 'mass-market-paperback', 'paperback-nonfiction', 'e-book-fiction', 'e-book-nonfiction', 'hardcover-advice', 'paperback-advice', 'advice-how-to-and-miscellaneous', 'hardcover-graphic-books', 'paperback-graphic-books', 'manga', 'combined-print-fiction', 'combined-print-nonfiction', 'chapter-books', 'childrens-middle-grade', 'childrens-middle-grade-e-book', 'childrens-middle-grade-hardcover', 'childrens-middle-grade-paperback', 'paperback-books', 'picture-books', 'series-books', 'young-adult', 'young-adult-e-book', 'young-adult-hardcover', 'young-adult-paperback', 'animals', 'audio-fiction', 'audio-nonfiction', 'business-books', 'celebrities', 'crime-and-punishment', 'culture', 'education', 'espionage', 'expeditions-disasters-and-adventures', 'fashion-manners-and-customs', 'food-and-fitness', 'games-and-activities', 'graphic-books-and-manga', 'hardcover-business-books', 'health', 'humor', 'indigenous-americans', 'relationships', 'mass-market-monthly', 'middle-grade-paperback-monthly', 'paperback-business-books', 'family', 'hardcover-political-books', 'race-and-civil-rights', 'religion-spirituality-and-faith', 'science', 'sports', 'travel', 'young-adult-paperback-monthly']
    elif form=="deadboth":
        return [['Combined Print and E-Book Fiction', 'combined-print-and-e-book-fiction'], ['Combined Print and E-Book Nonfiction', 'combined-print-and-e-book-nonfiction'], ['Hardcover Fiction', 'hardcover-fiction'], ['Hardcover Nonfiction', 'hardcover-nonfiction'], ['Trade Fiction Paperback', 'trade-fiction-paperback'], ['Mass Market Paperback', 'mass-market-paperback'], ['Paperback Nonfiction', 'paperback-nonfiction'], ['E-Book Fiction', 'e-book-fiction'], ['E-Book Nonfiction', 'e-book-nonfiction'], ['Hardcover Advice', 'hardcover-advice'], ['Paperback Advice', 'paperback-advice'], ['Advice How-To and Miscellaneous', 'advice-how-to-and-miscellaneous'], ['Hardcover Graphic Books', 'hardcover-graphic-books'], ['Paperback Graphic Books', 'paperback-graphic-books'], ['Manga', 'manga'], ['Combined Print Fiction', 'combined-print-fiction'], ['Combined Print Nonfiction', 'combined-print-nonfiction'], ['Chapter Books', 'chapter-books'], ['Childrens Middle Grade', 'childrens-middle-grade'], ['Childrens Middle Grade E-Book', 'childrens-middle-grade-e-book'], ['Childrens Middle Grade Hardcover', 'childrens-middle-grade-hardcover'], ['Childrens Middle Grade Paperback', 'childrens-middle-grade-paperback'], ['Paperback Books', 'paperback-books'], ['Picture Books', 'picture-books'], ['Series Books', 'series-books'], ['Young Adult', 'young-adult'], ['Young Adult E-Book', 'young-adult-e-book'], ['Young Adult Hardcover', 'young-adult-hardcover'], ['Young Adult Paperback', 'young-adult-paperback'], ['Animals', 'animals'], ['Audio Fiction', 'audio-fiction'], ['Audio Nonfiction', 'audio-nonfiction'], ['Business Books', 'business-books'], ['Celebrities', 'celebrities'], ['Crime and Punishment', 'crime-and-punishment'], ['Culture', 'culture'], ['Education', 'education'], ['Espionage', 'espionage'], ['Expeditions Disasters and Adventures', 'expeditions-disasters-and-adventures'], ['Fashion Manners and Customs', 'fashion-manners-and-customs'], ['Food and Fitness', 'food-and-fitness'], ['Games and Activities', 'games-and-activities'], ['Graphic Books and Manga', 'graphic-books-and-manga'], ['Hardcover Business Books', 'hardcover-business-books'], ['Health', 'health'], ['Humor', 'humor'], ['Indigenous Americans', 'indigenous-americans'], ['Relationships', 'relationships'], ['Mass Market Monthly', 'mass-market-monthly'], ['Middle Grade Paperback Monthly', 'middle-grade-paperback-monthly'], ['Paperback Business Books', 'paperback-business-books'], ['Family', 'family'], ['Hardcover Political Books', 'hardcover-political-books'], ['Race and Civil Rights', 'race-and-civil-rights'], ['Religion Spirituality and Faith', 'religion-spirituality-and-faith'], ['Science', 'science'], ['Sports', 'sports'], ['Travel', 'travel'], ['Young Adult Paperback Monthly', 'young-adult-paperback-monthly']]

    # API calling
    response = requests.get(f"https://api.nytimes.com/svc/books/v3/lists/names.json?api-key={key}")
    if form=="unformated":
        return (json.loads(response.content)['results'])
    elif form=="onlynames":
        return [i['list_name'] for i in (json.loads(response.content)['results'])]
    elif form=="onlyclean":
        return [i['list_name'].lower().replace(' ','-') for i in (json.loads(response.content)['results'])]
    elif form=="both":
        return [[i['list_name'],i['list_name'].lower().replace(' ','-')] for i in (json.loads(response.content)['results'])]

def bestsellers(
        key:str,
        date:str="current",
        category:str="overview",
        offset:int=0
    ):
    """
    Gets bestsellers from date and category.
    Reference: https://developer.nytimes.com/docs/books-product/1/routes/lists/%7Bdate%7D/%7Blist%7D.json/get

    Parameters
    ----------
    date (str): date in YYYY-MM-DD format or "current" for today
    category (str): category from categories list in proper format (no caps, spaces replaced with dashes). May also include 'overview' or 'full-overview'.
    offset (int): integer multiple of 20

    Return
    ----------
    Returns list of bestsellers
    """

    if date != "current" and not is_valid_date(date):
        return {'type':'error','message':'Improper date input.'}
    elif category.lower().replace(' ','-') not in categories('',"deadclean"):
        if category in ['overview','full-overview']:
            return json.loads(requests.get(f"https://api.nytimes.com/svc/books/v3/lists/{category}.json?api-key={key}&offset={offset}").content)
        return {'type':'error','message':'Invalid category input.'}

    return json.loads(requests.get(f"https://api.nytimes.com/svc/books/v3/lists/{date}/{category}.json?api-key={key}&offset={offset}").content)

def bookexists(
        key:str,
        isbn:str
    ):
    """
    If an isbn for a book exists, return true.
    
    Parameters
    ----------
    key (str):
    isbn (str):

    Returns
    ----------
    bool: true if book exists.
    """
    

    link = requests.get(f"https://api.nytimes.com/svc/books/v3/reviews.json?isbn={isbn}&api-key={key}").content
    print(link)
    exists = bool((json.loads(link)["num_results"])>=0)
    
    return exists
    


if __name__ == '__main__':
    
    a = bestsellers(getkey("nyt.key"),"current",'combined-print-and-e-book-fiction',0)
    print((a))