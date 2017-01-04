from angular_flask import app

class Response_frame(object):

	def __init__(self):
		self.template = None # template name string
		self.data = None # should be [] 
		self.isCompleted = None # true or false
		self.context = None # set the context 
