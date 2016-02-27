#!/usr/bin/env python
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import FOAF
from flask import Flask
import flask_rdf
import random

app = Flask(__name__)


# set up a custom formatter to return turtle in text/plain to browsers
custom_formatter = flask_rdf.FormatSelector()
custom_formatter.wildcard_mimetype = 'text/plain'
custom_formatter.add_format('text/plain', 'turtle')
custom_decorator = flask_rdf.flask.Decorator(custom_formatter)

@app.route('/')
@app.route('/<path:path>')
@custom_decorator
def random_age(path=''):
    graph = Graph('IOMemory', BNode())
    graph.add((URIRef(path), FOAF.age, Literal(random.randint(20, 50))))
    return graph

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
