import unittest
import webtest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask_rdf.wsgi import returns_rdf, output, Decorator


def make_graph():
	graph = Graph('IOMemory', BNode())
	person = URIRef('http://example.com/#person')
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	return graph
graph = make_graph()

def make_ctx_graph():
	context = URIRef('http://example.com/#root')
	graph = ConjunctiveGraph('IOMemory', context)
	person = URIRef('http://example.com/#person')
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	return graph
ctx_graph = make_ctx_graph()

def make_unicode_graph():
	mygraph = make_graph()
	mygraph.add((BNode(), FOAF.name, Literal('\u2603')))
	return mygraph
unicode_graph = make_unicode_graph()


@returns_rdf
def application(environ, start_response):
	path = environ.get('PATH_INFO', '/')
	if path == '/test':
		return graph
	if path == '/ctx':
		return ctx_graph
	if path == '/unicode':
		return unicode_graph
	if path == '/text':
		return ['This is a test string'.encode('utf-8')]
	if path == '/sneaky':
		write = start_response('200 OK', [])
		write('Sneaky'.encode('utf-8'))
		return ['Step2'.encode('utf-8')]
	if path == '/202':
		start_response('202 Custom', [('CustomHeader','yes')])
		return graph
	if path == '/smart':
		start_response('200 OK', [('Vary','Accept')])
		return graph
	if path == '/profile':
		start_response('200 OK', [('Vary','Cookie')])
		return graph
	if path == '/varyall':
		start_response('200 OK', [('Vary','*')])
		return graph
app = webtest.TestApp(application)

class TestCases(unittest.TestCase):
	def test_output_simple(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/n3;q=0.5, text/turtle;q=0.9'}
		response = {'content-type': '', 'status': '200 OK', 'data': []}
		def set_http_code(arg):
			response['status'] = arg
		def set_content_type(arg):
			response['content-type'] = arg
		response['data'] = output(graph, headers['Accept'], set_http_code, set_content_type)
		self.assertEqual(turtle, response['data'][0])
		self.assertEqual('text/turtle; charset=utf-8', response['content-type'])
		self.assertEqual(200, int(response['status'].split()[0]))

	def test_format_simple(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/n3;q=0.5, text/turtle;q=0.9'}
		response = app.get('/test', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_format_unacceptable(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/html;q=0.9'}
		response = app.get('/test', headers=headers, status=406)
		self.assertEqual(406, response.status_int)

	def test_format_quads_context(self):
		g = ctx_graph
		self.assertTrue(g.context_aware)
		quads = g.serialize(format='nquads')
		headers = {'Accept': 'application/n-quads;q=0.9'}
		response = app.get('/ctx', headers=headers)
		self.assertEqual(quads, response.body)
		self.assertEqual('application/n-quads', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_format_quads_lowprio(self):
		""" Test that quads are not used even if possible """
		g = ctx_graph
		quads = g.serialize(format='turtle')
		headers = {'Accept': 'text/turtle;q=0.9, application/n-quads;q=0.4'}
		response = app.get('/ctx', headers=headers)
		self.assertEqual(quads, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_format_quads_highprio(self):
		""" Test that quads are used with alternative """
		g = ctx_graph
		quads = g.serialize(format='nquads')
		headers = {'Accept': 'text/turtle;q=0.4, application/n-quads;q=0.9'}
		response = app.get('/ctx', headers=headers)
		self.assertEqual(quads, response.body)
		self.assertEqual('application/n-quads', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_format_quads_unavailable(self):
		""" Test that quads are not used with contextless store """
		g = graph
		quads = g.serialize(format='turtle')
		headers = {'Accept': 'text/turtle;q=0.4, application/n-quads;q=0.9'}
		response = app.get('/test', headers=headers)
		self.assertEqual(quads, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_empty_format_headers(self):
		xml = graph.serialize(format='xml')
		headers = {'Accept': ''}
		response = app.get('/test', headers=headers)
		self.assertEqual('application/rdf+xml', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])

	def test_text(self):
		test_str = 'This is a test string'
		headers = {'Accept': 'text/n3;q=0.5, text/turtle;q=0.9'}
		response = app.get('/text', headers=headers)
		self.assertEqual(test_str.encode('utf-8'), response.body)

	def test_sneaky(self):
		""" Test WSGI apps that use start_response().write() """
		test_str = 'SneakyStep2'
		headers = {'Accept': 'text/plain;q=0.5'}
		response = app.get('/sneaky', headers=headers)
		self.assertEqual(test_str.encode('utf-8'), response.body)

	def test_unicode(self):
		mygraph = unicode_graph
		turtle = mygraph.serialize(format='turtle')
		headers = {'Accept': 'text/turtle'}
		response = app.get('/unicode', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)
		self.assertTrue('\u2603' in response.body.decode('utf-8'))

	def test_custom_response(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/turtle'}
		response = app.get('/202', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual('yes', response.headers['CustomHeader'])
		self.assertEqual(202, response.status_int)

	def test_smart_vary(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/turtle'}
		response = app.get('/smart', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_custom_vary(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/turtle'}
		response = app.get('/profile', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Cookie, Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_custom_varyall(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/turtle'}
		response = app.get('/varyall', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('*', response.headers['vary'])
		self.assertEqual(200, response.status_int)

	def test_decorators(self):
		turtle = graph.serialize(format='turtle')
		xml = graph.serialize(format='xml')
		view = graph
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		decorator = Decorator()
		response = decorator.output(view, accepts, lambda *args: None, lambda *args: None)
		self.assertEqual(turtle, response[0])
		# use the decorator
		decoratee = lambda *args: view
		decorated = decorator.decorate(decoratee)
		response = decorated({}, lambda *args: None)
		self.assertEqual(xml, response[0])
		decorated = decorator(decoratee)
		response = decorated({}, lambda *args: None)
		self.assertEqual(xml, response[0])
