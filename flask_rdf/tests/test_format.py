import unittest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask import Flask
from flask_rdf import add_format, FormatSelector, output_flask
from flask_rdf.format import decide


class TestFormat(unittest.TestCase):
	def setUp(self):
		self.format = FormatSelector()

	def test_module(self):
		# test that moduleformat isn't in place
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/moduleformat;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		(modulemimetype, moduleformat) = decide('text/turtle;q=0.5, test/moduleformat;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', modulemimetype)
		self.assertEqual('n3', moduleformat)
		# add moduleformat to the module
		add_format('test/moduleformat', 'test')
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/moduleformat;q=1.0, test/n3;q=0.9')
		self.assertEqual('test/moduleformat', mimetype)
		self.assertEqual('test', format)
		(modulemimetype, moduleformat) = decide('text/turtle;q=0.5, test/moduleformat;q=1.0, text/n3;q=0.9')
		self.assertEqual('test/moduleformat', modulemimetype)
		self.assertEqual('test', moduleformat)
		# add instanceformat to the single class
		self.format.add_format('test/instanceformat', 'test')
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/instanceformat;q=1.0, test/n3;q=0.9')
		self.assertEqual('test/instanceformat', mimetype)
		self.assertEqual('test', format)
		(modulemimetype, moduleformat) = decide('text/turtle;q=0.5, test/instanceformat;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', modulemimetype)
		self.assertEqual('n3', moduleformat)

	def test_default(self):
		(mimetype, format) = self.format.decide(None)
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)
		(mimetype, format) = self.format.decide('')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_incorrect(self):
		(mimetype, format) = self.format.decide('text/strangerdf')
		self.assertEqual(None, mimetype)
		self.assertEqual(None, format)

	def test_browser(self):
		(mimetype, format) = self.format.decide('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_custom(self):
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		# custom
		self.format.add_format('test/format', 'test')
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('test/format', mimetype)
		self.assertEqual('test', format)
		# custom with context
		self.format.add_format('test/ctxformat', 'ctxtest', requires_context=True)
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/ctxformat;q=1.0, text/n3;q=0.9', context_aware=True)
		self.assertEqual('test/ctxformat', mimetype)
		self.assertEqual('ctxtest', format)
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, test/ctxformat;q=1.0, text/n3;q=0.9', context_aware=False)
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		# default
		(mimetype, format) = self.format.decide('')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_quads(self):
		# test that turtle is used because higher priority
		(mimetype, format) = self.format.decide('text/turtle;q=0.9, application/n-quads;q=0.4')
		self.assertEqual('text/turtle', mimetype)
		self.assertEqual('turtle', format)
		# test that turtle is used because our store doesn't have a context
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, application/n-quads;q=0.9', context_aware=False)
		self.assertEqual('text/turtle', mimetype)
		self.assertEqual('turtle', format)
		# test that quads is used because our store has a context
		(mimetype, format) = self.format.decide('text/turtle;q=0.5, application/n-quads;q=0.9', context_aware=True)
		self.assertEqual('application/n-quads', mimetype)
		self.assertEqual('nquads', format)
		# test that it returns no valid format
		(mimetype, format) = self.format.decide('application/n-quads;q=0.9', context_aware=False)
		self.assertEqual(None, mimetype)
		self.assertEqual(None, format)
