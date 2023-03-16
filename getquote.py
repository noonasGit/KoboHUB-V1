# By Jonas Johansson
# For the KoboHUB Dashboard

from requests import get
from requests.exceptions import RequestException
from dataclasses import dataclass


@dataclass
class quote_summary:
    quote_text: str
    quote_author :str

def quoteoftheday():
    quote_data = ""
    try:
        response = get('http://api.quotable.io/random')
        if response.ok:
            quote_body = response.json()
            #quote_body = json.loads(rawresponse)
            #print(rawresponse)
            #print(quote_body['quoteText'])
            #print(quote_body['quoteAuthor'])
            quote_text = quote_body['content']
            quote_author = quote_body['author']
            quote_data = quote_summary(quote_text, quote_author)
    except RequestException as e:
        print("Error getting quote")
        quote_text = ""
        quote_author = ""
        quote_data = quote_summary(quote_text, quote_author)

    return quote_data    
