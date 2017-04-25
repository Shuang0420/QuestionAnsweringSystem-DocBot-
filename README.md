# Question-Answering-System-DocBot-
Given a Wikipedia article, generate N "good" questions and answer N questions. See how we make it at https://www.youtube.com/watch?v=VWdR6ornHoc&feature=youtu.be

## Status

This is a semester-long project for CMU 11611. We have a team of 4 people. The original code is on https://github.com/hexiaoyuhaha/Wiki-Question-Answering-System. 

It can generate and answer yes-no questions and wh-questions like what/when/where/how/how many(much)/why.

I'm still working on it and trying to improve the performance.



## Requirements

- python==2.7


- spaCy==1.7.5
- pattern==2.6
- textblob==0.12.0
- nltk==3.2.2
- requests==2.13.0
- scipy==0.18.1
- sklearn==0.18.1
- numpy==1.11.3
- stanford-corenlp-full-2016-10-31  



## Repository contents

- stanford-corenlp-full-2016-10-31/:  I'm working on python wrapper now. Hopefully it will be released within 2 weeks.Currently, using the following command to run the server on port 3456, <pre>java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 3456 -timeout 15000</pre>

- S10/: contains sample wikipedia dataset

  article folder contains the sample articles, questions and answers 

  data folder contains only articles in htm, txt format

- data/: contains training data and model information for answer type detection

- .py files will be reorganized in the near future

  ​

## How to use

- install the stuff the requirement mentions, and run the stanford corenlp server on port 3456.
- <pre>./run-ask.sh filename nquestions</pre>
- <pre>./run-answer.sh filename questions</pre>