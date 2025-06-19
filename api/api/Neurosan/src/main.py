from flask import Flask, request, Response
from app.neurosan import ask_query
from app.utility import clean_json

app=Flask(__name__)

@app.route("/it-enterprise-bot/neurosan/api/ask-query",methods=["POST"])
def neurosan_ask_query():
    user_query_json = request.get_json()
    user_query_json = clean_json(user_query_json)
    return ask_query(user_query_json)

@app.route("/it-enterprise-bot/neurosan/api/health-check",methods=["GET"])
def health_check():
    return Response("OK", status=200, mimetype='text/plain')


if __name__=="__main__":
    app.run(host="0.0.0.0",port=8080)
    
