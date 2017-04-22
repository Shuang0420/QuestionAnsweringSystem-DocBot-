'''
Read the question_
'''
import shutil
import os
import answer
from settings import verbose

S10_folder = "S10/"
out_folder = "S10/article/"


def generate_evaluation_files():
    '''
    For extracting the test data from S10 data.
    Only need to run it once. No need to run anymore.
    :return:
    '''
    # "ArticleTitle	Question	Answer	DifficultyFromQuestioner	DifficultyFromAnswerer	ArticleFile"
    # Alessandro_Volta	Was Alessandro Volta a professor of chemistry?	No	easy	hard	data/set4/a10

    with open(os.path.join(S10_folder, "question_answer_pairs.txt")) as infile:
        header = infile.readline()
        if verbose:
            print 'len:', len(header.split("\t")), 'header:', header
        lines = infile.readlines()
        data = [line.strip().split("\t") for line in lines if line.strip()]

        pre_ArticleTitle = ''
        pre_ArticleFile = ''
        questions = []
        answers = []
        for line in data:
            assert len(line) == 6
            cur_ArticleTitle, cur_Question, cur_Answer, cur_ArticleFile = line[0], line[1], line[2], line[-1]

            if not pre_ArticleTitle:
                pre_ArticleTitle = cur_ArticleTitle
                pre_ArticleFile = cur_ArticleFile

            if pre_ArticleTitle != cur_ArticleTitle and pre_ArticleTitle and pre_ArticleFile:
                # 1. write the article file
                old_file_path = os.path.join(S10_folder, pre_ArticleFile + '.txt')
                new_file_path = os.path.join(out_folder, pre_ArticleTitle + '.txt')
                shutil.copyfile(old_file_path, new_file_path)

                # 2. write question, answer file
                assert len(questions) == len(answers)
                question_file_path = os.path.join(out_folder, pre_ArticleTitle + '_question.txt')
                answer_file_path   = os.path.join(out_folder, pre_ArticleTitle + '_answer.txt')

                with open(question_file_path, 'w') as outfile:
                    outfile.write('\n'.join(questions))
                with open(answer_file_path, 'w') as outfile:
                    outfile.writelines('\n'.join(answers))

                # 4. clear out
                questions = []
                answers = []

            # update previsou pointer
            questions += [cur_Question]
            answers += [cur_Answer]
            pre_ArticleTitle = cur_ArticleTitle
            pre_ArticleFile = cur_ArticleFile




def test_answer():
    article_file_path = 'S10/article/Berlin.txt'
    question_file_path = 'ques1.txt'   # 'S10/article/Alessandro_Volta_question.txt'
    argv = ['', article_file_path, question_file_path]
    answer.main(argv)



if __name__ == '__main__':
    test_answer()









