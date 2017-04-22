import re
import nltk
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tag import StanfordNERTagger
import os
from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize
import string
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(text))
    prev = None
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
             if type(i) == Tree:
                     current_chunk.append(" ".join([token for token, pos in i.leaves()]))
             elif current_chunk:
                     named_entity = " ".join(current_chunk)
                     if named_entity not in continuous_chunk:
                             continuous_chunk.append(named_entity)
                             current_chunk = []
             else:
                     continue
    return continuous_chunk

# Alternatively to setting the CLASSPATH add the jar and model via their path:
jar = 'C:/stanford-postagger-2015-04-20/stanford-postagger.jar'
model = 'C:/stanford-postagger-2015-04-20/models/english-left3words-distsim.tagger'

pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')

jar = 'C:/stanford-ner-2015-04-20/stanford-ner.jar'
model = 'C:/stanford-ner-2015-04-20/classifiers/english.all.3class.distsim.crf.ser.gz'

ner_tagger = StanfordNERTagger(model, jar, encoding='utf8')

posTagger = pos_tagger
nerTagger = ner_tagger

sentence = "Where can I find some bubble tea??"
def queryGenrator(sentence):
    #find words in quotes
    quoted = re.findall(r'"([^"]*)"', sentence)
    #get words
    example_words = word_tokenize(sentence)
    #remove punctuation
    example_words = filter(lambda x: x not in string.punctuation, example_words)
    #remove stopwords
    example_words = [word for word in example_words if word not in stopwords.words('english')]

    #get Named Entities
    named_entities = get_continuous_chunks(example_words)

    #get Nouns
    tags = posTagger.tag(example_words)
    res = []
    for (k,t) in tags:
        if str(t).startswith('NN'):
            res.append(str(k))
    nouns = res

    #get verbs
    res = []
    for (k,t) in tags:
        if str(t).startswith('VB'):
            res.append(str(k))
    verbs = res
    print quoted, named_entities, nouns, verbs

queryGenrator(sentence)
