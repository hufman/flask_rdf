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
# the list of any mimetypes, unlocked if we have a context
all_mimetypes = list(formats.keys())
# the list of mimetypes that don't require a context
ctxless_mimetypes = [m for m in all_mimetypes if 'n-quads' not in m]


def add_format(mimetype, format, requires_context=False):
	""" Registers a new format to be used in a graph's serialize call
	    If you've installed an rdflib serializer plugin, use this
	    to add it to the content negotiation system
	    Set requires_context=True if this format requires a context-aware graph
	"""
	global formats
	formats[mimetype] = format
	if not requires_context:
		ctxless_mimetypes.append(mimetype)
	all_mimetypes.append(mimetype)


def decide_format(accepts, context_aware = False):
	""" Returns what (mimetype,format) the client wants to receive
	    Parses the given Accept header and picks the best one that
	    we know how to output
	    Returns (mimetype, format)
	    An unknown Accept will default to rdf+xml
	    context_aware=True will allow nquad serialization
	"""
	if context_aware:
		mimetype = mimeparse.best_match(all_mimetypes, accepts)
	else:
		mimetype = mimeparse.best_match(ctxless_mimetypes, accepts)
	if mimetype:
		return (mimetype, formats[mimetype])
	else:
		return ('application/rdf+xml', 'xml')
