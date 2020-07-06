import unittest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask_rdf.common_decorators import ViewDecorator


def make_graph():
	graph = Graph('IOMemory', BNode())
	person = URIRef('http://example.com/#person')
	graph.add((person, RDF.type, FOAF.Person))
	graph.add((person, FOAF.age, Literal(15, datatype=XSD.integer)))
	return graph
graph = make_graph()



class TestCommonDecorators(unittest.TestCase):
	def test_defaults(self):
		decorator = ViewDecorator()
		text = "Test string"
		alt_text = "Test string 2"
		self.assertFalse(decorator.is_graph(text))
		self.assertTrue(decorator.is_graph(graph))
		self.assertEquals(None, decorator.get_graph(text))
		self.assertEquals(graph, decorator.get_graph(graph))
		self.assertEquals(text, decorator.replace_graph(text, alt_text))
		self.assertEquals(alt_text, decorator.replace_graph(graph, alt_text))

	def test_override_raises(self):
		decorator = ViewDecorator()
		self.assertRaises(NotImplementedError, decorator.make_new_response, "response", "text/mimetype", "response")
		self.assertRaises(NotImplementedError, decorator.make_406_response)
		self.assertRaises(NotImplementedError, decorator.get_accept)
