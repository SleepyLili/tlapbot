from flask import Flask,request,json
import requests

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Webhooks with Python'

@app.route('/githubIssue',methods=['POST'])
def githubIssue():
    data = request.json
    print(f'Issue {data["issue"]["title"]} {data["action"]} \n')
    print(f'{data["issue"]["body"]} \n')
    print(f'{data["issue"]["url"]} \n')
    return data

@app.route('/owncastWebhook',methods=['POST'])
def owncastWebhook():
    data = request.json
    if data["type"] == "CHAT":
        print("New chat message:")
        print(f'from {data["eventData"]["user"]["displayName"]}:')
        print(f'{data["eventData"]["body"]}')
    return data

if __name__ == '__main__':
    app.run(debug=True)