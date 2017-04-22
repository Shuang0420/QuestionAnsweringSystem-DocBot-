import operator
from Article import Article
import math
from textblob import TextBlob as tb
from collections import defaultdict
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import PorterStemmer
from settings import verbose


ps = PorterStemmer()

percent_map = set(['what', 'when', 'where', 'who', 'how many', 'how much', 'how', 'why', 'do', 'are', 'have', 'did', 'does', 'were', 'was', 'is', 'had', 'has'])


class SearchEngine:
    """
    SearchEngine class finds the best match sentences
    using given document and query.

    During the information retrieval, query are removed with stop words, stemmed using Porter Stemmer.
    The lines used for matching is also stemmed, with stop words in them.

    But returnTopKResult() return the original sentence, instead of the stemmed one.


    Attributes:
        result: ranking result, dict {sentenceIdx: sentence score}
        sortResult: sorted ranking result, list of (index, score) tuple
        article: Article
    """
    def __init__(self, article):
        '''
        Init the class with article.
        Multiple query can be performed on one article,
        thus only need to initialize the article inverted list once.

        :param article: input list of sentences
        '''
        self.article = article
        self.sentences = article.getRawLines()
        self.sentences_stem = article.getRawLines_stem()

        self.doc_len = 0
        self.myLambda = 0.1
        self.myMu = 2500
        # {word: {docid: [doclen, tf],...}
        self.invertedList = defaultdict(dict)
        self.initiateInvertedList()


    def initiateInvertedList(self):
        '''
        Initialized the inverted list
        :return:
        '''
        bloblist = [tb(sent.strip()) for sent in self.sentences_stem]
        for sentid, blob in enumerate(bloblist):
            sent_len = len(blob.words)
            self.doc_len += sent_len
            for word in blob.words:
                tf = blob.words.count(word)
                self.invertedList[word][sentid] = (sent_len, tf)


    def rankByIndri(self, query):
        '''
        Given the query, compute the ranking score for each sentence.

        :param query: String of query words
        :return: the list of ranking tuple (sentence id, score)
        '''
        # stem the query. Remove the first token
        qargs = [ps.stem(word) for word in wordpunct_tokenize(query)] # wordpunct_tokenize(query)
        if qargs[0] in percent_map:
            qargs = qargs[1:]

        result = defaultdict(float)
        if verbose:
            print 'query:', query
            print 'qargs:', ' '.join(qargs)

        for q in qargs:
            sents = self.invertedList[q]
            ctf = len(sents)
            mle = ctf / float(self.doc_len)
            if mle == 0:
                continue
            for sentid, s in enumerate(self.sentences_stem):
                # initiate score
                if sentid not in result:
                    result[sentid] = 1.0
                if sentid in sents:
                    sent_len = sents[sentid][0]
                    tf = min(sents[sentid][1], 2)
                    result[sentid] *= (1 - self.myLambda) * (tf + self.myMu * mle) / (sent_len + self.myMu) + self.myLambda * mle
                else:
                    sent_len = len(tb(s.strip()).words)
                    result[sentid] *= (1-self.myLambda) * (self.myMu * mle) / (sent_len + self.myMu) + self.myLambda * mle
        for sentid, score in result.iteritems():
            result[sentid] = math.pow(score, 1.0 / len(qargs))

        return result


    def returnTopKResult(self, result, k):
        '''
        Return the top K original sentence.
        '''
        topKResult = sorted(result.items(), key=lambda d: -d[1])[:k]
        topKSentences = [self.sentences[sentid] for sentid, sent in topKResult]
        return topKSentences


def test(article, query):
    '''
    For local Search Engine testing purpose.
    :param article:
    :param query:
    :return:
    '''
    se = SearchEngine(article)
    result = se.rankByIndri(query)
    if verbose:
        print '\t','\n\t'.join(se.returnTopKResult(result, 5))


if __name__ == '__main__':
    article = Article('S10/article/Alessandro_Volta.txt')
    queries_path = 'S10/article/Alessandro_Volta_question.txt'
    queries = []
    with open(queries_path) as infile:
        for line in infile:
            if line.strip() not in queries:
                queries.append(line.strip())
    for query in queries:
        test(article, query)

