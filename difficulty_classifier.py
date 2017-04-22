import operator
import random
seed = 400
mapping = {'easy': 1, 'medium': 2, 'hard': 3}

def process(filename):
    questions = []
    labels_1 = []
    labels_2 = []
    with open(filename, 'r') as file:
        file.readline()
        for line in file:
            tokens = line.split('\t')
            if tokens[1] == 'NULL':
                continue
            questions.append(tokens[1])
            labels_1.append(tokens[3])
            labels_2.append(tokens[4])

    sentence = []
    label = []
    print len(questions), len(labels_1), len(labels_2)
    for i in range(0, len(questions) - 1, 2):
        vote = {'too easy': 0, 'easy': 0, 'medium': 0, 'hard': 0, 'too hard': 0}
        sentence.append(questions[i])
        if labels_1[i] != '' and labels_1[i] != 'NULL':      
            vote[labels_1[i]] += 1
        if labels_1[i + 1] != '' and labels_1[i + 1] != 'NULL':      
            vote[labels_1[i + 1]] += 1
        if labels_2[i] != '' and labels_2[i] != 'NULL':      
            vote[labels_2[i]] += 1
        if labels_2[i + 1] != '' and labels_2[i + 1] != 'NULL':      
            vote[labels_2[i + 1]] += 1
        label.append((sorted(vote.items(), key=operator.itemgetter(1), reverse = True))[0][0])

    with open('difficulty.txt', 'w') as file1, open('difficulty_label.txt', 'w') as file2:
        for sen, la in zip(sentence, label):
            file1.write(sen + '\n')
            file2.write(la + '\n')

def split():
    with open('data/difficulty.txt', 'r') as file1, open('data/difficulty_label.txt', 'r') as file2:
        data1 = file1.read().split('\n')
        data2 = file2.read().split('\n')
    random.shuffle(data1)
    random.shuffle(data2)

    file1 = open('data/difficulty_train.txt', 'w')
    file2 = open('data/difficulty_test.txt', 'w')
    file3 = open('data/difficulty_label_train.txt', 'w')
    file4 = open('data/difficulty_label_test.txt', 'w')

    length =  int(len(data1) * 0.8)
    data_train = data1[:length]
    label_train = data2[:length]
    data_test = data1[length:]
    label_test = data2[length:]

    for data, label in zip(data_train, label_train):
        file1.write(data + '\n')
        file3.write(label + '\n')
    for data, label in zip(data_test, label_test):
        file2.write(data + '\n')
        file4.write(label + '\n')


split()
# process('question_answer_pairs.txt')


