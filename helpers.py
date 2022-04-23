import os
import random
import googlesearch
import requests
from bs4 import BeautifulSoup
from functools import wraps
from flask import g, request, redirect, url_for, session
from urllib.request import Request, urlopen
from urllib.parse import urljoin

#requests.get() method is used to remove any link with response status code 403(forbidden client error) upfront to avoid error in running websearch function
#User agent is used in the request header to avoid from getting HTTP 403 response status code from certain websites that restrict web crawler
#urlopen method return sequence of bytes and can be render into UTF-8
#PDF links is removed to avoid interruption when encoding to UTF-8
#urljoin method is used to concatenate strings of url website with image source in order to get the absolute file path for the image
#Exceptions handling is used to handle attribute error associated with elements in HTML and index error associated with lists in Python

def websearch(query):

        new_list = []
        new_image = []
        new_dict = {"link" : []  , "title" : [], "image":[] }
        search = googlesearch.search(query, num_results = 10, lang = 'en')
        for link in search:
             if link.endswith('pdf'):
                search.remove(link)
        for code in search:
            search_request = requests.get(code,  headers={'User-Agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
            if search_request.status_code == 403:
                 search.remove(code)
        random.shuffle(search)
        print(search)

        for i in search:
             print(i)
             search_request = Request(i, headers={'User-Agent': 'Mozilla/5.0(Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
             print(search_request)
             search_result = urlopen(search_request).read().decode('utf8')
             soup = BeautifulSoup(search_result, "html.parser")
             try:
                  title = soup.title.getText()
             except AttributeError:
                  title = soup.getText()
             gallery = soup.findAll('img', src=True)
             for image in gallery:
                  try:
                       image_new = urljoin(i, image['src'])
                       new_image.append(image_new)
                       image_src = random.choice(new_image)
                  except IndexError:
                       pass
             if len(new_image) == 0:
                image_src = "/static/marbles_logo.png"
             if (len(new_list)) == 0:
                      new_dict.update({"link": (i)   , "title": (title)   , "image": (image_src)  })
                      new_list.append(new_dict)
             else:
                     new_list.append({"link": (i)   , "title": (title)   , "image": (image_src)  })
             new_image.clear()
        return new_list

#decorators are wrapped using functools module to extend the functionality(added login capability) beyond its existing purpose
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



