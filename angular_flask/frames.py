from angular_flask import app

class Show_chart(object):

	def __init__(self):
		self.chart_type = None
		self.data = None
		self.x_axis = None
		self.y_axis = None

	def display_frame(self):
		print "printing show_chart frame"
		print "Chart Type : "+str(self.chart_type)
		print "Data : "+str(self.data)
		print "X-axis : "+str(self.x_axis)
		print "Y-axis : "+str(self.y_axis)

	def isAllFilled(self):
		if self.chart_type is None:
			return False
		if self.data is None:
			return False
		if self.x_axis is None:
			return False
		if self.y_axis is None:
			return False
		
		return True

class Get_jira(object):

	def __init__(self):
		self.project = "PROJECT"
		self.issue_status = None
		self.user = "USER"

	def display_frame(self):
		print "printing Get_jira frame"
		print "project : "+str(self.project)
		print "issue_status : "+str(self.issue_status)
		print "user : "+str(self.user)

	def isAllFilled(self):
		if self.project is None:
			return False
		if self.issue_status is None:
			return False
		if self.user is None:
			return False
		
		return True