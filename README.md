Flask\_rdf
==========

A Flask decorator to output RDF using content negotiation.

Apply the @flask\_rdf decorator to a view function and return an rdflib Graph object. Flask\_rdf will automatically format it into an RDF output format, depending on what the request's Accept header says. If the view function return something besides an rdflib graph, it will be passed through without modification.

API
---

 - `add_format` - registers a new (mimetype, serialize\_format) pair, in case you've added some extra rdflib plugins
 - `decide_format` - Given an Accept header, return a (mimetype, format) tuple to be used
 - `flask_rdf` - Decorator to handle returning an rdflib Graph object and formatting it for the client
