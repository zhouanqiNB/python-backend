from flask import Flask
from neo4j import GraphDatabase
from query_all import query_all_handler

app = Flask(__name__)

driver = GraphDatabase.driver("bolt://localhost:7687",
                              auth=("neo4j", "12345678"))
session = driver.session(database="neo4j")


@app.route('/')
def hello_world():  # put application's code heres
    return 'Hello World!'


@app.route('/query_all')
def query_all():  # put application's code here
    res = query_all_handler(session)
    return res


if __name__ == '__main__':
    app.run()
