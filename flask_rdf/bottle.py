from __future__ import absolute_import
from .format import decide, FormatSelector
from rdflib.graph import Graph


class Decorator(object):
	def __init__(self, format_selector=None):
		self.format_selector = format_selector
		if self.format_selector is None:
			self.format_selector = FormatSelector()

	@staticmethod
	def _is_graph(obj):
		return isinstance(obj, Graph)

	@staticmethod
	def _get_graph(output):
		""" Given a Bottle response, check for a rdflib Graph """
		if Decorator._is_graph(output):	# single graph object
			return output

	def output(self, output, accepts):
		""" Formats a response from a Bottle view to handle any RDF graphs
		    If a view function returns a single RDF graph, serialize it based on Accept header
		    If it's not an RDF graph, return it without any special handling
		"""
		import bottle

		graph = Decorator._get_graph(output)
		if graph is not None:
			# decide the format
			output_mimetype, output_format = self.format_selector.decide(accepts, graph.context_aware)
			# requested content couldn't find anything
			if output_mimetype is None:
				bottle.abort(406, '406 Not Acceptable')
			# explicitly mark text mimetypes as utf-8
			if 'text' in output_mimetype:
				output_mimetype = output_mimetype + '; charset=utf-8'

			# format the new response
			serialized = graph.serialize(format=output_format)
			bottle.response.content_type = output_mimetype
			return serialized
		else:
			return output

	def decorate(self, view):
		""" Wraps a Bottle view function to return formatted RDF graphs
		    Uses content negotiation to serialize the graph to the client-preferred format
		    Passes other content through unmodified
		"""
		from functools import wraps
		import bottle

		@wraps(view)
		def decorated(*args, **kwargs):
			output = view(*args, **kwargs)
			return self.output(output, bottle.request.headers.get('Accept', ''))
		return decorated

	def __call__(self, view):
		""" Enables this class to be used as the decorator directly """
		return self.decorate(view)


_implicit_instance = Decorator()


def output(output, accepts):
	return _implicit_instance.output(output, accepts)
def returns_rdf(view):
	return _implicit_instance.decorate(view)
