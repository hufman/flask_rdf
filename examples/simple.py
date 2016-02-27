#!/usr/bin/env python
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import FOAF
from flask import Flask
from flask_rdf.flask import returns_rdf
import random

app = Flask(__name__)

@app.route('/')
@app.route('/<path:path>')
@returns_rdf
def random_age(path=''):
    graph = Graph('IOMemory', BNode())
    graph.add((URIRef(path), FOAF.age, Literal(random.randint(20, 50))))
    return graph

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
