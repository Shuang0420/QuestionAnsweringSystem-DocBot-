# -*- coding: utf-8 -*-

"""Simple grammar checker

This grammar checker will fix grammar mistakes using Ginger.
"""

import sys
import urllib
import urlparse
from urllib2 import HTTPError
from urllib2 import URLError
import json

def get_ginger_url(text):
    """Get URL for checking grammar using Ginger.
    @param text English text
    @return URL
    """
    API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"

    scheme = "http"
    netloc = "services.gingersoftware.com"
    path = "/Ginger/correct/json/GingerTheText"
    params = ""
    query = urllib.urlencode([
        ("lang", "US"),
        ("clientVersion", "2.0"),
        ("apiKey", API_KEY),
        ("text", text)])
    fragment = ""

    return(urlparse.urlunparse((scheme, netloc, path, params, query, fragment)))


def get_ginger_result(text):
    """Get a result of checking grammar.
    @param text English text
    @return result of grammar check by Ginger
    """
    url = get_ginger_url(text)

    try:
        response = urllib.urlopen(url)
    except HTTPError as e:
            print("HTTP Error:", e.code)
            quit()
    except URLError as e:
            print("URL Error:", e.reason)
            quit()
    except IOError, (errno, strerror):
        print("I/O error (%s): %s" % (errno, strerror))
        quit

    try:
        result = json.loads(response.read().decode('utf-8'))
    except ValueError:
        print("Value Error: Invalid server response.")
        quit()

    return(result)

def get_grammar_error(original_text):
    """main function"""
    # if len(original_text) > 600:
    #     print("You can't check more than 600 characters at a time.")
    #     quit()
    results = get_ginger_result(original_text)

    return len(results[u'LightGingerTheTextResult'])

def main():
    """main function"""
    original_text = " ".join(sys.argv[1:])
    # if len(original_text) > 600:
    #     print("You can't check more than 600 characters at a time.")
    #     quit()
    results = get_ginger_result(original_text)
    print results
    print  len(results[u'LightGingerTheTextResult']) 

if __name__ == '__main__':
    main()
