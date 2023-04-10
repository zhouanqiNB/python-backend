from flask import Flask, current_app, redirect, url_for, request
from neo4j import GraphDatabase
from query_all import query_all_handler
from get_node import get_node_handler
from get_relationship import get_relationship_handler
import json

app = Flask(__name__)

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "12345678"))
session = driver.session(database="neo4j")


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/query_all')
def query_all():
    res = query_all_handler(session)
    return res


@app.route('/get_node', methods=["POST"])
def get_node():
    # get params from form
    node_id = request.form.get("node_id")
    res = get_node_handler(session, node_id)
    return res


@app.route('/get_relationship', methods=["POST"])
def get_relationship():
    # get params from form
    relationship_id = request.form.get("relationship_id")
    res = get_relationship_handler(session, relationship_id)
    return res


if __name__ == '__main__':
    app.run()
