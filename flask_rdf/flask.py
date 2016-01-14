from __future__ import absolute_import
from .format import decide, FormatSelector


class Decorator(object):
	def __init__(self, format_selector=None):
		self.format_selector = format_selector
		if self.format_selector is None:
			self.format_selector = FormatSelector()

	@staticmethod
	def _get_graph(output):
		""" Given a Flask response, find the rdflib Graph """
		if hasattr(output, 'serialize'):	# single graph object
			return output

		if hasattr(output, '__getitem__'):	# indexable tuple
			if len(output) > 0 and \
			   hasattr(output[0], 'serialize'):	# graph object
				return output[0]

	@staticmethod
	def _set_graph(output, newgraph):
		""" Replace the rdflib Graph in a Flask response """
		if hasattr(output, 'serialize'):	# single graph object
			return newgraph

		if hasattr(output, '__getitem__'):	# indexable tuple
			if len(output) > 0 and \
			   hasattr(output[0], 'serialize'):	# graph object
				return (newgraph,) + output[1:]

	def output(self, output, accepts):
		""" Formats a response from a Flask view to handle any RDF graphs
		    If a view function returns a single RDF graph, serialize it based on Accept header
		    If it's an RDF graph plus some extra headers, pass those along
		    If it's not an RDF graph at all, return it without any special handling
		"""
		from flask import make_response

		graph = Decorator._get_graph(output)
		if graph is not None:
			# decide the format
			output_mimetype, output_format = self.format_selector.decide(accepts, graph.context_aware)
			# requested content couldn't find anything
			if output_mimetype is None:
				return '406 Not Acceptable', 406
			# explicitly mark text mimetypes as utf-8
			if 'text' in output_mimetype:
				output_mimetype = output_mimetype + '; charset=utf-8'

			# format the new response
			serialized = graph.serialize(format=output_format)
			final_output = Decorator._set_graph(output, serialized)
			response = make_response(final_output)
			response.headers['Content-Type'] = output_mimetype
			return response
		else:
			return make_response(output)

	def decorate(self, view):
		""" Wraps a Flask view function to return formatted RDF graphs
		    Uses content negotiation to serialize the graph to the client-preferred format
		    Passes other content through unmodified
		"""
		from flask import request
		from functools import wraps

		@wraps(view)
		def decorated(*args, **kwargs):
			output = view(*args, **kwargs)
			return self.output(output, request.headers.get('Accept', ''))
		return decorated

	def __call__(self, view):
		""" Enables this class to be used as the decorator directly """
		return self.decorate(view)


_implicit_instance = Decorator()


def output(output, accepts):
	return _implicit_instance.output(output, accepts)
def returns_rdf(view):
	return _implicit_instance.decorate(view)
