Flask\_rdf
==========

A Flask decorator to output RDF using content negotiation.

Apply the @flask\_rdf decorator to a view function and return an rdflib Graph object. Flask\_rdf will automatically format it into an RDF output format, depending on what the request's Accept header says. If the view function return something besides an rdflib graph, it will be passed through without modification.

API
---

 - `add_format` - registers a new (mimetype, serialize\_format) pair, in case you've added some extra rdflib plugins
 - `decide_format` - Given an Accept header, return a (mimetype, format) tuple to be used
 - `flask_rdf` - Decorator to handle returning an rdflib Graph object and formatting it for the client

Example
-------

```python
#!/usr/bin/env python
from rdflib import Graph, BNode, Literal, URIRef
from rdflib.namespace import FOAF
from flask import Flask
from flask_rdf import flask_rdf
import random

app = Flask(__name__)

@app.route('/')
@app.route('/<path:path>')
@flask_rdf
def random_age(path=''):
	graph = Graph('IOMemory', BNode())
	graph.add((URIRef(path), FOAF.age, Literal(random.randint(20, 50))))
	return graph

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
```

[![Build Status](https://travis-ci.org/hufman/flask_rdf.svg?branch=master)](https://travis-ci.org/hufman/flask_rdf)
