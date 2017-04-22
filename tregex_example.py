from __future__ import division, unicode_literals
import nltk
from nltk.parse.stanford import StanfordParser
import requests
import Helper


APPOSITION = "NP=n1 < (NP=n2 $.. (/,/ $.. NP=n3))"
parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

def getParserTree(line):
    '''
    return parse tree of the string
    :param line: string
    :return: list of tree nodes
    '''
    return list(parser.raw_parse(line))


def getAppositions(tree):
    url = "http://localhost:9000/tregex"
    request_params = {"pattern": "NP=n1 < (NP=n2 $.. (/,/ $.. NP=n3))"}
    r = requests.post(url, data=text, params=request_params)
    js = r.json()
    if js['sentences'][0] and '0' in js['sentences'][0] and 'namedNodes' in js['sentences'][0]['0']:
        return js['sentences'][0]['0']['namedNodes']
    return None


text = 'Harry Potter, a young boy, is very famous in US'
testTree = Helper.getParserTree(text)
res = getAppositions(testTree)
print 'result',res
# print one by one
if res:
    for c in res:
        print c
