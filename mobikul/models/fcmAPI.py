import requests
import json

FCM_URL = "https://fcm.googleapis.com/fcm/send"

class FCMAPI(object):

    def __init__(self, api_key):
        self._API_KEY = api_key

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "Key=" + self._API_KEY
        }

    def jsonDumps(self, data):
        return json.dumps(data).encode('utf8')

    def _push(self, payload):
        response = requests.post(FCM_URL, headers=self._headers(), data=payload)
        print (response)
        if response.status_code == 200:
            if int(response.headers.get('content-length',0)) <= 0:
                return {}
            return response.json()
        elif response.status_code == 401:
            raise Exception("There was an error authenticating the sender account")
        elif response.status_code == 400:
            raise Exception(response.text)
        else:
            raise Exception("FCM server is temporarily unavailable")

    def send(self, payloads=None):
        self.all_responses = []
        for payload in payloads:
            response = self._push(payload)
            self.all_responses.append(response)
        return self.all_responses

    def parse_payload(self, registration_ids=None, topic_name=None, message_body=None, message_title=None,
                      message_icon=None, priority=False, data_message=None, badge=None, color=None, tag=None,
                      **extra_kwargs):
        fcm_payload = dict()
        if registration_ids:
            if len(registration_ids) > 1:
                fcm_payload['registration_ids'] = registration_ids
            else:
                fcm_payload['to'] = registration_ids[0]
        if topic_name:
            fcm_payload['to'] = '/topics/%s' % topic_name
        if priority:
            fcm_payload['priority'] = 'normal'
        else:
            fcm_payload['priority'] = 'high'

        if data_message:
            if isinstance(data_message, dict):
                fcm_payload['data'] = data_message
            else:
                raise Exception("Provided data_message is in the wrong format")

        fcm_payload['notification'] = {}
        if message_icon:
            fcm_payload['notification']['icon'] = message_icon
        if message_body:
            fcm_payload['notification']['body'] = message_body
        if message_title:
            fcm_payload['notification']['title'] = message_title

        if badge:
            fcm_payload['notification']['badge'] = badge
        if color:
            fcm_payload['notification']['color'] = color
        if tag:
            fcm_payload['notification']['tag'] = tag

        if extra_kwargs:
            fcm_payload['notification'].update(extra_kwargs)

        return self.jsonDumps(fcm_payload)

if __name__== "__main__":
    key = "AAAAkdP3f44:APA91bEyls0NapnpJi9IZvMe7jEpkYYx99bdCcFUYtIy4ZDEsEaKaZd1DRhodK6yIXiiWvRfwCE_17HU2uz04s--1qYSw635BgB_ilMxwlQEbBPOqoJkFTPpWnERbbJ2401Eyh27Szyv"
    push_service = FCMAPI(api_key=key)

    registration_id = ["eSUQAef0S2Y:APA91bHm_Q2YJnzBJI77g7mTAW1teFd3i0t8gOM8HqJuv2RgO3_FFSI03ffShGCXus6jNNyILZ3Xng2jNKQdMCJ5FBPneJifkhQ9RJsC52reHfoXOxeEQvLFRbXZw1mKccUIGjf7P7_l"]
    message_title = "Test"
    message_body = "Hi Mohit, your customized news for today is ready"
    payload = push_service.parse_payload(registration_ids=registration_id, message_title=message_title, message_body=message_body)
    print (payload)
    print (push_service.send([payload]))
                
