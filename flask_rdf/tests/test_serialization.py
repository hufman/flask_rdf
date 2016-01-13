import unittest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask import Flask
from flask_rdf import output_flask


def graph():
	graph = Graph('IOMemory', BNode())
	person = BNode()
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	graph.add((person, FOAF.birthday, Literal('2002-01-04', datatype=XSD.date)))
	return graph


def ctx_graph():
	context = URIRef('http://example.com/#root')
	graph = ConjunctiveGraph('IOMemory', context)
	person = BNode()
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	graph.add((person, FOAF.birthday, Literal('2002-01-04', datatype=XSD.date)))
	return graph


class TestCases(unittest.TestCase):
	def setUp(self):
		self.app = Flask(__name__)
		self.context = self.app.test_request_context('/test')
		self.context.__enter__()
	def tearDown(self):
		self.context.__exit__(None, None, None)

	def test_format_simple(self):
		turtle = graph().serialize(format='turtle')
		output = graph()
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(turtle, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual(200, response.status_code)

	def test_format_tuple(self):
		turtle = graph().serialize(format='turtle')
		output = (graph(), 202)
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(turtle, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual(202, response.status_code)

	def test_format_quads_nocontext(self):
		g = graph()
		self.assertFalse(g.context_aware)
		self.assertRaises(Exception,
			g.serialize, format='nquads')

	def test_format_quads_context(self):
		g = ctx_graph()
		self.assertTrue(g.context_aware)
		quads = g.serialize(format='nquads')
		output = (g, 202)
		accepts = 'application/n-quads;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(quads, response.get_data())
		self.assertEqual('application/n-quads', response.headers['content-type'])
		self.assertEqual(202, response.status_code)

	def test_format_quads_lowprio(self):
		""" Test that quads are not used even if possible """
		g = ctx_graph()
		quads = g.serialize(format='turtle')
		output = (g, 202)
		accepts = 'text/turtle;q=0.9, application/n-quads;q=0.4'
		response = output_flask(output, accepts)
		self.assertEqual(quads, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual(202, response.status_code)

	def test_format_quads_highprio(self):
		""" Test that quads are used with alternative """
		g = ctx_graph()
		quads = g.serialize(format='nquads')
		output = (g, 202)
		accepts = 'text/turtle;q=0.4, application/n-quads;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(quads, response.get_data())
		self.assertEqual('application/n-quads', response.headers['content-type'])
		self.assertEqual(202, response.status_code)

	def test_format_quads_unavailable(self):
		""" Test that quads are not used with contextless store """
		g = graph()
		quads = g.serialize(format='turtle')
		output = (g, 202)
		accepts = 'text/turtle;q=0.4, application/n-quads;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(quads, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual(202, response.status_code)

	def test_format_headers(self):
		turtle = graph().serialize(format='turtle')
		output = (graph(), 203, {'x-custom':'12'})
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		response = output_flask(output, accepts)
		self.assertEqual(turtle, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual('12', response.headers['x-custom'])
		self.assertEqual(203, response.status_code)

	def test_empty_format_headers(self):
		xml = graph().serialize(format='xml')
		accepts = ''
		response = output_flask(graph(), accepts)
		self.assertEqual('application/rdf+xml', response.headers['content-type'])

	def test_text(self):
		test_str = 'This is a test string'
		accepts = 'text/n3;q=0.5, text/turtle;q=0.9'
		response = output_flask(test_str, accepts)
		self.assertEqual(test_str.encode('utf-8'), response.get_data())

	def test_unicode(self):
		mygraph = graph()
		mygraph.add((BNode(), FOAF.name, Literal('\u2603')))
		turtle = mygraph.serialize(format='turtle')
		accepts = 'text/turtle'
		response = output_flask(mygraph, accepts)
		data = response.get_data()
		datastr = data.decode('utf-8')
		self.assertEqual(turtle, response.get_data())
		self.assertEqual('text/turtle; charset=utf-8', response.headers['content-type'])
		self.assertEqual(200, response.status_code)
		self.assertTrue('\u2603' in datastr)
