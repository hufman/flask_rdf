import unittest
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask import Flask
from flask_rdf import add_format, decide_format, output_flask


def graph():
	graph = Graph('IOMemory', BNode())
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
	def test_accepts(self):
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		add_format('test/format', 'test')
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('test/format', mimetype)
		self.assertEqual('test', format)
		(mimetype, format) = decide_format('')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

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
		self.assertEqual(test_str, response.get_data())

