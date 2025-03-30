# curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
#   -H 'Content-Type: application/json' \
#   -X POST \
#   -d '{
#     "contents": [
#       {
#         "parts": [
#           {
#             "text": "How does AI work?"
#           }
#         ]
#       }
#     ]
#   }'


import os
import json
import urllib.request


def fetch(command: str):
    request = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyBWKGu3QCMcgJE53cybyHB_Bk_mywr6eRQ")
    request.method = 'POST'
    request.add_header('Content-Type', 'application/json')
    content = {
        "contents": [
            {
                "parts": [
                    {
                        "text": command
                    }
                ]
            }
        ]
    }
    request.add_header('Content-Length', str(len(json.dumps(content))))
    request.data = json.dumps(content).encode('utf-8')
    response = urllib.request.urlopen(request)
    response_data = response.read()
    return json.loads(response_data.decode('utf-8'))


print(fetch())