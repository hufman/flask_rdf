import mimeparse


# What formats we support for serialization
formats = {
   'application/x-turtle': 'turtle',
   'text/turtle': 'turtle',
   'application/rdf+xml': 'xml',
   'application/trix': 'trix',
   'application/n-quads': 'nquads',
   'application/n-triples': 'nt',
   'text/n-triples': 'nt',
   'text/rdf+nt': 'nt',
   'application/n3': 'n3',
   'text/n3': 'n3',
   'text/rdf+n3': 'n3'
}
known_mimetypes = formats.keys()


def add_format(mimetype, format):
	""" Registers a new format to be used in a graph's serialize call
	    If you've installed an rdflib serializer plugin, use this
	    to add it to the content negotiation system
	"""
	global formats
	global known_mimetypes
	formats[mimetype] = format
	known_mimetypes = formats.keys()


def decide_format(accepts):
	""" Returns what (mimetype,format) the client wants to receive
	    Parses the given Accept header and picks the best one that
	    we know how to output
	    Returns (mimetype, format)
	    An unknown Accept will default to rdf+xml
	"""
	mimetype = mimeparse.best_match(known_mimetypes, accepts)
	if mimetype:
		return (mimetype, formats[mimetype])
	else:
		return ('application/rdf+xml', 'xml')
