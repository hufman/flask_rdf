import mimeparse


DEFAULT_MIMETYPE = 'application/rdf+xml'	# default mimetype to return
WILDCARD = 'INVALID/MATCH'	# matches Accept:*/*
WILDCARD_MIMETYPE = 'application/rdf+xml'	# mimetype for wildcard


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


class FormatSelector(object):
	def __init__(self):
		# any extra formats that we support
		self.formats = {}
		# the list of any mimetypes, unlocked if we have a context
		self.all_mimetypes = []
		# the list of mimetypes that don't require a context
		self.ctxless_mimetypes = []
		# the default mimetype to use
		self.default_mimetype = None
		# the wildcard mimetype to use
		self.wildcard_mimetype = None

	def add_format(self, mimetype, format, requires_context=False):
		""" Registers a new format to be used in a graph's serialize call
		    If you've installed an rdflib serializer plugin, use this
		    to add it to the content negotiation system
		    Set requires_context=True if this format requires a context-aware graph
		"""
		self.formats[mimetype] = format
		if not requires_context:
			self.ctxless_mimetypes.append(mimetype)
		self.all_mimetypes.append(mimetype)

	def get_default_mimetype(self):
		""" Returns the default mimetype """
		mimetype = self.default_mimetype
		if mimetype is None:	# class inherits from module default
			mimetype = DEFAULT_MIMETYPE
		if mimetype is None:	# module is set to None?
			mimetype = 'application/rdf+xml'
		return mimetype

	def get_wildcard_mimetype(self):
		""" Returns the mimetype if the client sends */* """
		mimetype = self.wildcard_mimetype
		if mimetype is None:	# class inherits from module default
			mimetype = WILDCARD_MIMETYPE
		if mimetype is None:	# module is set to None?
			mimetype = 'application/rdf+xml'
		return mimetype

	def decide_mimetype(self, accepts, context_aware = False):
		""" Returns what mimetype the client wants to receive
		    Parses the given Accept header and returns the best one that
		    we know how to output
		    An empty Accept will default to application/rdf+xml
		    An Accept with */* use rdf+xml unless a better match is found
		    An Accept that doesn't match anything will return None
		"""
		mimetype = None
		# If the client didn't request a thing, use default
		if accepts is None or accepts.strip() == '':
			mimetype = self.get_default_mimetype()
			return mimetype

		# pick the mimetype
		if context_aware:
			mimetype = mimeparse.best_match(all_mimetypes + self.all_mimetypes + [WILDCARD], accepts)
		else:
			mimetype = mimeparse.best_match(ctxless_mimetypes + self.ctxless_mimetypes + [WILDCARD], accepts)
		if mimetype == '':
			mimetype = None

		# if browser sent */*
		if mimetype == WILDCARD:
			mimetype = self.get_wildcard_mimetype()

		return mimetype

	def get_serialize_format(self, mimetype):
		""" Get the serialization format for the given mimetype """
		format = self.formats.get(mimetype, None)
		if format is None:
			format = formats.get(mimetype, None)
		return format

	def decide(self, accepts, context_aware=False):
		""" Returns what (mimetype,format) the client wants to receive
		    Parses the given Accept header and picks the best one that
		    we know how to output
		    Returns (mimetype, format)
		    An empty Accept will default to rdf+xml
		    An Accept with */* use rdf+xml unless a better match is found
		    An Accept that doesn't match anything will return (None,None)
		    context_aware=True will allow nquad serialization
		"""
		mimetype = self.decide_mimetype(accepts, context_aware)
		# return what format to serialize as
		if mimetype is not None:
			return (mimetype, self.get_serialize_format(mimetype))
		else:
			# couldn't find a matching mimetype for the Accepts header
			return (None, None)

	def wants_rdf(self, accepts):
		""" Returns whether this client's Accept header indicates
		    that the client wants to receive RDF
		"""
		mimetype = mimeparse.best_match(all_mimetypes + self.all_mimetypes + [WILDCARD], accepts)
		return mimetype and mimetype != WILDCARD


_implicit_instance = FormatSelector()


def add_format(mimetype, format, requires_context=False):
	""" Registers a new format to be used in a graph's serialize call
	    If you've installed an rdflib serializer plugin, use this
	    to add it to the content negotiation system
	    Set requires_context=True if this format requires a context-aware graph
	"""
	global formats
	global ctxless_mimetypes
	global all_mimetypes
	formats[mimetype] = format
	if not requires_context:
		ctxless_mimetypes.append(mimetype)
	all_mimetypes.append(mimetype)

def decide(accepts, context_aware=False):
	return _implicit_instance.decide(accepts, context_aware)

def wants_rdf(accepts):
	""" Returns whether this client's Accept header indicates
	    that the client wants to receive RDF
	"""
	return _implicit_instance.wants_rdf(accepts)
