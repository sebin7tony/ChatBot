from angular_flask import app
import frames,models
import show_chart_processor as chrt_proc
import jira_processor as jira_proc

import logging
import json

from nltk.corpus import wordnet as wn
import spacy
nlp = spacy.load('en')

logger = logging.getLogger("controller.data_explore")

training_verb_list = ['get.v.4','display.v.1','fetch.v.1','draw.v.3','show.v.5','see.v.1','plot.v.2','represent.v.9']
show_chart_verb_list = [verb for verb_input in training_verb_list for verb in wn.synset(verb_input).lemma_names()]
show_chart_noun_list = ['chart','graph']
jira_noun_list = ['bugs','issues']
dep_list = ['dobj','prep','xcomp']
verbs_special_cases = ['represent','depict','exhibit']


# get a list of tokens from children of a root token
# with given label
# @params : spacy Token, spacy Label, list
# @returns : list
def getlabeledToken(root,label,tokList):
    if root is None:
        return tokList
    if label is None:
        print "Pass valid label"
        return tokList
    
    if root.dep_ == label:
        tokList.append(root)
    
    for child in root.children:
        tokList = getlabeledToken(child,label,tokList)
    return tokList


# This extracts the intent object root token, intent verb 
# and intent data root token if available.
# @params : spacy token
# @returns : spacy token,spacy token,spacy token
def extract_intent_obj(root):
    intent_obj_root = None
    intent_data_root = None
    intent_verb = root
    isPrep = False
    for child in root.children:
        if child.dep_ in dep_list:
            if child.dep_ == 'xcomp' and 'VERB' in child.pos_ :
                intent_obj_root,intent_data_root,intent_verb = extract_intent_obj(child)
                intent_verb = child
            elif child.dep_ == 'prep':
                intent_data_root = intent_obj_root
                intent_obj_root = [chil for chil in child.children][-1]
                isPrep = True
            elif isPrep and child.dep_ == 'dobj':
                intent_data_root = child
            elif not isPrep and child.dep_ == 'dobj':
                intent_obj_root = child
                
    return intent_obj_root,intent_data_root,intent_verb


# This function gives you what kind of intent the chat text holding.
# this will return various intent types from the text.
# @params : string
# @returns : Response_frame
def text_parser(text):
    show_chart_response = None
    parsed_input_text = nlp(unicode(text))
    sentences = list(parsed_input_text.sents)
    # finding the root of the given text. 
    # Assumes there is only one sentence
    root = sentences[0].root
    intent_obj_root,intent_data_root,intent_verb = extract_intent_obj(root)
    
    if str(intent_verb).lower() in verbs_special_cases:
        # Handling special verbs
        text = text.replace(str(intent_verb),'display')
        return text_parser(text)

    elif str(intent_verb).lower() in show_chart_verb_list and str(intent_obj_root).lower() in show_chart_noun_list:
        # Trigger show_chart intent
        logger.debug("show_chart Intent identified !!")
        logger.debug("Intent verb "+str(intent_verb).lower())
        logger.debug("Intent obj root "+str(intent_obj_root).lower())
        logger.debug("Intent data root "+str(intent_data_root).lower())

        showChart_frame = frames.Show_chart()
        show_chart_response = chrt_proc.fillFrame_show_chart(showChart_frame,intent_obj_root,intent_data_root,None,None)
        # Response here always will be asking about the axis info
        logger.debug("leaving  text_parser t"+str(show_chart_response.__dict__).lower())
        logger.debug(show_chart_response)
        return show_chart_response

    elif str(intent_verb).lower() in show_chart_verb_list and str(intent_obj_root).lower() in jira_noun_list:
        # Trigger get_jira intent
        logger.debug("get_jira Intent identified !!")
        logger.debug("Intent verb "+str(intent_verb).lower())
        logger.debug("Intent obj root "+str(intent_obj_root).lower())

        getJira_frame = frames.Get_jira(intent_obj_root)
        show_jira_response = jira_proc.fillFrame_jira(getJira_frame,intent_obj_root)
        # Response here always will be asking about the axis info
        logger.debug("leaving  text_parser t"+str(show_chart_response.__dict__).lower())
        logger.debug(show_chart_response)
        return show_chart_response
    else:
    	# Nothing got triggered
        logger.info("Nothing got triggered !!")
        return None


