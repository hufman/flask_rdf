from __future__ import absolute_import
from .common_decorators import ViewDecorator
from rdflib.graph import Graph


class Decorator(ViewDecorator):
	@classmethod
	def make_new_response(cls, old_response, mimetype, serialized):
		import bottle
		bottle.response.content_type = mimetype
		bottle.response.set_header('Vary', 'Accept')
		return serialized

	@classmethod
	def make_406_response(cls):
		import bottle
		bottle.abort(406, '406 Not Acceptable')

	@classmethod
	def get_accept(cls):
		import bottle
		return bottle.request.headers.get('Accept', '')


_implicit_instance = Decorator()


def output(output, accepts):
	return _implicit_instance.output(output, accepts)
def returns_rdf(view):
	return _implicit_instance.decorate(view)
