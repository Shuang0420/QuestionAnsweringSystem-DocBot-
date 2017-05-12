from __future__ import division, unicode_literals
import nltk
from nltk.parse.stanford import StanfordParser
import requests
from pattern.en import conjugate, lemma, tag
import re
import sys
from Article import Article
import spacy
from nltk.tokenize import sent_tokenize
import logging
from collections import defaultdict
import random
import copy
import question_evaluator

nlp = spacy.load('en')

reload(sys)
sys.setdefaultencoding('utf-8')

VERBOSE = False
# initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


APPO = "APPOSITION"
VM = "VERB_MODIFIER"
NV = "NP_VP"
APPOSITION = "NP !< CC !< CONJP < (NP=np1 $.. (/,/ $.. (NP=app $.. /,/)))"
VERB_MODIFIER = "NP=noun > NP $.. VP=modifier"
#NP_VP = "S < (NP=np $.. VP=vp)"
#MAIN_VERB = "S=clause < (VP=main_vp < /VB.?/=tensed !< (VP < /VB.?/))"
#POST_RULE = "S < (NP=np $.. (VP=vp < /VB.?/=tensed))"
NP_VP = "S < (NP=np ?$PP=pp1 $.. (VP=vp < (/VB.?/=tensed ?$.. PP=pp2 ?$.. SBAR=reason)))"
#NP_VP = "S < (NP=np $.. (VP=vp < (/VB.?/=tensed)))"
patterns = [(NV, NP_VP)]
'''
Ignore VBG and VBN, since we have processed it in auxiliary checking.
VBG	Verb, gerund or present participle
VBN	Verb, past participle
add VB to avoid any exceptions
'''
verb_tense_dict = {"VBD": "past", "VBG":"past", "VBN":"past", "VBP": "1sg", "VBZ": "3sg", "VB": "3sg"}

"""
Remaining work:
- coreference resolution
stanford pos treebank
https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
"""

ques_pool = set()
noun_plu_set = set(['people'])
noun_sing_set = set(['Mary'])

def getTregexResult(text, pattern):
    url = "http://localhost:3456/tregex"
    #request_params = {"pattern": "NP=np < (NP=np1 $.. (/,/ $.. NP=app))"}
    request_params = {"pattern": pattern}
    r = requests.post(url, data=text, params=request_params)
    try:
        js = r.json()
        if js['sentences'][0]:
            # currently, only returns one possible match
            return js['sentences'][0]
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        #print 'Decoding JSON has failed'
        return None


def getSimpleSentence(text, pattern, TYPE):
    """
    return simplified sentence
    :param text: original sentence
    :param pattern: rule of simplification
    :param TYPE: pattern type
    :return: string
    """
    js = getTregexResult(text, pattern)
    if not js:
        return None
    # if TYPE == APPO:
    #     main_verb = get_main_verb_tag(text)
    #     return getAppoSimpleSent(js, main_verb)
    # elif TYPE == VM:
    #     main_verb = get_main_verb_tag(text)
    #     return getVerbModSimpleSent(js, main_verb)
    # else:
    ques = []
    for k,v in js.iteritems():
        generateSimpleQues(v)




def generateSimpleQues(js):
    if 'namedNodes' in js:
        js = js['namedNodes']
    # parse result
    np, vp, tensed_verb, pp1, pp2, reason = {},{},{},{},{},{}
    res = defaultdict(str)
    for r in js:
        logger.debug('R %s' % r)
        if 'np' in r:
            np = r['np']
        if 'vp' in r:
            vp = r['vp']
        if 'tensed'  in r:
            tensed_verb = r['tensed']
        if 'pp1' in r:
            pp1 = r['pp1']
        if 'pp2' in r:
            pp2 = r['pp2']
        if 'reason' in r:
            reason = r['reason']
    # optional
    if pp1:
        pp1 = get_words_and_tags(pp1)
        pp1 = ' '.join(pp1)
        # first letter should be lower case
        pp1 = pp1[0].lower() + pp1[1:]
    else:
        pp1 = ''
    res['pp1'] = pp1
    # it's possible to handle direct object, but cannot handle indirect object
    inf_pp, inf_pp_left = '',''
    if pp2:
        pp2 = get_words_and_tags(pp2)
        res['pp2'] = pp2
        # # check infinitive, if is, the PP tag should appear before VB.? tag in the vp tree
        # pp_index = vp.find('PP')
        # np_index = vp.find('NP')
        # if pp_index > -1 and pp_index < np_index:
        #     inf_pp_index = pp2.index('\n')
        #     inf_pp = ''
        #     if inf_pp_index > -1:
        #         inf_pp = get_words_and_tags(pp2[:inf_pp_index])
        #         inf_pp = ' '.join(inf_pp)
        #         res['inf_pp'] = inf_pp
        #     inf_pp_left = get_words_and_tags(pp2[inf_pp_index:])
        #     inf_pp_left = ' '.join(inf_pp_left)
        #     res['inf_pp_left'] = inf_pp_left
    if reason:
        reason = get_words_and_tags(reason)
        res['reason'] = reason
    if not np or not vp:
        return

    # get head_verb and its tag
    head_verb, head_verb_tag = get_words_and_tags(tensed_verb, TAG=True)
    if not head_verb or  not head_verb_tag:
        return
    head_verb, head_verb_tag = head_verb[0], head_verb_tag[0]
    np, np_tags = get_words_and_tags(np, TAG=True)
    vp, vp_tags = get_words_and_tags(vp, TAG=True)
    if len(np_tags) < 2:
        return
    head_noun_tag = np_tags[1]
    if head_noun_tag != 'NNP':
        np[0] = np[0].lower()
    # generate binary questions and wh questions
    res['head_verb'] = head_verb
    res['head_verb_tag'] = head_verb_tag
    res['head_noun_tag'] = head_noun_tag
    res['np'] = np
    res['vp'] = vp
    res['vp_tags'] = vp_tags
    res['simpleSent'] = ' '.join([' '.join(np), ' '.join(vp), pp1])
    logger.debug('-'*100)
    logger.debug('SIMPLE SENT %s JSON %s' % (res['simpleSent'], str(js)))
    #generateQues(res)
    generate_question(res)



def ques_word_from_subject(np, doc):
    """
    Returns question_word, contains pron
    """
    logger.debug('FROM SUBJECT')
    logger.debug('*'*100)
    logger.debug('NP %s' % np)
    logger.debug('DOC %s' % doc)
    logger.debug('NER %s' % ' '.join([ne.text + '\t' + ne.label_ for ne in doc.ents]))
    np_len = len(np)
    has_ner = False
    # if subject contains PRON, do not do coreference resolution, only generates wh question
    subj_pron = False
    qw_res = []
    is_plural = False
    how_many_index = -1
    for word in doc[:np_len]:
        if word.pos_ == 'PRON':
            subj_pron = True
            break
    for index, word in enumerate(doc[:np_len]):
        logger.debug('WORD %s \t TAG %s POS \t %s' % (word, word.tag_, word.pos_))
        if word.tag_.startswith('PRP') and is_possessive(word):
            qw_res.append('whose ' + ' '.join(np[index + 1:]))
        if word.pos_.startswith('NUM') and word.ent_type_ != 'DATE':
            how_many_index = index
        if word.ent_type:
            has_ner = True
        if word.tag_.endswith('S'):
            is_plural = True
    # how many question with % fixed
    if how_many_index > -1 and len(np)>how_many_index+1:
        if np[how_many_index+1] == '%':
            qw = 'how many percent '
            if len(np) > how_many_index + 2:
                qw_res.append(qw + ' '.join(np[how_many_index + 2:]))
        elif np[how_many_index].endswith('%'):
            qw = 'how many percent '
            qw_res.append(qw + ' '.join(np[how_many_index + 1:]))
        else:
            qw = 'how many ' if is_plural else 'how much '
            qw_res.append(qw + ' '.join(np[how_many_index + 1:]))
    if has_ner:
        np_doc = nlp(' '.join(np))
        for ne in np_doc.ents:
            logger.debug('ne label %s \t %s ' % (ne.label_, ne.text))
            if not ne.label:
                continue
            if ne.label_ == 'PERSON':
                qw_res.append('who')
    # should be what even if the ner is LOCATION or DATA since this is a NP instead of PP
    # but actually if the ner is GPE, the best question word should be which country/city/state, but it's hard to decide which one to choose
    qw_res.append('what')
    nouns = ' '.join(np)
    if not subj_pron and nouns != '%':
        noun_plu_set.add(nouns.lower()) if is_plural else noun_sing_set.add(nouns.lower())
    return qw_res, subj_pron


HEAD_WORD_FOR_WHY = ['because', 'since', 'as']
def ques_word_from_object(np, vp, doc, reason, simpleSent):
    logger.debug('='*100)
    logger.debug('NP %s' % np)
    logger.debug('VP %s' % vp)
    logger.debug('DOC %s' % doc)
    logger.debug('NER %s' % ' '.join([ne.text + '\t' + ne.label_ for ne in doc.ents]))
    has_why, has_ner = False, False
    verb_break, noun_break = False, False
    plural_noun = False
    verbs = ''
    verbs_no_adp = ''
    first_noun_ending_index = -1
    qw_res = []
    # if contains SBAR, then discard this part to avoid weird questions
    if reason and reason[0] in HEAD_WORD_FOR_WHY:
        has_why = True
        vp = vp[:len(vp)-len(reason)]
    np_len = len(np)
    vp_len = len(vp)
    for index, word in enumerate(doc[np_len:np_len+vp_len+1]):
        logger.debug('WORD %s \t TAG %s POS \t %s NER \t %s' % (word, word.tag_, word.pos_, word.ent_type_))
        if not verb_break:
            if word.pos_ in ['VERB', 'ADP'] and index > 0:
                verbs += word.text + ' '
                if word.pos_ == 'VERB': verbs_no_adp += word.text + ' '
            elif index > 0:
                verb_break = True
        if word.pos_ == 'NOUN':
            if not noun_break: first_noun_ending_index = index
            noun_break = True
        if word.tag_.startswith('PRP') and is_possessive(word):
            nouns = ''
            for word in doc[np_len+index+1:vp_len+1]:
                nouns += word.text +' '
                if word.pos_ == 'NOUN':
                    qw_res.append(('whose ' + nouns.strip(), verbs.strip()))
        if word.pos_.startswith('NUM') and word.ent_type_ != 'DATE':
            nouns = ''
            if len(doc) > np_len+index+1 and doc[np_len+index+1].pos_ == 'NOUN': # avoid phrases like one or more fertile females
                for tmpword in doc[np_len+index+1:]:
                    nouns += tmpword.text +' '
                    if tmpword.pos_ == 'NOUN':
                        # add to noun_set
                        nouns = nouns.strip()
                        if tmpword.tag_.endswith('S'):
                            noun_plu_set.add(nouns.lower())
                            plural_noun = True
                        else:
                            noun_sing_set.add(nouns.lower())
                        break
                if nouns.startswith('km/') or nouns.startswith('m/') or nouns.startswith('mph'):
                    qw = 'how fast '
                    ques = simpleSent.replace(word.text, qw, 1)
                    ques = ques.replace(nouns.split(' ')[0],'',1)
                    nouns = ' '.join(nouns.split(' ')[1:])
                    qw_res.append(('how fast ' + nouns.strip(), verbs.strip()))
                else:
                    if nouns.startswith('%'):
                        qw = 'how many percent'
                        ques = simpleSent.replace(word.text + ' %', qw, 1)
                        # % is treated as noun, don't generate question like How many percent does the cat eat ?
                        # nouns = nouns.replace('%', '', 1)
                        # qw_res.append(('how many percent ' + nouns.strip(), verbs.strip()))
                    elif word.text.endswith('%'):
                        qw = 'how many percent '
                        ques = simpleSent.replace(word.text, qw, 1)
                    else:
                        qw = 'how many ' if plural_noun else 'how much '
                        qw_res.append((qw + nouns.strip(), verbs.strip()))
                        ques = simpleSent.replace(word.text, qw, 1)
                qw_res.append((False, ques))

        if word.ent_type:
            has_ner = True
    # if contains named entities, generate who/when/where question
    if has_ner:
        vp_doc = nlp(' '.join(vp))
        for ne in vp_doc.ents:
            logger.debug('ne label %s \t %s ' % (ne.label_, ne.text))
            if not ne.label:
                continue
            if ne.label_ == 'PERSON':
                # add to noun_set
                noun_sing_set.add(ne.text)
                qw_res.append(('who', verbs.strip()))
            if ne.label_ in ['LOC', 'GPE']:
                qw_res.append(('where', verbs_no_adp.strip())) # should be what since it is a NP instead of PP
            if ne.label_ in ['DATE', 'TIME']:
                qw_res.append(('when', verbs_no_adp.strip()))
        if has_why:
            qw_res.append(('why', verbs.strip()))
    # always generate what question
    if first_noun_ending_index > 0:
        verbs += ' '.join(vp[first_noun_ending_index+1:])
        qw_res.append(('what', verbs.strip()))
    return qw_res



def ques_word_from_pp1(pp):
    doc = nlp(pp)
    for ne in doc.ents:
        logger.debug('ne label %s \t %s ' % (ne.label_, ne.text))
        if not ne.label:
            continue
        if ne.label_ == 'PERSON':
            # add to noun_set
            noun_sing_set.add(ne.text)
            return 'who'
        if ne.label_ in ['LOC', 'GPE']:
            return 'where' # should be what since it is a NP instead of PP
        if ne.label_ in ['DATE', 'TIME']:
            return 'when'



HEAD_WORD_FOR_HOW = ['using', 'by', 'through', 'with', 'via']
def ques_word_from_pp2(pp2, vp):
    if pp2[0] in HEAD_WORD_FOR_HOW:
        vp = vp[:(len(vp)-len(pp2))]
        return 'how', vp
    return None, None




def generate_question(res):
    simpleSent, np, vp, vp_tags, pp1, pp2, head_verb, head_verb_tag, head_noun_tag, reason = res['simpleSent'], res['np'], res['vp'], res['vp_tags'], res['pp1'], res['pp2'],res['head_verb'],res['head_verb_tag'], res['head_noun_tag'], res['reason']
    doc = nlp(simpleSent)
    # generate question where question word is from subject
    qw_res, subj_pron = ques_word_from_subject(np, doc)
    if subj_pron:
        return
    for ques_word in qw_res:
        main_parts = wh_sub_question_part(res)
        ques = ' '.join([ques_word, main_parts])
        ques = post_process(ques)
        ques_pool.add(ques)
        if VERBOSE:
            #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
            logger.info('NP VP(subject)\t%s' % ques)
    # wh question from pp1
    if pp1:
        ques_word = ques_word_from_pp1(pp1)
        if ques_word:
            main_parts = binary_question_part(res, PP_FLAG=False)
            ques = ' '.join([ques_word, main_parts])
            ques = post_process(ques)
            ques_pool.add(ques)
            if VERBOSE:
                #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
                logger.info('NP VP(pp1)\t%s' % ques)
    # wh question from vp
    qw_res = ques_word_from_object(np, vp, doc, reason, simpleSent)
    for ques_word, verbs in qw_res:
        if ques_word == False:
            ques = post_process(verbs)
            ques_pool.add(ques)
            if VERBOSE:
                #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
                logger.info('NP VP(object HARD)\t%s' % ques)
            continue
        elif ques_word == 'why':# generate why question
            new_res = copy.deepcopy(res)
            new_res['vp'] = vp[:len(vp)-len(reason)]
            main_parts = wh_obj_question_part(new_res, verbs)
        else:
            main_parts = wh_obj_question_part(res, verbs)
        ques = ' '.join([ques_word, main_parts])
        ques = post_process(ques)
        ques_pool.add(ques)
        if VERBOSE:
            #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
            logger.info('NP VP(object)\t%s' % ques)
    # how question from pp2
    if pp2:
        ques_word, verbs = ques_word_from_pp2(pp2, vp)
        if ques_word:
            new_res = copy.deepcopy(res)
            new_res['vp'] = verbs
            main_parts = binary_question_part(new_res)
            ques = ' '.join([ques_word, main_parts])
            ques = post_process(ques)
            ques_pool.add(ques)
            if VERBOSE:
                #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
                logger.info('NP VP(pp2)\t%s' % ques)
    # yes-no question
    if not subj_pron:
        # make yes question
        main_parts = binary_question_part(res)
        ques = post_process(main_parts)
        ques_pool.add(ques)
        if VERBOSE:
            #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
            logger.info('NP VP(yes)\t%s' % ques)
        # make no question
        np_doc = nlp(' '.join(np))
        is_plural = False
        for n in np_doc:
            if n.tag_.endswith('S'):
                is_plural = True
        if is_plural and noun_plu_set:
            new_res = copy.deepcopy(res)
            new_np = random.sample(noun_plu_set, 1)
            new_res['np'] = new_np
            main_parts = binary_question_part(new_res)
            ques = post_process(main_parts)
            ques_pool.add(ques)
            if VERBOSE:
                #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
                logger.info('NP VP(no)\t%s' % ques)
        elif not is_plural and noun_sing_set:
            new_res = copy.deepcopy(res)
            new_np = random.sample(noun_sing_set, 1)
            new_res['np'] = new_np
            main_parts = binary_question_part(new_res)
            ques = post_process(main_parts)
            ques_pool.add(ques)
            if VERBOSE:
                #logger.info('\t%s \t \t%s \t \t%s' % (simpleSent, np, vp))
                logger.info('NP VP(no)\t%s' % ques)


def binary_question_part(res, PP_FLAG=True):
    simpleSent, np, vp, vp_tags, pp1, head_verb, head_verb_tag, head_noun_tag = res['simpleSent'], res['np'], res['vp'], res['vp_tags'], res['pp1'], res['head_verb'],res['head_verb_tag'], res['head_noun_tag']
    has_aux = has_auxiliary(head_verb, head_verb_tag, vp_tags)
    if has_aux:
        if PP_FLAG:
            return ' '.join([head_verb, ' '.join(np), ' '.join(vp[1:]), pp1])
        else:
            return ' '.join([head_verb, ' '.join(np), ' '.join(vp[1:])])
    else:
        do, verb = decompose_verb(head_verb, head_verb_tag)
        if PP_FLAG:
            return ' '.join([do, ' '.join(np), verb, ' '.join(vp[1:]), pp1])
        else:
            return ' '.join([do, ' '.join(np), verb, ' '.join(vp[1:])])


def wh_sub_question_part(res):
    simpleSent, np, vp, vp_tags, pp1, head_verb, head_verb_tag, head_noun_tag = res['simpleSent'], res['np'], res['vp'], res['vp_tags'], res['pp1'], res['head_verb'],res['head_verb_tag'], res['head_noun_tag']
    has_aux = has_auxiliary(head_verb, head_verb_tag, vp_tags)
    if has_aux:
        return ' '.join([head_verb, ' '.join(vp[1:]), pp1])
    else:
        #do, vp[0] = decompose_verb(head_verb, head_verb_tag)
        return ' '.join([' '.join(vp), pp1])

def wh_obj_question_part(res, verbs):
    simpleSent, np, vp, vp_tags, pp1, head_verb, head_verb_tag, head_noun_tag = res['simpleSent'], res['np'], res['vp'], res['vp_tags'], res['pp1'], res['head_verb'],res['head_verb_tag'], res['head_noun_tag']
    has_aux = has_auxiliary(head_verb, head_verb_tag, vp_tags)
    if has_aux:
        return ' '.join([head_verb, ' '.join(np), verbs, pp1])
    else:
        do, head_verb = decompose_verb(head_verb, head_verb_tag)
        return ' '.join([do, ' '.join(np), head_verb, verbs, pp1])




def post_process(ques):
    ques = re.sub(' +',' ',ques) + '?'
    ques = ques[0].capitalize() + ques[1:]
    ques = re.sub('-LRB- ', '', ques, flags=re.IGNORECASE)
    ques = re.sub(' *-RRB-', '', ques, flags=re.IGNORECASE)
    ques = re.sub('`` ', '"', ques)
    ques = re.sub(" ''", '"', ques)
    return ques


# check if plural
def is_plural(tag):
    if not tag:
        return False
    return tag.endswith('S')

# check if possessive pronoun
def is_possessive(word):
    return word.text in ['his', 'her', 'their']

ADV_STOP_LIST = ['almost', 'also', 'further', 'generally', 'greatly','however', 'just', 'later', 'longer', 'often', 'only', 'typically']
ADV_LIST = ['by', 'via', 'through']
def is_how(word):
    return word in ADV_LIST

# check if contains auxiliary
def has_auxiliary(head_verb, head_verb_tag, vp_tags):
    if head_verb_tag=='MD' or lemma(head_verb) in ['be','do']:
        return True
    if lemma(head_verb) in ['have'] and len(vp_tags) > 2 and vp_tags[2].startswith('V'):
        return True
    return False


def decompose_verb(verb, verb_tag):
    logger.debug('verb \t %s verb_tag \t %s' % (verb, verb_tag))
    tense = verb_tense_dict[verb_tag]
    return conjugate('do', tense), lemma(verb)


def get_words_and_tags(tree, TAG=False):
    """
    Return (words, tags) if TAG is True else False
    """
    if TAG:
        return (re.findall(r'(?<= )?[^( )]+(?=\))', tree), re.findall(r'(?<=\()\w+(?= )',tree))
    else:
        return re.findall(r'(?<= )?[^( )]+(?=\))', tree)





def ask(farticle, nquestions):
    article = Article(farticle)
    sentences = article.getRawLines()
    if VERBOSE:
        logger.debug('sentences\t%slen%d' % (sentences[0],len(sentences)))
    #sentences = ['The car drives 100km/h']
    #sentences = ['The electrolyte exists in the form 2H +  and SO 4  2- .']
    #sentences = ['The positively charged hydrogen bubbles start depositing around the copper and take away some of its electrons.']
    #sentences = ['Caat is the electromotive force -LRB- emf -RRB- of a galvanic cell between their two electrode potentials.']
    #sentences = ['10 fishes are dying']
    #sentences = ['The word ant is derived from ante of Middle English which is derived from mette of Old English and is related to the Old High German meiza , hence the modern German Ameise.']
    #sentences = ['London is a big city in the United Kingdom.']
    #sentences = ['Ants are social insects of the family Formicidae ( ), and along with the related wasps and bees, they belong to the order Hymenoptera.']
    #sentences = ['More than 12,500 species are classified with upper estimates of about 22,000 species']
    #sentences = ['10 white ducks are swimming in the water.']
    #sentences = ['Mary saw white ducks swimming in the water.']
    #sentences = ['In 1990, 5 valuable pandas were born in Beijing, China']
    #sentences = ['Mary was born in 1990.']
    #sentences = ['Nearly all ant colonies also have some fertile males called "drones" and one or more fertile females called "queens".']
    #sentences = ['The colonies are sometimes described as superorganisms because the ants appear to operate as a unified entity, collectively working together to support ']
    #sentences = ['The colonies sometimes are described as superorganisms because the ants appear to operate as a unified entity , collectively working together to support the colony.']
    #sentences = ['In the early 1990s, the video game SimAnt, which simulated an ant colony, won the 1992 Codie award for "Best Simulation Program".']
    #sentences = ['The team wins the game because they cheated']
    #sentences = ['In China, Mary was born in 1990.']
    # ignore super long sentences (more than 50 words)
    sentences = [s.strip() for s in sentences if s.count(' ') < 50]
    #sentences = ['Dempsey was born in Nacogdoches, Texas, and, for much of his childhood, his family lived in a trailer park, where he and his siblings grew up playing soccer with Hispanic immigrants. ']
    for sent in sentences:
        sent = sent.encode('ascii', 'ignore').decode('ascii')
        sent = re.sub(u'\(.*\) ','', sent)
        # simplify sentence
        for (TYPE, pattern) in patterns:
            #print 'sent \t%s pattern \t%s TYPE \t%s' % (sent, pattern, TYPE)
            getSimpleSentence(sent, pattern, TYPE)
    rankedQues = question_evaluator.get_score(ques_pool, nquestions)
    for q in rankedQues:
        print q
    #print 'total ques', len(ques_pool)




farticle = sys.argv[1]
nquestions = int(sys.argv[2])
if len(sys.argv)<3:
    print 'Usage: ./ask.py article.txt nqeustions'
ask(farticle, nquestions)



'''
#text = 'Harry Potter, a young boy, is very famous in US'
text = 'Harry Potter is very famous in US'
#text = 'You must eat'
testTree = Helper.getParserTree(text)
#res = getAppositions(testTree)
print 'test tree',testTree
generateNP_VP_ques(testTree)

res = getNP_VPs(testTree)
print 'result',res
# print one by one
if res:
    for c in res:
        print c
'''
