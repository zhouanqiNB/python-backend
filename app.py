from flask import Flask, current_app, redirect, url_for, request
from neo4j import GraphDatabase
from query_all import query_all_handler
from get_node import get_node_handler
from get_relationship import get_relationship_handler
from nl_query import nl_query_handler
from analyze_database import analyze_database
import json
from flask_cors import CORS

app = Flask(__name__)

# 解决localhost无法请求问题
CORS(app, supports_credentials=True)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))
session = driver.session(database="neo4j")

db_word_set, db_word_2_attr = analyze_database(session)
print("database analyzing done.")
nl_query_handler(session, "", db_word_set, db_word_2_attr)


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/query_all")
def query_all():
    res = query_all_handler(session)
    return json.loads(res)


@app.route("/get_node", methods=["POST"])
def get_node():
    # get params from form
    node_id = request.form.get("node_id")
    res = get_node_handler(session, node_id)
    return res


@app.route("/get_relationship", methods=["POST"])
def get_relationship():
    # get params from form
    relationship_id = request.form.get("relationship_id")
    res = get_relationship_handler(session, relationship_id)
    return res


@app.route("/nl_query", methods=["POST"])
def nl_query():
    # get params from form
    nl_query_str = request.form.get("query_str")
    res = nl_query_handler(session, nl_query_str, db_word_set, db_word_2_attr)
    return json.loads(res)


if __name__ == "__main__":
    app.run(host="0.0.0.0", threaded=True, debug=False)
