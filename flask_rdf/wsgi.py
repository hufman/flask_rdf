from __future__ import absolute_import
from .format import decide, FormatSelector
from rdflib.graph import Graph
from six import BytesIO
import itertools


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
		""" Given a WSGI response, check for a rdflib Graph """
		if Decorator._is_graph(output):	# single graph object
			return output

	def output(self, output, accepts, set_http_code, set_content_type):
		""" Formats a response from a WSGI app to handle any RDF graphs
		    If a view function returns a single RDF graph, serialize it based on Accept header
		    If it's not an RDF graph, return it without any special handling
		"""

		graph = Decorator._get_graph(output)
		if graph is not None:
			# decide the format
			output_mimetype, output_format = self.format_selector.decide(accepts, graph.context_aware)
			# requested content couldn't find anything
			if output_mimetype is None:
				set_http_code("406 Not Acceptable")
				return ['406 Not Acceptable'.encode('utf-8')]
			# explicitly mark text mimetypes as utf-8
			if 'text' in output_mimetype:
				output_mimetype = output_mimetype + '; charset=utf-8'

			# format the new response
			serialized = graph.serialize(format=output_format)
			set_content_type(output_mimetype)
			return [serialized]
		else:
			return output

	def decorate(self, app):
		""" Wraps a WSGI application to return formatted RDF graphs
		    Uses content negotiation to serialize the graph to the client-preferred format
		    Passes other content through unmodified
		"""
		from functools import wraps

		@wraps(app)
		def decorated(environ, start_response):
			# capture any start_response from the app
			app_response = {}
			app_response['status'] = "200 OK"
			app_response['headers'] = []
			app_response['written'] = BytesIO()
			def custom_start_response(status, headers, *args, **kwargs):
				app_response['status'] = status
				app_response['headers'] = headers
				app_response['args'] = args
				app_response['kwargs'] = kwargs
				return app_response['written'].write
			returned = app(environ, custom_start_response)

			# callbacks from the serialization
			def set_http_code(status):
				app_response['status'] = str(status)
			def set_header(header, value):
				app_response['headers'] = [(h,v) for (h,v) in app_response['headers'] if h.lower() != header.lower()]
				app_response['headers'].append((header, value))
			def set_content_type(content_type):
				set_header('Content-Type', content_type)

			# do the serialization
			accept = environ.get('HTTP_ACCEPT', '')
			new_return = self.output(returned, accept, set_http_code, set_content_type)

			# set the Vary header
			vary_headers = (v for (h,v) in app_response['headers'] if h.lower() == 'vary')
			vary_elements = list(itertools.chain(*[v.split(',') for v in vary_headers]))
			vary_elements = list(set([v.strip() for v in vary_elements]))
			if '*' not in vary_elements and 'accept' not in (v.lower() for v in vary_elements):
				vary_elements.append('Accept')
				set_header('Vary', ', '.join(vary_elements))

			# pass on the result to the parent WSGI server
			parent_writer = start_response(app_response['status'],
			                               app_response['headers'],
			                               *app_response.get('args', []),
			                               **app_response.get('kwargs', {}))
			written = app_response['written'].getvalue()
			if len(written) > 0:
				parent_writer(written)
			return new_return
		return decorated

	def __call__(self, app):
		""" Enables this class to be used as the decorator directly """
		return self.decorate(app)


_implicit_instance = Decorator()


def output(output, accepts, set_http_code, set_content_type):
	return _implicit_instance.output(output, accepts, set_http_code, set_content_type)
def returns_rdf(view):
	return _implicit_instance.decorate(view)
