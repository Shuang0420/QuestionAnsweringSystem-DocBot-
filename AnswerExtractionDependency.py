from spacy import symbols
import spacy

nlp = spacy.load('en')
nsubj_group = ['nsubj', 'nsubjpass']

def show_structure(doc):
        for token in doc:
            print '%15s | %8d |% 10s | %15s' % (token.text, token.dep,
                                                token.dep_, token.head.text)


def show(token):
    print token.text, token.dep_  # token.lemma_


def get_verb_subj(question):
    # for token in question:
    #     if token.head.dep_ == 'ROOT' and token.dep_ == 'ccomp':
    #         verb = token
    for token in question:
        if token.dep_ in ['nsubj', 'nsubjpass']:  # and token.head == verb
            subj = token
            verb = subj.head
            if verb.pos_ != 'VERB':
                continue
    return verb, subj


def process_passage(doc, verb, subj):
    for rootmatch in doc:
        if rootmatch.lemma_ == verb.lemma_:
            for prepmatch in doc:
                if prepmatch.head == rootmatch and prepmatch.dep_ == 'prep':
                    for pobjmatch in doc:
                        if pobjmatch.head == prepmatch and pobjmatch.dep_ == 'pobj':
                            match = pobjmatch

    answer = []
    for subtoken in match.subtree:
        answer += [subtoken.text]
    return ' '.join(answer)


def get_answer(question, passage):
    print '-' * 10
    print 'question:', question
    print 'passage:', passage
    verb, subj = get_verb_subj(nlp(question))
    print 'verb:', show(verb)
    print 'subj:', show(subj)

    # now try to find the answer~
    answer = process_passage(nlp(passage), verb, subj)
    print answer
    return 'Final answer', answer


if __name__ == '__main__':
    question = u'Where are Bullet ants located?'
    passage = u'Bullet are located in Central and South America.'
    get_answer(question, passage)

    question = u'Where do Bullet ants lives?'
    passage = u'Bullets live in Central and South America'
    get_answer(question, passage)

    question = u'Where was Mary born?'
    passage = u'Mary was born in America.'
    get_answer(question, passage)



'''


'''
