import codecs

import spacy
from AnswerExtractionYesNo import get_yes_no_answer
from settings import verbose

nlp = spacy.load('en')

# possible head word for each tyep of questions
location_types = ['GPE', 'LOC']
date_types = ['DATE', 'TIME']
person_types = ['PERSON', 'NORP']

is_types = ['is', 'was', 'are', 'were']
is_pos = ['is', 'was', 'are', 'were']
is_neg = ["isn't", "wasn't", "aren't", "weren't"]

do_types = ['did', 'do', 'does']
do_pos = ['did', 'do', 'does']
do_neg = ["didn't", "don't", "doesn't"]


def get_ner_token_pair(text):
    '''
    Careful! NER tag is case sensitive
    :param string text:
    :return: list of (NER tag, text) pair for the given text
    '''
    doc = nlp(text)
    result = []
    for ent in doc.ents:
        result += [(ent.label_, ent.text)]
    return result


def get_when_answer(potent_types, retrieved_passage):
    '''
    Get corresponding answer phrase using the NER tag
    :param list potent_types: Identify a phrase as answer as long as it is one of the potent_types
    :param string retrieved_passage:
    :return:
    '''
    ner_token_pair = get_ner_token_pair(unicode(retrieved_passage))
    if verbose:
        print 'NER token:',ner_token_pair
    if ner_token_pair:
        for ner, token in ner_token_pair:
            if ner in potent_types:
                return token
    return retrieved_passage

def get_where_answer(potent_types, question, retrieved_passage):
    '''
    Get corresponding answer phrase using the NER tag
    :param list potent_types: Identify a phrase as answer as long as it is one of the potent_types
    :param string retrieved_passage:
    :return:
    '''
    ner_token_pair = get_ner_token_pair(unicode(retrieved_passage))
    if verbose:
        print 'NER token Passege:',ner_token_pair

    if ner_token_pair:
        for ner, token in ner_token_pair:
            if ner in potent_types and token not in question:
                return token

    return retrieved_passage


def get_answer(question, expected_type, retrieved_passage):
    '''
    Get the answer for where, who, when, is, do, what, why, how question.

    For is, do question which should return 'YES', 'NO', 'EMPTY', call AnswerExtractionYesNo.get_yes_no_answer()
    For where, when question, return NER phrase
    For who, return passage
    For rest, including what, why, how, return the passage

    We tried to use NER tag to answer who question, but the problem is, NER tagger provided by spaCy sometimes confuses
    between PERSON and ORG, especially for some wired person name in Wikipedia. And there are a lot of case that multiple
    person name exist in one sentence. In this case, just return the retrieved sentence is more reasonable.

    :param string question:
    :param string expected_type:
    :param string retrieved_passage:
    :return: answer phrase of retrieved passage
    '''
    headword = question.split(" ")[0].lower()
    if headword in is_types or headword in do_types:
        result = get_yes_no_answer(question, retrieved_passage)
        if result == 'EMPTY':
            return retrieved_passage
        else:
            return result  # Yes, No
    elif expected_type in ['OTHER', 'CARDINAL']:
        return retrieved_passage
    elif question.lower().strip().startswith("where"):  # expected_type in location_types
        potent_types = location_types
        return get_where_answer(potent_types, question, retrieved_passage)
    elif question.lower().strip().startswith("when"):  # expected_type in date_types
        potent_types = date_types
        return get_when_answer(potent_types, retrieved_passage)
    elif question.lower().strip().startswith("who"):  # expected_type in person_types 
        return retrieved_passage
    else:
        return retrieved_passage





if __name__ == '__main__':
    filepath = "data/AnsEx_train_where.txt"
    with codecs.open(filepath, encoding='utf-8', errors='replace') as infile:
        lines = infile.readlines()
        train_data = [(line.split('\t')[1].strip(), line.split('\t')[2].strip())
                for line in lines if 'NULL' not in line]

    # train_data = [('','Bullet ants are located in Central and South America.')]
    m = len(train_data)


    # for each record, find it's answer
    count_right = 0
    count_empty = 0
    for question, answer in train_data:
        print '=='
        pred_answer = get_answer(question, 'LOC', answer)
        if pred_answer in answer:
            print '+', pred_answer
            count_right += 1
        else:
            if (pred_answer == '/'):
                count_empty += 1
            print '-', pred_answer
    print '***************'
    print 'correct rate:', 1. * count_right / m
    print 'false rate:', 1. * (m - count_right - count_empty) / m
    print 'empty rate:', 1. * count_empty / m
