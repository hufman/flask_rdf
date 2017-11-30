import unittest
import webtest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
import bottle
from flask_rdf.bottle import returns_rdf, output, Decorator


def make_graph():
	graph = Graph('IOMemory', BNode())
	person = URIRef('http://example.com/#person')
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	graph.add((person, FOAF.birthday, Literal('2002-01-04', datatype=XSD.date)))
	return graph
graph = make_graph()

def make_ctx_graph():
	context = URIRef('http://example.com/#root')
	graph = ConjunctiveGraph('IOMemory', context)
	person = URIRef('http://example.com/#person')
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	graph.add((person, FOAF.birthday, Literal('2002-01-04', datatype=XSD.date)))
	return graph
ctx_graph = make_ctx_graph()

def make_unicode_graph():
	mygraph = make_graph()
	mygraph.add((BNode(), FOAF.name, Literal('\u2603')))
	return mygraph
unicode_graph = make_unicode_graph()


application = bottle.Bottle()
@application.route('/test')
@returns_rdf
def ctxless():
	return graph
@application.route('/ctx')
@returns_rdf
def ctx():
	return ctx_graph
@application.route('/text')
@returns_rdf
def text():
	return 'This is a test string'
@application.route('/manual')
def manual():
	return output(graph, bottle.request.headers.get('Accept', ''))
@application.route('/unicode')
@returns_rdf
def unicode():
	return unicode_graph
@application.route('/202')
@returns_rdf
def custom():
	bottle.response.set_header('CustomHeader', 'yes')
	bottle.response.status = '202 Custom'
	return graph
app = webtest.TestApp(application)

class TestCases(unittest.TestCase):
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

	def test_format_manual(self):
		turtle = graph.serialize(format='turtle')
		headers = {'Accept': 'text/n3;q=0.5, text/turtle;q=0.9'}
		response = app.get('/manual', headers=headers)
		self.assertEqual(turtle, response.body)
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('Accept', response.headers['vary'])
		self.assertEqual(200, response.status_int)

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

	def test_decorators(self):
		turtle = graph.serialize(format='turtle')
		xml = graph.serialize(format='xml')
		view = graph
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		decorator = Decorator()
		response = decorator.output(view, accepts)
		self.assertEqual(turtle, response)
		# use the decorator
		decoratee = lambda *args: view
		decorated = decorator.decorate(decoratee)
		response = decorated()
		self.assertEqual(turtle, response)
		decorated = decorator(decoratee)
		response = decorated()
		self.assertEqual(turtle, response)
