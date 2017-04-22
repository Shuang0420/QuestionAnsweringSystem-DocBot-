import codecs
import re
import sys
import json
import numpy as np
from scipy.sparse import hstack
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import CountVectorizer
import spacy
import cPickle

verbose = False

def global_setting():
    global folder 
    folder = 'data/'
    global mod
    mod = {}   

def text_to_pos(source_file, tar_file):
    output = open(tar_file, 'w')
    nlp = spacy.load('en')
    with open(source_file) as file:
        for line in file:
            line = unicode(line[:-1], encoding='utf-8', errors='ignore')
            tokens = nlp(line)
            tar = ''
            for tok in tokens:
                tar += tok.tag_ + ' '
            output.write(tar[:-1] + '\n')

def text_to_ner(source_file, tar_file):
    output = open(tar_file, 'w')
    nlp = spacy.load('en')
    with open(source_file, 'r') as file:
        for line in file:
            line = unicode(line[:-1],encoding='utf-8', errors='ignore')
            doc = nlp(line)
            tar = ''
            for ent in doc.ents:
                tar += ent.label_ + ' '
            output.write(tar[:-1] + '\n')

def text_to_words(source_file, tar_file):
    output = open(tar_file, 'w')
    with open(source_file, 'r') as file:
        k = 0
        for line in file:
            line = line.strip()
            if line:
                tokens = re.sub(r"`",r"'",line).split()
                tar = ""
                for i in range(len(tokens) - 1):
                    tar += tokens[i] + ' '
                modify(tokens[0], k)
                k += 1
                output.write(tar[:-1] + '\n')

def modify(token, k):
    token = token.lower()
    if token == 'when':
        mod[k] = 'DATE'
    elif token == 'where':
        mod[k] = 'GPE'
    elif token == 'who':
        mod[k] = 'PERSON'


# Used to get labels of training set and test set
def get_labels(filename):
    labels = []
    with codecs.open(filename, "r",encoding='utf-8', errors='ignore') as file:
        for line in file:
            labels.append(line.split()[0])
    return labels

# # Used to get features of training set and test set
# def vectorize(filename, vector_fn):
#     docs = []
#     with codecs.open(filename, "r",encoding='utf-8', errors='ignore') as file:
#         for line in file:
#             docs.append(line)
#     vector = CountVectorizer(ngram_range = (1, 2))
#     res = vector.fit_transform(docs)
#     with open(vector_fn, 'wb') as fid:
#         cPickle.dump(vector, fid)  
#     return res

def vectorize_test(filename, vector_fn):
    docs = []
    with codecs.open(filename, "r",encoding='utf-8', errors='ignore') as file:
        for line in file:
            docs.append(line)
    with open(vector_fn, 'rb') as file:
        vector = cPickle.load(file)
    return vector.transform(docs)

# def feature_construction(fn_list):
#     vectors = []
#     features = vectorize(fn_list[0], 'data/at_vector0.pkl')

#     for i in range(1, len(fn_list)):
#         tmp = vectorize(fn_list[i], 'data/at_vector' + str(i) + '.pkl')
#         features = hstack((features, tmp))

#     return features

def feature_construction_test(fn_list):
    features = vectorize_test(fn_list[0], 'data/at_vector0.pkl')
    for i in range(1, len(fn_list)):
        features = hstack((features, vectorize_test(fn_list[i], 'data/at_vector' + str(i) + '.pkl')))
    return features

def classify(classifier_fn, X_test, Y_test = []):
    with open(classifier_fn, 'rb') as file:
        classifier = cPickle.load(file)

    labels_test = LinearSVC.predict(classifier, X_test)

    mapping = {}
    with open('data/mapping.json', 'r') as file:
        mapping = json.loads(file.read())

    result = []

    for label in labels_test:
        res = ''
        if label in mapping:
            res = mapping[label]
        else:
            res = 'OTHER'
        result.append(res)
    for key, val in mod.iteritems():
        result[key] = val

    # count = 0
    # for i in range(len(labels_test)):
    #     if labels_test[i] == Y_test[i]:
    #         count += 1
    # print "accuracy is ", (float)(count) / len(labels_test)
    return result

# def difficulty_classify(classfier, X_test):
#     labels_test = LinearSVC.predict(classifier, X_test)
#     return labels_test

def get_file_name(suffix):
    fn_list = ['words', 'PoS', 'NER']
    return [folder + i + suffix for i in fn_list]

def at_detect(filename):
    global_setting()
    predict_fn_list = get_file_name('_predict.txt')

    # It takes a long time to run pos and ner extraction.
    text_to_words(filename, predict_fn_list[0])
    text_to_pos(predict_fn_list[0], predict_fn_list[1])
    text_to_ner(predict_fn_list[0], predict_fn_list[2])

    X_test = feature_construction_test(predict_fn_list)
    Y_test = get_labels(filename)

    return classify('data/at_classifier.pkl', X_test)

# def difficulty_detect():
#     global_setting()
#     train_fn_list = get_file_name('_diff_train.txt')
#     train_source = 'data/difficulty_train.txt'
#     predict_fn_list = get_file_name('_diff_predict.txt')
#     test_source = 'data/difficulty_test.txt'

#     # text_to_words(test_source, test_fn_list[0])
#     # text_to_pos(test_fn_list[0], test_fn_list[1])
#     # text_to_ner(test_fn_list[0], test_fn_list[2])

#     X_train = feature_construction(train_fn_list)
#     Y_train = get_labels('data/difficulty_label_train.txt')

#     X_test = feature_construction_test(predict_fn_list)
#     Y_test = get_labels('data/difficulty_label_test.txt')

#     return classify('data/difficulty_classifier.pkl', X_train, Y_train, X_test, Y_test)

# def get_difficulty_classfier():
#     with open('data/difficulty_classifier.pkl', 'rb') as file:
#         classifier = cPickle.load(file)
#     return classifier

if __name__ == '__main__':
    # difficulty_detect()
    at_detect('data/AT_test.txt')
