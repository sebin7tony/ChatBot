from angular_flask import app
import frames,models

import logging
import json,os,csv

logger = logging.getLogger("controller.show_chart_processor")

FOLDER_LOCATION = "C:/_Kazeon/Analytics/chat/csv"
CSVFILE_LIST = None
CSVFILE_FIELD_MAPPING = None
CONTEXT = {}
variable_types = [
    # (Type, Test)
    (int, int),
    (float, float)
]

# this function will get the type of passed value
# @params : string
# @ returns : string
def getType(value):
    for typ, test in variable_types:
        try:
            test(value)
            return typ
        except ValueError:
            continue
    
    return 'str'


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


# function that will scan and extract all the csv files in a given direcory
# It will also parse the type of the values used in the csv.
# @params : string
# @returns : list,dict
#
def extract_csv_metadata(FOLDER_LOCATION):
    csvfile_list = []
    csvfile_field_mappings = {}
    for root, dirs, files in os.walk(FOLDER_LOCATION):
        for file in files:
            if file.endswith(".csv"):
                
                 with open(os.path.join(root, file), 'r') as csvfile:
                        csvreader = csv.reader(csvfile)
                        csv_titles = next(csvreader)
                        filename = file[:-4]
                        csvfile_list.append(filename)
                        csvfile_field_mappings[filename] = {}
                        csvfile_field_mappings[filename]["title"] = csv_titles
                        csvfile_field_mappings[filename]["types"] = {}
                        csv_values = next(csvreader)
                        for index,title in enumerate(csv_titles):
                            csvfile_field_mappings[filename]["types"][title] = getType(csv_values[index])
                        
    return csvfile_list,csvfile_field_mappings


# Extracting the csv data fields
CSVFILE_LIST,CSVFILE_FIELD_MAPPING = extract_csv_metadata(FOLDER_LOCATION)



# This function will create response needed for the UI to process
# @params : Show_chart
# @returns : Response_frame
def response_generator_showchart(showChart_frame):

    logger.info("Entering response_generator_showchart"+str(showChart_frame.__dict__))

    showChart_response = models.Response_frame()

    if showChart_frame.chart_type is None:
        logger.error("chart_type is not detected properly, cant process anymore")
        return
    if showChart_frame.data is None:
        logger.error("data is not detected properly, cant process anymore")
        return
    
    # x-axis and y-axis are not available
    # send the frame to get that
    if showChart_frame.x_axis is None and showChart_frame.y_axis is None:
        showChart_response.template = "graph-axis-selector.html"
        temp = {}
        temp['x'] = []
        temp['y'] = []
        if showChart_frame.data in CSVFILE_FIELD_MAPPING:
            for key in CSVFILE_FIELD_MAPPING[showChart_frame.data]['types']:
                if CSVFILE_FIELD_MAPPING[showChart_frame.data]['types'][key] == 'str':
                    temp['x'].append(key)
                else:
                    temp['y'].append(key)
        else:
            logger.error("Detected data is not present in the CSVFILE_FIELD_MAPPING")
            return

        newTmp = {}
        newTmp['text'] = "Ok. Got it. But i need more information on the data used with x axis and y axis. Please select appropriate fields from the " +str(showChart_frame.data) +"."
        newTmp['template_data'] = temp
        showChart_response.data = newTmp
        showChart_response.isCompleted = False
        
        tmp_context = {}
        tmp_context['frame_name'] = "Show_chart"
        tmp_context['frame'] = showChart_frame.__dict__
        showChart_response.context = tmp_context

        logger.info("Leaving response_generator_showchart "+str(showChart_response.__dict__))
        return showChart_response

    # all fields are filled and send the chart frame
    else:
        return None




# This function fills the frame that is used for show_chart intent
# @params : Show_chart ,spacy token,spacy token , string , string
# @returns : Response_frame
def fillFrame_show_chart(showChart_frame,obj_root,data_root,x_axis,y_axis):
    
    # find the type of chart #
    if showChart_frame.chart_type is None:
        if obj_root is not None:
            for child in obj_root.children:
                if child.dep_ == 'compound' and child.pos_ == 'NOUN':
                    showChart_frame.chart_type = str(child)
        else:
            # throw error 
            logger.error("obj_root is not passed properly, None object passed 1")
            return
        
        # finding the data_root if data_root is None #
        tmp_list = []
        if data_root is None and obj_root is not None:
            tmp_list = getlabeledToken(obj_root,'pobj',tmp_list)
            if len(tmp_list) == 1:
                data_root = tmp_list[0]
            else:
                # Error
                logger.error("Number of 'pobj' in the input text is not compatible")
                logger.error("Expecting only one 'pobj' in the input text")
                return
    
    if showChart_frame.data is None:
        if data_root is not None:
            tmp_list = []
            tmp_list = getlabeledToken(data_root,'compound',tmp_list)
            intent_data = data_root
            for tok in tmp_list:
                if tok.i < data_root.i:
                    intent_data = str(tok) +" "+ str(intent_data) 
            showChart_frame.data = intent_data 
        else:
            # throw error 
            logger.error("data_root is not passed properly, None object passed")
            return

    if x_axis is None and y_axis is None:
        logger.info("inside")
        return response_generator_showchart(showChart_frame)
    else:
        showChart_frame.x_axis = x_axis
        showChart_frame.y_axis = y_axis

    if showChart_frame.isAllFilled():
        # fire the graph
        return response_generator_showchart(showChart_frame)
    else:
        # something is wrong
        logger.error("Something has terribly gone wrong !!")
        logger.error("frame is not filled properly at the end of the function")
        return


# This function will accept the x and y axis fields and process
# the chart as requested in the text. 
# @params : string,string,dict
# @returns : Response_frame
def processChartAxis(x_axis,y_axis,context):

    logger.debug("Inside the processChartAxis")

    x_data = []
    y_data = []

    if x_axis is None or y_axis is None or context is None:
        logger.error("Parameters are not passed properly. None type encountered")
        return

    # Parse data from the csv file
    if 'frame' in context:
        file_name = context['frame']['data']
        file_name = file_name+'.csv'
        file_name = os.path.join(FOLDER_LOCATION, file_name)

        with open(file_name, 'rb') as csvfile:
            logger.debug("Reading the file successfully ")
            csvreader = csv.reader(csvfile)
            csv_titles = next(csvreader)
            csv_titles = [title.lower() for title in csv_titles]
            x_index = csv_titles.index(x_axis.lower())
            y_index = csv_titles.index(y_axis.lower())

            # Creating the data for the graph
            for row in csvreader:
                x_data.append(row[x_index])
                y_data.append(row[y_index])

    logger.debug("x_data "+str(x_data))
    logger.debug("y_data "+str(y_data))

    if not x_data or not y_data :
        logger.error("Something has gone wrong. CSV file did not got parsed properly")
        return
    else:
        chart_response = models.Response_frame()

        # fixing the template
        if context['frame']['chart_type'] == 'bar':
            chart_response.template = "bar-chart.html"
        elif context['frame']['chart_type'] == 'line':
            chart_response.template = "bar-chart.html"
        elif context['frame']['chart_type'] == 'spline':
            chart_response.template = "bar-chart.html"
        elif context['frame']['chart_type'] == 'pie':
            chart_response.template = "pie-chart.html"

        # fixing the chart data
        tmp = {}
        tmp['template_data'] = {}
        tmp['template_data']['x'] = x_data
        tmp['template_data']['y'] = y_data
        chart_response.data = tmp

        chart_response.isCompleted = True

        # set the context
        context['frame']['x_axis'] = x_axis
        context['frame']['y_axis'] = y_axis
        chart_response.context = context
        return chart_response
