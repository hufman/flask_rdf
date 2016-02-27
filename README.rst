Flask_rdf
==========

A Flask or Bottle or WSGI decorator to output RDF using content negotiation.

Apply the ``@flask_rdf`` or ``@bottle_rdf`` or ``@wsgi_rdf`` decorator to
a view function and return an rdflib Graph object. Flask_rdf will automatically
format it into an RDF output format, depending on what the request's Accept
header says.  If the view function returns something besides an rdflib graph,
it will be passed through without modification.

Custom formats can be registered easily. After registering the new
serializer with rdflib's plugin support, use the ``add_format``
method to register a new mimetype request to use the new formatter.

The functionality of this module can still help other web frameworks, even
if there isn't a specific decorator yet. The ``format.decide`` function will
return information about with ``Content-Type`` header to send and what
serialization format to use with rdflib. The ``format.wants_rdf`` function
can be used at a high level to determine whether the client even wants RDF.

API
---

-  ``add_format(mimetype, serialize_format)``, ``format.add_format(mimetype, serialize_format)``

   Registers a new format to be recognized for content negotiation. It
   accepts arguments ``mimetype``, ``serialize_format``, and is used to add any
   custom rdflib serializer plugins to be used for the content
   negotiation.
   A third argument, requires_context, will restrict this serializer to
   only be used by graphs that are ``context_aware``.

-  ``format.decide(accept, context_aware=False)``

   Given an Accept header, return a (``mimetype``, ``format``) tuple that would
   best satisfy the client's request.
   If the Accept header is blank, default to RDF+XML
   If the Accept header can't be satisfied, returns (None, None)
   A second argument, context_aware, may be used to allow formats
   that require a ``context_aware`` graph.

- ``FormatSelector()``, ``format.FormatSelector()``

   Class to decide serialization formats. It supports using the module-level
   formats added with ``format.add_format``, but it has its own list of
   formats added with ``FormatSelector().add_format``.

- ``wants_rdf(accept)``, ``format.wants_rdf(accept)``, ``FormatSelector.wants_rdf(accept)``

   Returns whether the client's Accept header indicates that the client
   is prepared to receive RDF data. This can be used in the view to
   return a pretty HTML page for browsers, for example.

-  ``@flask_rdf``, ``@flask.returns_rdf``

   Decorator for a Flask view function to use the Flask request's Accept
   header. It handles converting an rdflib Graph object to the proper
   Flask response, depending on the content negotiation. Other content
   is returned without modification.

-  ``flask.Decorator``

   Class to act as the decorator, in case some behavior needs to be overridden.
   The constructor accepts a FormatSelector object to do custom negotiation.
   The Decorator object itself can be used as the decorator, and it also
   supports the methods ``.output`` and ``.decorate``.

-  ``@bottle_rdf``, ``@bottle.returns_rdf``

   Decorator for a Bottle view function to use the Bottle request's Accept
   header. It handles converting an rdflib Graph object to the proper
   Bottle response, depending on the content negotiation. Other content
   is returned without modification.

-  ``bottle.Decorator``

   Class to act as the decorator, in case some behavior needs to be overridden.
   The constructor accepts a FormatSelector object to do custom negotiation.
   The Decorator object itself can be used as the decorator, and it also
   supports the methods ``.output`` and ``.decorate``.

-  ``@wsgi_rdf``, ``@wsgi.returns_rdf``

   Decorator for a WSGI app function to use the WSGI request's Accept
   header. It handles converting an rdflib Graph object to the proper
   Bottle response, depending on the content negotiation. Other content
   is returned without modification.
   Calls to WSGI's ``start_response`` will pass data through unchanged. Doing
   both a ``start_response`` and returning an RDF object will result in both
   outputs being returned, so don't do that.

-  ``wsgi.Decorator``

   Class to act as the decorator, in case some behavior needs to be overridden.
   The constructor accepts a FormatSelector object to do custom negotiation.
   The Decorator object itself can be used as the decorator, and it also
   supports the methods ``.output`` and ``.decorate``.

Example
-------

.. code:: python

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

.. image:: https://travis-ci.org/hufman/flask_rdf.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/hufman/flask_rdf

