import spacy
from settings import verbose

nlp = spacy.load('en')

# Possible headers for Is, Do type questions
# _pos and _neg type can be used in the future work
is_types = ['is', 'was', 'are', 'were']
is_pos = ['is', 'was', 'are', 'were']
is_neg = ["isn't", "wasn't", "aren't", "weren't"]

do_types = ['did', 'do', 'does']
do_pos = ['did', 'do', 'does']
do_neg = ["didn't", "don't", "doesn't"]


def show_structure(doc):
    '''
    Dependency parsing.
    :param doc: spaCy doc class
    '''
    print doc
    for token in doc:
        print '%15s | %8d |% 10s | %15s' % (token.text, token.dep,
                                            token.dep_, token.head.text)
    print ''


def show(doc):
    '''
    show detail information about the given doc
    :param doc: spaCy doc class
    '''
    print '-' * 10
    for word in doc:
        print word.text, word.lemma_, word.tag_, word.pos_, word.ent_type_


def show_noun_trunk(doc):
    print '-' * 10, 'show_noun_trunk'
    for word in doc.noun_chunks:
        print word.text


def show_noun(doc):
    '''
    show all the noun in the sentence
    :param doc: spaCy doc class
    '''
    print '-' * 10, 'show_noun'
    for word in doc:
        if word.pos_ in ['NOUN', 'PROPN']:
            print word.lemma_, word.tag_, word.pos_, word.ent_type_


def get_noun_lemma_no_person(doc):
    '''
    Get all the lemmatized nouns except nouns that are person name.
    :param doc: spaCy doc class
    '''
    result = []
    for word in doc:
        if word.pos_ in ['NOUN', 'PROPN'] and word.ent_type_ != 'PERSON':
            result += [word.lemma_]
    return result


def get_noun_lemma(doc):
    '''
    Get all the lemmatized nouns.
    :param doc: spaCy doc class
    '''
    result = []
    for word in doc:
        if word.pos_ in ['NOUN', 'PROPN']:
            result += [word.lemma_]
    return result


def get_yes_no_answer(ques_text, sent_text):
    '''
    A heuristic stategy for answering Yes or No for Is, Do type question.
    The basic idea is that, if the answer is yes, then all the noun in the question should be found in the retrieved
    sentence. However, in many situation, question may contain full person name while retrieved sentence only contains
    first name or last name. So we used NER tagger to identify person name, and allow partial match in person name.

    For noun phrase match, we use lemmatized word.
    For name matching, it's case sensitive and exact match.

    For some sentence that do not contain any noun (including name), our heuristic strategy will fail. In this case, we
    just return 'EMPTY'.

    :param string ques_text: string format of question
    :param string sent_text: string format of retrieved sentence from search engine
    :return: 'YES', 'NO', 'EMPTY'
    '''
    ques = nlp(ques_text)
    sent = nlp(sent_text)

    doc1_nouns = get_noun_lemma_no_person(ques)
    doc2_nouns = get_noun_lemma_no_person(sent)
    doc1_names = find_person_name(ques)

    # if
    if not doc1_nouns and not doc1_names:
        return 'EMPTY'

    if verbose:
        print '-' * 10
        print 'doc1_nouns', doc1_nouns
        print 'doc2_nouns', doc2_nouns

        print '-' * 10
        print 'doc1_names', doc1_names
        print '-' * 10

    for word in doc1_nouns:
        if word not in doc2_nouns:
            return 'No'

    for name in doc1_names:
        # if at least part of this name is contained in doc2
        # name = ['Alessandro', 'Volta']
        flag = False
        for token in name:
            if token in sent.text:
                flag = True
                break
        if flag == False:
            return 'No'

    return 'Yes'


def find_person_name(doc):
    '''
    Return 2D array containing person name
    [['Xiaoyu', 'He'], ['Andrew', 'Ng']]
    '''
    names = []
    start = -1
    for i in range(len(doc)):
        if doc[i].ent_type_ == 'PERSON':
            if start == -1:
                start = i
        elif start != -1:
            name = [doc[k].text for k in range(start, i)]
            names.append(name)
            start = -1
    return names





# def main():
#     text1 = u'Was Alessandro Volta a professor of chemistry?'
#     text2 = u'In 1776-77 Volta studied the chemistry of gases, he discovered methane by collecting the gas from marshes.'
#     print noun_words_match(text1, text2)
#
#
# if __name__ == '__main__':
#     main()