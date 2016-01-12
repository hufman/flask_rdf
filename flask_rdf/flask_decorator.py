from .format import decide_format
from flask import request, make_response


def _get_graph(output):
	""" Given a Flask response, find the rdflib Graph """
	if hasattr(output, 'serialize'):	# single graph object
		return output

	if hasattr(output, '__getitem__'):	# indexable tuple
		if len(output) > 0 and \
		   hasattr(output[0], 'serialize'):	# graph object
			return output[0]


def _set_graph(output, newgraph):
	""" Replace the rdflib Graph in a Flask response """
	if hasattr(output, 'serialize'):	# single graph object
		return newgraph

	if hasattr(output, '__getitem__'):	# indexable tuple
		if len(output) > 0 and \
		   hasattr(output[0], 'serialize'):	# graph object
			return (newgraph,) + output[1:]

def output_flask(output, accepts):
	""" Formats a response from a Flask view to handle any RDF graphs
	    If a view function returns a single RDF graph, serialize it based on Accept header
	    If it's an RDF graph plus some extra headers, pass those along
	    If it's not an RDF graph at all, return it without any special handling
	"""

	graph = _get_graph(output)
	if graph is not None:
		# decide the format
		output_mimetype, output_format = decide_format(accepts, graph.context_aware)
		if 'text' in output_mimetype:
			output_mimetype = output_mimetype + '; charset=utf-8'

		# format the new response
		serialized = graph.serialize(format=output_format)
		final_output = _set_graph(output, serialized)
		response = make_response(final_output)
		response.headers['Content-Type'] = output_mimetype
		return response
	else:
		return make_response(output)


def flask_rdf(view):
	""" Wraps a Flask view function to return formatted RDF graphs
	    Uses content negotiation to serialize the graph to the client-preferred format
	    Passes other content through unmodified
	"""
	from flask import request, make_response
	from functools import wraps

	@wraps(view)
	def decorated(*args, **kwargs):
		output = view(*args, **kwargs)
		return output_flask(output, request.headers.get('Accept', ''))
	return decorated
