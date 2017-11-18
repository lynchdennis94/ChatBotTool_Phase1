# https://stackoverflow.com/questions/37345215/retrieve-text-from-textarea-in-flask

import os
import json
import myWit
import myLUIS
import myAPI
import convAPI
import mySession
from flask import Flask, request, send_from_directory, make_response
from pymongo import MongoClient

# NLU testing page
NLUhtmlHeader = '<center><h1>Eric Gregori OMSCS Advisor NLU Testing - egregori3@gatech.edu<br>Ask me about OMSCS admissions or curriculum</h1></center><br>'
NLUformTest = '<center><form action="nlusubmit" id="textform" method="post"><textarea name="text" cols="40"></textarea><input type="submit" value="Submit"></form></center>'
NLUhtmlWitRespStart = '<h2>Wit.ai response<br><textarea cols="40" rows="10">'
NLUhtmlWitRespEnd   = '</textarea>'
NLUhtmlLUISRespStart = '<h2>LUIS response<br><textarea cols="40" rows="10">'
NLUhtmlLUISRespEnd   = '</textarea>'
NLUhtmlAPIRespStart = '<h2>API.ai response<br><textarea cols="40" rows="10">'
NLUhtmlAPIRespEnd   = '</textarea>'
testForm = NLUhtmlHeader+NLUformTest

# Conversation page
CONVhtmlHeader = '<center><h1>Dennis Lynch OMSCS Advisor Chatbot - dlynch35@gatech.edu</h1><h2>Based off of the conversation agent developed by Eric Gregori - egregori3@gatech.edu</h2><h2>Ask about OMSCS admissions or curriculum.</h2></center>'
CONVformTest = '<center><form action="convsubmit" id="textform" method="post"><textarea name="text" cols="40" placeholder="Enter text and click Submit"></textarea><input type="submit" value="Submit"></form></center>'
CONVhtmlAPIRespStart = '<center><br><textarea cols="80" rows="40" readonly>'
CONVhtmlAPIRespEnd   = '</textarea></center>'
convForm = CONVhtmlHeader+CONVformTest

# Start Flask server - This code runs once when server is started
my_dir = os.path.dirname(__file__)
my_file_path = os.path.join(my_dir, 'tools/OMSCSLexJson1.json')
with open(my_file_path, encoding='utf-8') as json_data:
    OMSCSDict = json.load(json_data)

#Global variables
Session = mySession.mySession()
client = MongoClient(port=27017)
db = client.chatbot

app = Flask(__name__)

@app.route('/')
def main_page():
    return send_from_directory(my_dir, 'index.html')

#Conversation Testing
@app.route('/conversation')
def ConvPage():
    Session.setInQuestionMode(True)
    Session.setPrevResponse("")
    Session.setPrevIntent("")
    if Session.Timeout():
        Session.StartSession()
        return convForm
    return ('Sorry, only one session is supported and someone else has it. Try again in:'+str(Session.TimeRemaining())+' seconds')

@app.route('/convsubmit', methods=['POST'])
def csubmit_post():
    if Session.isInQuestionMode():
        if Session.stateDone():
            Session.StartSession()
        if Session.Timeout():
            return 'Your session has timed out. Please return to the conversation home page to restart '
        client = convAPI.convAPI()
        if Session.inValidSession():
            return 'Return to the conversation homepage to restart your conversation'
        APIresp, retState = client.GetIntent(request.form["text"], Session.GetSessionId())
        if retState: Session.ChangeState(retState)
        retResponse =  convForm
        retResponse += CONVhtmlAPIRespStart
        retResponse += ('Session Time remaining:'+str(Session.TimeRemaining())+' seconds&#13;&#10;')
        retResponse += Session.AddResponse(APIresp)
        retResponse += CONVhtmlAPIRespEnd
        Session.setInQuestionMode(False)
        return retResponse
    else:
        feedback = request.form["text"]
        accuracy, understandability, effectiveness, written_feedback = feedback.split(';')
        feedback_item = {
            'intent': Session.getPrevIntent(),
            'accuracy': accuracy,
            'understandability': understandability,
            'effectiveness': effectiveness,
            'written_feedback': written_feedback,
            'prev_response': Session.getPrevResponse()
        }
        prev_intent = Session.getPrevIntent()
        weight_score = accuracy + understandability + effectiveness
        prev_weight = prev_intent['weight']
        new_weight = (weight_score + prev_weight)/2
        db.intent.update_one({'_id': prev_intent['_id']}, {'$set': {'weight': new_weight}})
        db.feedback.insert_one(feedback_item)
        Session.setInQuestionMode(True)
        retResponse =  convForm
        retResponse += CONVhtmlAPIRespStart
        retResponse += ('Session Time remaining:'+str(Session.TimeRemaining())+' seconds&#13;&#10;')
        retResponse += Session.AddResponse("Thank you for your feedback!  Feel free to ask another question")
        retResponse += CONVhtmlAPIRespEnd
        return retResponse

#NLU Testing
@app.route('/nlu')
def NLUPage():
    return testForm

@app.route('/nlusubmit', methods=['POST'])
def submit_post():
    WitClient = myWit.myWit( OMSCSDict )
    LUISClient = myLUIS.myLUIS( OMSCSDict )
    APIClient = myAPI.myAPI( OMSCSDict )
    WITresp = WitClient.GetIntent(request.form["text"])
    LUISresp = LUISClient.GetIntent(request.form["text"])
    APIresp = APIClient.GetIntent(request.form["text"])
    retResponse = testForm + '<table style="width:100%" align="center"><tr>'
    retResponse += ('<td>' + NLUhtmlWitRespStart + WITresp + NLUhtmlWitRespEnd + '</td>')
    retResponse += ('<td>' + NLUhtmlLUISRespStart + LUISresp +  NLUhtmlLUISRespEnd + '</td>')
    retResponse += ('<td>' + NLUhtmlAPIRespStart + APIresp +  NLUhtmlAPIRespEnd + '</td>')
    retResponse += '</tr></table>'
    return retResponse

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    intent_name = req['result']['metadata']['intentName']
    intent = db.intent.find_one({'intent': intent_name})
    Session.setPrevIntent(intent)
    return process_response(intent['response'])

def process_response(string_response):
    response = {
        "speech": string_response + "\n\nTo provide feedback on this answer, respond with a 1-10 grading on:\n1)The answer's accuracy in answering your question\n2)How understandable the answer was\n3)How effectively your question was answered\nAdd any other feedback you care to leave as well - scores and feedback should be sent in the format <accuracy score>;<understandability score>;<effectiveness score>;<written feedback>\n\nThank you!",
        "displayText": string_response,
        "source": "lynchdennis94-chatbot-phase1"
    }
    response = json.dumps(response)
    Session.setPrevResponse(response)
    r = make_response(response)
    r.headers['Content-Type'] = 'application/json'
    return r

if __name__ == '__main__':
    app.run()
