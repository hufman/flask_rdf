from __future__ import absolute_import
from .format import decide, FormatSelector
from rdflib.graph import Graph


class ViewDecorator(object):
	def __init__(self, format_selector=None):
		self.format_selector = format_selector
		if self.format_selector is None:
			self.format_selector = FormatSelector()

	@classmethod
	def is_graph(cls, obj):
		""" Check whether this object is an rdflib Graph """
		return isinstance(obj, Graph)

	@classmethod
	def get_graph(cls, response):
		""" Given a view response, find the rdflib Graph, or None """
		if cls.is_graph(response):	# single graph object
			return response

	@classmethod
	def replace_graph(cls, response, serialized):
		""" Replace the rdflib Graph in a view response """
		if cls.is_graph(response):	# single graph object
			return serialized
		return response

	@classmethod
	def make_new_response(cls, old_response, mimetype, serialized):
		""" Return a new framework-specific response with the seralized data """
		raise NotImplementedError

	@classmethod
	def make_406_response(cls):
		""" Return the framework-specific HTTP 406 error """
		raise NotImplementedError

	@classmethod
	def get_accept(cls):
		""" Load the framework-specific Accept header """
		raise NotImplementedError

	def output(self, response, accepts):
		""" Formats a response from a view to handle any RDF graphs
		    If a view function returns an RDF graph, serialize it based on Accept header
		    If it's not an RDF graph, return it without any special handling
		"""
		graph = self.get_graph(response)
		if graph is not None:
			# decide the format
			mimetype, format = self.format_selector.decide(accepts, graph.context_aware)

			# requested content couldn't find anything
			if mimetype is None:
				return self.make_406_response()

			# explicitly mark text mimetypes as utf-8
			if 'text' in mimetype:
				mimetype = mimetype + '; charset=utf-8'

			# format the new response
			serialized = graph.serialize(format=format)
			response = self.make_new_response(response, mimetype, serialized)
			return response
		else:
			return response

	def decorate(self, view):
		""" Wraps a view function to return formatted RDF graphs
		    Uses content negotiation to serialize the graph to the client-preferred format
		    Passes other content through unmodified
		"""
		from functools import wraps

		@wraps(view)
		def decorated(*args, **kwargs):
			response = view(*args, **kwargs)
			accept = self.get_accept()
			return self.output(response, accept)
		return decorated

	def __call__(self, view):
		""" Enables this class to be used as the decorator directly """
		return self.decorate(view)
