import numpy as np
import operator
from ginger_python2 import get_grammar_error

# print get_grammar_error("Did Mary note by Luigi Galvani when two different metals were connected in series with the frog 's leg and to one another ?")
diversity_map = {'why': 5, 'how many': 1, 'how much': 1, 'what': -1}
percent_map = {'what': 1, 'when': 1, 'where': 1, 'who': 1, 'how many': 1, 'how much': 1, 'how': 1, 'why': 1, 'do': 1, 'are': 1, 'have': 1, 'did': 1, 'does': 1, 'were': 1, 'was': 1, 'is': 1, 'had': 1, 'has': 1}
zero_error = []

def get_complexity(questions):
    length_li = map(lambda x : len(x.split()), questions)
    length_li = map(lambda x : func(x), length_li)
    max_len, min_len = max(length_li), min(length_li)
    comlexity = map(lambda x : float(x - min_len) / (max_len - min_len), length_li)
    # print comlexity
    return np.asarray(comlexity)

def get_score(questions, N):
    questions = list(questions)
    tuple_list = map(lambda x : score_func(x), questions)
    hard_scores = map(lambda x : x[1], tuple_list)
    com_scores = map(lambda x : x[2], tuple_list)
    max_com, min_com = max(com_scores), min(com_scores)
    # max_hard = max(hard_scores)
    comlexity = map(lambda x : float(x - min_com) / (max_com - min_com), com_scores)
    scores = np.asarray(comlexity) + 0.5 * np.asarray(hard_scores)
    
    for tup, s in zip(tuple_list, scores):
        tup.append(s)

    sorted_list = sorted(tuple_list, key = operator.itemgetter(4), reverse = True)
    total_percent = sum(percent_map.values())
    for key in percent_map.keys():
        percent_map[key] = float(percent_map[key]) / float(total_percent) * N
    
    res = set()
    for ele in sorted_list:
        if ele[3] and percent_map[ele[3]] > 0:
            res.add(ele[0])
            percent_map[ele[3]] -= 1
            # print percent_map
            N -= 1
        if N == 0:
            break
    for ele in sorted_list:
        if ele[0] not in res:
            res.add(ele[0])
            N -= 1
        if N == 0:
            break
    return list(res)

def score_func(x):
    div_score = 0
    tokens = x.lower().split()
    leng = len(tokens)
    com_score = func(leng)
    hard_score = 1
    head = None
    if tokens[0] in percent_map or (tokens[0] + ' ' + tokens[1]) in percent_map:
        hard_score = 0
    for i in range(leng):
        if i < leng - 1 and (tokens[i] + ' ' + tokens[i + 1]) in percent_map:
            head = tokens[i] + ' ' + tokens[i + 1]
            break
        if tokens[i] in percent_map:
            head = tokens[i]
            break
    if not head:
        hard_score = 0
    return [x, hard_score, com_score, head]

def func(x):
    res = 0
    if x <= 5 or x >=30:
        res = -10
    elif x > 5 and x <= 20:
        res = 10
    elif x > 20:
        res = 5
    return res

def get_error(questions):
    # global N
    errors = []
    length = len(questions)
    for i in range(length):
        err = get_grammar_error(questions[i][:-1])
        if err == 0:
            zero_error.append(questions[i])
            # N -= 1
        errors.append(err)
    max_error = max(errors)
    if max_error == 0:
        return np.asarray(errors)
    return np.asarray(map(lambda x : float(x) / max_error, errors))

def diversity_helper(x):
    div_score = 0
    tokens = x.lower().split()
    # for key, val in diversity_map.iteritems():
    #     if key in tokens:
    #         div_score += val
    #     elif key  == 'how':
    #         pass
    leng = len(tokens)
    for i in range(leng):
        if i < leng - 1 and (tokens[i] + ' ' + tokens[i + 1]) in diversity_map:
            div_score += diversity_map[tokens[i] + ' ' + tokens[i + 1]]
            break
        if tokens[i] in diversity_map:
            div_score += diversity_map[tokens[i]]
            break

    return div_score

def get_diversity(questions):
    diversity = map(lambda x : diversity_helper(x), questions)
    max_diversity = max(diversity)
    min_diversity = min(diversity)
    # print diversity
    return np.asarray(diversity) - min_diversity / float(max_diversity - min_diversity)

def first_round(questions):
    questions = list(questions)
    scores = 0.3 * get_complexity(questions) + 0.3 * get_diversity(questions)
    res = {}
    for q, s in zip(questions, scores):
        res[q] = s
    sorted_res = sorted(res.items(), key = operator.itemgetter(1), reverse = True)
    return sorted_res[:100]

def second_round(filtered, N):
    questions = []
    scores = []
    for x in filtered:
        questions.append(x[0])
        scores.append(x[1])
    errors = get_error(questions)
    scores = np.asarray(scores) - 0.4 * errors
    res = {}
    for q, s in zip(questions, scores):
        res[q] = s
    sorted_res = sorted(res.items(), key = operator.itemgetter(1), reverse = True)
    return sorted_res[:N]

def ranking(questions, N):
    questions = []
    with open('ques1.txt', 'r') as file:
        for line in file:
            if line:
                questions.append(line.strip())
    # res = second_round(first_round(set(questions)), 20)
    res = get_score(questions, 50)


if __name__ == '__main__':
    main()
