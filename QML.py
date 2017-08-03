# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 11:19:33 2017

@author: dmamartin
"""
import itertools
import os

#NUMBER_OF_RESPONSES = 5 # set this to a fixed number or 0 to use all options. 
#POSITIVE_REQUIRED = 0 # set this to 1 to require a positive response in each question
#NEGATIVE_REQUIRED = 0 # set this to 1 to require a negative resposne in each question
#MULTIPLE_FILES = 0 # set this to 1 to produce a file for each question
#USE_SUBTOPICS = 1 # set this to 1 to generate a subtopic for each question set, 0 to have all questions in the same topic.
#SCORING = -1 # set a fixed value for the bonus, or -1 for the number of responses - 1

#INPUTFILE = "inputfile.txt" # your filename must be spelled correctly and be between quotes. 
#OUTPUTFILE = "questions" # The .qml will be added. For multiple file output, this is the name of the directory into which
                         # which files will be saved. It will be created if it doesn't exist
    
## Do not change anything below this line.
def buildQuestions(INPUTFILE, OUTPUTFILE, NUMBER_OF_RESPONSES, POSITIVE_REQUIRED, NEGATIVE_REQUIRED, 
                   MULTIPLE_FILES, USE_SUBTOPICS, SCORING):
    Qstart = """ <?xml version="1.0" standalone="no"?>
<!DOCTYPE QML SYSTEM "QML_V3.dtd">

<QML>

"""
    Qend =  "</QML>\n"
    QuestionTemplate = """<QUESTION ID="{}" DESCRIPTION="{}" TOPIC="{}" STATUS="Normal">
  <CONTENT TYPE="text/html"><![CDATA[{}]]></CONTENT>
  <ANSWER QTYPE="MR" SHUFFLE="YES" SUBTYPE="VERT" MAXRESPONSE="{}">
{}
  </ANSWER>
{}
</QUESTION>
"""   

    ChoiceTemplate = """    <CHOICE ID="{}">
      <CONTENT TYPE="text/html"><![CDATA[{}]]></CONTENT>
    </CHOICE>
"""            
    OutcomesTemplate = """<OUTCOME ID="{}" ADD="{}" CONTINUE="TRUE">
    <CONDITION>{}</CONDITION>
    <CONTENT TYPE="text/html"><![CDATA[{}]]></CONTENT>
  </OUTCOME>
"""  

    try: 
        fh = open(INPUTFILE)
    except:
        print('Could not open input file {}'.format())
        return
    topicbase = fh.readline().strip()
    print('Reading questions for topic "{}"'.format(topicbase))
    outfile = OUTPUTFILE
    if MULTIPLE_FILES:
        os.makedirs(outfile, exist_ok=True)
    else:
        ofh = open('{}.qml'.format(outfile), 'w')
        print(Qstart, file=ofh)
        
    for line in fh.readlines():
        fields = line.strip().split('\t')
        if len(fields)<7:
            continue
        qdesc = fields[0]
        qprompt = fields[1]
        qfeedback = fields[2]
        responses = []
        for r in fields[3:]:        
            response = {'text': r[1:], 'not': '','fb':''}
            if r[0].lower() == 'f':
                response['not']='NOT'
            else:
                response['fb']='NOT'
            responses.append(response)
        tsize = NUMBER_OF_RESPONSES
        if tsize == 0:
            tsize = len(responses)
        if MULTIPLE_FILES:
            ofh = open('{}/{}.qml'.format(outfile,qdesc))
            print(Qstart, file=ofh)
        score = SCORING
        if score == -1:
            score = tsize-1
        qnum=0
        if USE_SUBTOPICS:
            topic = '{}\{}'.format(topicbase, qdesc)
        for t in itertools.combinations(responses, tsize):
            if POSITIVE_REQUIRED and len([x for x in t if x['not']==''] )==0:
                continue
            if NEGATIVE_REQUIRED and len([x for x in t if  x['not']=='NOT'] )==0:
                continue
            qnum = qnum + 1
            qid = 1234567891011121 + qnum
            topic = topicbase
            choices=[]
            outcomes=[]
            allright = []
            notright = []
            for i in range(tsize):
                choices.append(ChoiceTemplate.format(i,t[i]['text']))
                outcome = '{} "{}"'.format(t[i]['not'], i)
                allright.append(outcome)
                fb = "{} {} : Correct!".format(t[i]['not'],t[i]['text'])
                feedback = '{} "{}"'.format(t[i]['fb'], i)
                notright.append(feedback)
                outcomes.append(OutcomesTemplate.format(i, 1, outcome, fb))
            if score:
                outcomes.append(OutcomesTemplate.format('bonus', score, ' AND '.join(allright), "All correct!" ))
            outcomes.append(OutcomesTemplate.format('feedback', 0, ' OR '.join(notright), qfeedback ))
            
            print(QuestionTemplate.format(qid, "{}.{}".format(qdesc,qnum), topic,qprompt, tsize,
                                          "".join(choices), "".join(outcomes)), file=ofh)
        if MULTIPLE_FILES:
            print(Qend, file=ofh)
    if not MULTIPLE_FILES:
        print(Qend, file=ofh)
        