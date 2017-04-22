import sys
from nltk.corpus import stopwords
from nltk import word_tokenize
import string
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
import codecs

from Article import Article
from SearchEngine import SearchEngine
from AT_detection import at_detect
from AnswerExtraction import get_answer
from settings import verbose

ps = PorterStemmer()
RETRIEVAL_LIMIT = 5


def readQuestions(questionFilePath):
    '''
    Read questions from file.
    :param string questionFilePath:
    :return: list of questions
    '''
    with codecs.open(questionFilePath, encoding='utf-8', errors='replace') as infile:
        lines = infile.readlines()
        output = [line.strip() for line in lines]
        return output


def main(argv):
    try:
        inputFilePath = argv[1]
        questionFilePath = argv[2]
    except:
        print "ERROR: Unable to read input argument!!"
        inputFilePath = 'data/a1.txt'
        questionFilePath = 'ques1.txt'
        # exit(1)


    article = Article(inputFilePath)

    # Get questions, queries, expected_types
    questions = readQuestions(questionFilePath)
    expected_types = at_detect(questionFilePath)
    # queries = [remove_stop_words_stem(question) for question in questions]

    assert len(expected_types) == len(questions)
    # assert len(expected_types) == len(queries)


    # Init classes
    se = SearchEngine(article)


    for i in range(len(questions)):
        if verbose:
            print '-' * 10

        result = se.rankByIndri(questions[i])
        topSentence = se.returnTopKResult(result, RETRIEVAL_LIMIT)

        finalAnswer = ''
        # Retrieve the top rankning answers
        for sentence in topSentence:
            if verbose:
                print 'expected_types: %s\n sentence:%s' % (expected_types[i], sentence)

            answer = get_answer(questions[i], expected_types[i], sentence)
            if answer != '/':
                finalAnswer = answer
                break
        if verbose:
            print '==finalAnswer==  ', finalAnswer
        else:
            print finalAnswer


if __name__ == '__main__':
    main(sys.argv)



# def remove_stop_words_stem(sentence):
#     """Remove stop words"""
#     #get words
#     example_words = word_tokenize(sentence)
#     #remove punctuation
#     example_words = filter(lambda x: x not in string.punctuation, example_words)
#     #remove stopwords
#     example_words = [word for word in example_words if word not in stopwords.words('english')]
#     # stem the words
#     example_words = [ps.stem(word) for word in wordpunct_tokenize(example_words)]
#     return ' '.join(example_words)
