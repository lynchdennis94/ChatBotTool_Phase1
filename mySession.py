import uuid
import time

class mySession:
    def __init__(self):
        self.session_id = None
        self.response = ""
        self.state = 'init'
        self.SessionTime = 120

    def StartSession(self):
        self.response = ""
        self.state = 'startDialog'
        self.session_id = str(uuid.uuid4())
        self.start_time = time.time()
        self.in_question_mode = True
        self.prev_intent = ""
        self.prev_response = ""

    def inValidSession(self):
        return (self.session_id == None)

    def GetSessionId(self):
        return self.session_id

    def isInQuestionMode(self):
        return self.in_question_mode

    def setInQuestionMode(self, input_question_mode):
        self.in_question_mode = input_question_mode

    def getPrevIntent(self):
        return self.prev_intent

    def setPrevIntent(self, input_prev_intent):
        self.prev_intent = input_prev_intent

    def getPrevResponse(self):
        return self.prev_response

    def setPrevResponse(self, input_prev_response):
        self.prev_response = input_prev_response

    def AddResponse(self,response):
        self.response = (response + '&#13;&#10;&#13;&#10;' + self.response)
        return self.response

    def ChangeState(self,newState):
        self.state = newState

    def stateDone(self):
        return (self.state == 'done')

    def elapsedTime(self):
        return time.time() - self.start_time

    def Timeout(self):
        return (self.state == 'init' or self.elapsedTime() > self.SessionTime)

    def TimeRemaining(self):
        return max((self.SessionTime - self.elapsedTime()), 0)
