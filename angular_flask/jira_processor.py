
from angular_flask import app
import frames,models

import logging
import json,os,csv
import requests
import base64

logger = logging.getLogger("controller.jira_processor")
JIRA_ADDR = ''

jira_session = requests.session()

# This function login to jira
# Access Global varibale jira_session
def login_jira():
	try:
		jira_session.post(JIRA_ADDR, auth=('user', 'pass'), verify=False)
	except:
		logger.error('Unable to connect or authenticate with JIRA server.')


# This function gets the jira data by
# contacting the jira server
# @params : a valid jira rest api
# @params : dict
def get_jira_data(issue_status):
	# Prepare URL for jira rest
	url = JIRA_ADDR + "/rest/api/latest/search?"
	url = url + "jql=project%20IN%20(KZN)%20AND%20status%20in%20("+issue_status+")&maxResults=6"
	logger.debug('url for JIRA : '+url)
	print('url for JIRA : '+url)

	login_jira()
	results = jira_session.get(url)
	jira_data = results.json()

	bugs = []
	for data in jira_data['issues']:
		bug = {}
		bug['key'] = data['key']
		bug['link'] = JIRA_ADDR+"/browse/"+data['key']
		bug['summary'] = data['fields']['summary']
		bug['assignee'] = data['fields']['assignee']['displayName']
		bugs.append(bug)

	return bugs


# This function will create the response needed for the Get_jira intent
# @params : Get_jira frame
# @returns : Response_frame 
def response_generator_jira(getJira_frame):
	
	if not getJira_frame.isAllFilled:
		logger.error("Passed parameter does not qualify for response generation")
		return

	jira_response = models.Response_frame()	
	jira_response.template = "jira-tiles.html"
	tmp = {}
	tmp["text"] = "These are the top "+getJira_frame.issue_status+" jira issues that i found. Click on it for details"
	tmp["template_data"] = get_jira_data(getJira_frame.issue_status)
	jira_response.data = tmp
	jira_response.isCompleted = True
	jira_response.context = getJira_frame.__dict__

	return jira_response

 
# This function will fill the Get_jira frame
# @params : Get_jira, Spacy Token
# @returns : Response_frame
def fillFrame_jira(getJira_frame,intent_obj_root):
	
	if intent_obj_root is None:
		logger.error("intent_obj_root is None. Something went wrong")
		return

	for child in intent_obj_root.children:
		if child.dep_ == 'amod':
			getJira_frame.issue_status = str(child)
			break

	if getJira_frame.isAllFilled:
		return response_generator_jira(getJira_frame)
	else:
		logger.error("getJira_frame is not filled fully. Something went wrong")
		return


if __name__ == '__main__':
	k = get_jira_data('Submitted')
	print k