import apiai, json
from config import config
from db import Settings, get_data_from_db, get_setting_value

def getAnswerFromDialogflow(messageText):
  request = apiai.ApiAI(get_setting_value('DialogflowApi')).text_request()
  request.lang = get_setting_value('language')
  request.session_id = get_setting_value('sessionId')
  request.query = messageText
  responseJson = json.loads(request.getresponse().read().decode("utf-8"))
  response = responseJson["result"]["fulfillment"]["speech"]
  return response