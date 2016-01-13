Flask_rdf
==========

A Flask decorator to output RDF using content negotiation.

Apply the ``@flask_rdf`` decorator to a view function and return an
rdflib Graph object. Flask_rdf will automatically format it into an RDF
output format, depending on what the request's Accept header says. If
the view function returns something besides an rdflib graph, it will be
passed through without modification.

Custom formats can be registered easily. After registering the new
serializer with rdflib's plugin support, use the ``decide_format``
method to register a new mimetype request to use the new formatter.

API
---

-  ``add_format``, ``format.add_format``

   Registers a new format to be recognized for content negotiation. It
   accepts arguments ``mimetype``, ``serialize_format``, and is used to add any
   custom rdflib serializer plugins to be used for the content
   negotiation.
   A third argument, requires_context, will restrict this serializer to
   only be used by graphs that are ``context_aware``

-  ``format.decide``

   Given an Accept header, return a (``mimetype``, ``format``) tuple that would
   best satisfy the client's request.
   If the Accept header is blank, default to RDF+XML
   If the Accept header can't be satisfied, returns (None, None)
   A second argument, context_aware, may be used to allow formats
   that require a ``context_aware`` graph

- ``FormatSelector``

   Class to decide serialization formats. It supports using the module-level
   formats added with ``format.add_format``, but it has its own list of
   formats added with ``FormatSelector().add_format``.

-  ``flask_rdf``

   Decorator for a Flask view function to use the Flask request's Accept
   header. It handles converting an rdflib Graph object to the proper
   Flask response, depending on the content negotiation. Other content
   is returned without modification.

Example
-------

.. code:: python

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

.. image:: https://travis-ci.org/hufman/flask_rdf.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/hufman/flask_rdf

