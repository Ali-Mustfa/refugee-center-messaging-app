from flask import Flask,render_template,request
import requests
import os
import json
from pprint import pprint
from googleapiclient.discovery import build

app = Flask(__name__)

text_belt_api_key = os.environ["TEXT_BELT_API_KEY"]
sheet_id = []

@app.get("/")
def index():
    return render_template("index.html")

convo={}
@app.post("/")
def confirmation():
    data = request.form.get("data")
    template = request.form.get("template")
    data = data.replace("\r", "")
    rows = data.split("\n")
    first_row = 0
    keys = []
    final = []
    for row in rows:
        first_row = first_row + 1
        value = row.split(",")
        if first_row == 1:
            keys = value
        else:
            dictionary = {}
            key_index = 0
            for key in keys:
                dictionary[key] = value[key_index]
                key_index = key_index + 1
            final.append(dictionary)
    
    for each_message in final:
        resp = requests.post("https://textbelt.com/text", {
            "phone": each_message.get("phone"),
            "message": template.format(**each_message),
            "key": text_belt_api_key,
            "replyWebhookUrl":'https://ac9d-2601-681-6000-c120-383d-a798-b5a5-727a.ngrok-free.app/reply'
        })
        
        confirmation = resp.json()
        textId = confirmation.get("textId")
        convo[textId]= []
        convo[textId].append({"from": "system", "text": template.format(**each_message)})
        print(confirmation)
        with open("answer.json", "w") as file:
            json.dump(convo,file)  
    
    service = build('sheets', 'v4')
    spreadsheets = service.spreadsheets()
    new_sheets_request = spreadsheets.create(body={"properties": {"title": "Fal"}})
    new_sheets_response = new_sheets_request.execute()
    new_sheets_id = new_sheets_response['spreadsheetId']
    
    values = [
        ["textId", "from", "message"],
        ] 
    
    # for keys, val in convo.items():
    #     values[0].append([keys,"system",val[0].get("text")],)  

    body = {
        'values': values
    }

    result = spreadsheets.values().append(
        spreadsheetId=new_sheets_id,
        range="Sheet1",  # Update with your sheet name or range
        valueInputOption="RAW",
        body=body
    ).execute()
    
    sheet_id.append(new_sheets_id)
    service.close()
    
    return render_template("confirmation.html")

@app.post("/reply")
def reply():
    reply = request.json
    textId = reply.get("textId")
    # convo.get(textId).append({"from": reply.get("fromNumber"),"text": reply.get("text")})
    # print(reply)
    
    print(convo)
    for keys in convo:
        print(keys)
    
    service = build('sheets', 'v4')
    spreadsheets = service.spreadsheets()
    print (sheet_id)
    sheets_id = sheet_id[0]
    spreadsheet_id = sheets_id

    values = [
        [textId, reply.get("fromNumber"), reply.get("text")],

    ]   

    body = {
        'values': values
    }

    result = spreadsheets.values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1",  # Update with your sheet name or range
        valueInputOption="RAW",
        body=body
    ).execute()
    service.close()
    
    # with open("answer.json", "w") as file:
    #     json.dump(convo,file,indent=4)

    return "ok"


app.run(debug=True)