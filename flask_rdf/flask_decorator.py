from .format import decide_format
from flask import request, make_response


def output_flask(output, accepts):
	""" Formats a response from a Flask view to handle any RDF graphs
	    If a view function returns a single RDF graph, serialize it based on Accept header
	    If it's an RDF graph plus some extra headers, pass those along
	    If it's not an RDF graph at all, return it without any special handling
	"""
	output_mimetype, output_format = decide_format(accepts)
	if 'text' in output_mimetype:
		output_mimetype = output_mimetype + '; charset=utf-8'

	if hasattr(output, 'serialize'):	# single graph object
		output = output.serialize(format=output_format)
		output = output.encode('utf-8')
		response = make_response(output)
		response.headers['Content-Type'] = output_mimetype
		return response
	if hasattr(output, '__getitem__'):	# indexable tuple
		if hasattr(output[0], 'serialize'):	# graph object
			serialized = output[0].serialize(format=output_format)
			serialized = serialized.encode('utf-8')
			output = (serialized,) + output[1:]
			response = make_response(output)
			response.headers['Content-Type'] = output_mimetype
			return response
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
