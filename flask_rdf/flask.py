from __future__ import absolute_import
from .common_decorators import ViewDecorator
from rdflib.graph import Graph


class Decorator(ViewDecorator):
	@classmethod
	def get_graph(cls, response):
		""" Given a Flask response, find the rdflib Graph """
		if cls.is_graph(response):	# single graph object
			return response

		if hasattr(response, '__getitem__'):	# indexable tuple
			if len(response) > 0 and \
			   cls.is_graph(response[0]):	# graph object
				return response[0]

	@classmethod
	def replace_graph(cls, response, serialized):
		""" Replace the rdflib Graph in a Flask response """
		if cls.is_graph(response):	# single graph object
			return serialized

		if hasattr(response, '__getitem__'):	# indexable tuple
			if len(response) > 0 and \
			   cls.is_graph(response[0]):	# graph object
				return (serialized,) + response[1:]
		return response

	@classmethod
	def make_new_response(cls, old_response, mimetype, serialized):
		from flask import make_response
		final_output = cls.replace_graph(old_response, serialized)
		response = make_response(final_output)
		response.headers['Content-Type'] = mimetype
		response.headers['Vary'] = 'Accept'
		return response

	@classmethod
	def make_406_response(cls):
		return '406 Not Acceptable', 406

	@classmethod
	def get_accept(cls):
		from flask import request
		return request.headers.get('Accept', '')


_implicit_instance = Decorator()


def output(response, accepts):
	return _implicit_instance.output(response, accepts)
def returns_rdf(view):
	return _implicit_instance.decorate(view)
