目前，where, when, who return NER, 

is, does, what, 剩下的其他都 return whole sentence.

## NER tag处理who不靠谱

```
----------
query: Who did Alessandro Volta marry?
qargs: did Alessandro Volta marri ?
expected_types: PERSON
 sentence:In 1794, Volta married Teresa Peregrini, with whom he raised three sons, Giovanni, Flaminio and Zanino.
NER token: [(u'DATE', u'1794'), (u'ORG', u'Volta'), (u'ORG', u'Teresa Peregrini'), (u'CARDINAL', u'three'), (u'PERSON', u'Giovanni'), (u'GPE', u'Flaminio'), (u'GPE', u'Zanino')]
==finalAnswer==   Giovanni
```

```
----------
query: Who made Volta a count?
qargs: made Volta a count ?
expected_types: PERSON
 sentence:In honor of his work, Volta was made a count by Napoleon in 1810.
NER token: [(u'ORG', u'Volta'), (u'ORG', u'Napoleon'), (u'DATE', u'1810')]
expected_types: PERSON
 sentence:The battery made by Volta is credited as the first electrochemical cell.
NER token: [(u'PERSON', u'Volta'), (u'ORDINAL', u'first')]
==finalAnswer==   Volta
```

活生生的把人名Teresa Peregrini, Napoleon, Volta 识别成了ORG我也是醉了。


## NER处理where

```
----------
query: Where was Volta born?
qargs: wa Volta born ?
expected_types: LOC
 sentence:Volta was born in Como, Italy and was taught in the public schools there.
NER token: [(u'GPE', u'Como'), (u'GPE', u'Italy')]
==finalAnswer==   Como
```
成功handle where


## NER处理when比较可靠

```
query: When did Volta retire?
qargs: did Volta retir ?
expected_types: DATE
 sentence:Volta retired in 1819 in his estate in Camnago, a frazione of Como now called Camnago Volta after him, where he died on March 5, 1827.
NER token: [(u'DATE', u'1819'), (u'GPE', u'Camnago'), (u'PERSON', u'Como'), (u'LOC', u'Camnago Volta'), (u'DATE', u'March 5, 1827')]
==finalAnswer==   1819
```
成功handle where




## Wasn't 句子回答
```
query: Wasn't Alessandro Volta born in Como?
qargs: ' t Alessandro Volta born in Como ?
expected_types: PERSON
 sentence:Volta was born in Como, Italy and was taught in the public schools there.
NER token: [(u'GPE', u'Como'), (u'GPE', u'Italy')]
expected_types: PERSON
 sentence:*  Count Alessandro Giuseppe Antonio Anastasio Volta: A Pioneer in Electrochemistry
NER token: [(u'PERSON', u'Count Alessandro'), (u'ORG', u'Pioneer')]
==finalAnswer==   Count Alessandro
```





## CARDINAL 目前归在other里面
以后最好归档用POS tagger处理cardinal

```
----------
query: How long was Alessandro Volta a professor at the University of Pavia?
qargs: long wa Alessandro Volta a professor at the Univers of Pavia ?
expected_types: CARDINAL
 sentence:In 1779 he became professor of experimental physics at the University of Pavia, a chair he occupied for almost 25 years.
NER token: [(u'DATE', u'1779'), (u'ORG', u'the University of Pavia'), (u'DATE', u'almost 25 years')]
expected_types: CARDINAL
 sentence:In 1774 he became a professor of physics at the Royal School in Como.
NER token: [(u'DATE', u'1774'), (u'ORG', u'the Royal School')]
expected_types: CARDINAL
 sentence:Count Alessandro Giuseppe Antonio Anastasio Volta (February 18, 1745 – March 5, 1827) was an Italian Giuliano Pancaldi, "Volta: Science and culture in the age of enlightenment", Princeton University Press, 2003.
NER token: [(u'PERSON', u'Count Alessandro'), (u'DATE', u'February 18, 1745 \u2013 March 5, 1827'), (u'NORP', u'Italian'), (u'PERSON', u'Giuliano Pancaldi'), (u'WORK_OF_ART', u'Volta: Science and'), (u'DATE', u'the age of enlightenment'), (u'ORG', u'Princeton University Press'), (u'DATE', u'2003')]
expected_types: CARDINAL
 sentence:Alberto Gigli Berzolari, "Volta's Teaching in Como and Pavia"- Nuova voltiana  physicist known especially for the development of the first electric cell in 1800.
NER token: [(u'PERSON', u'Alberto Gigli Berzolari'), (u'WORK_OF_ART', u"Volta's Teaching in Como"), (u'GPE', u'Pavia"- Nuova'), (u'ORDINAL', u'first'), (u'DATE', u'1800')]
expected_types: CARDINAL
 sentence:His promotion of it was so extensive that he is often credited with its invention, even though a machine operating in the same principle was described in 1762 by Swedish professor Johan Wilcke.
NER token: [(u'DATE', u'1762'), (u'NORP', u'Swedish'), (u'PERSON', u'Johan Wilcke')]
==finalAnswer==  
```
How long 的quetion 别判断成了 CARDINAL的类别。然而这个NER类别压根没有用啊


## Headword不是第一个词
```
query: A year before improving and popularizing the electrophorus, what did Volta become?
qargs: year befor improv and popular the electrophoru , what did Volta becom ?
expected_types: OTHER
 sentence:A year later, he improved and popularized the electrophorus, a device that produces a static electric charge.
==finalAnswer==   None
```







