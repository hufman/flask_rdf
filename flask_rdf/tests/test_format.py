import unittest
from rdflib import BNode, ConjunctiveGraph, Graph, Literal, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD
from flask import Flask
from flask_rdf import add_format, decide_format, output_flask


class TestFormat(unittest.TestCase):
	def test_default(self):
		(mimetype, format) = decide_format(None)
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)
		(mimetype, format) = decide_format('')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_incorrect(self):
		(mimetype, format) = decide_format('text/strangerdf')
		self.assertEqual(None, mimetype)
		self.assertEqual(None, format)

	def test_browser(self):
		(mimetype, format) = decide_format('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_custom(self):
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		# custom
		add_format('test/format', 'test')
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/format;q=1.0, text/n3;q=0.9')
		self.assertEqual('test/format', mimetype)
		self.assertEqual('test', format)
		# custom with context
		add_format('test/ctxformat', 'ctxtest', requires_context=True)
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/ctxformat;q=1.0, text/n3;q=0.9', context_aware=True)
		self.assertEqual('test/ctxformat', mimetype)
		self.assertEqual('ctxtest', format)
		(mimetype, format) = decide_format('text/turtle;q=0.5, test/ctxformat;q=1.0, text/n3;q=0.9', context_aware=False)
		self.assertEqual('text/n3', mimetype)
		self.assertEqual('n3', format)
		# default
		(mimetype, format) = decide_format('')
		self.assertEqual('application/rdf+xml', mimetype)
		self.assertEqual('xml', format)

	def test_quads(self):
		# test that turtle is used because higher priority
		(mimetype, format) = decide_format('text/turtle;q=0.9, application/n-quads;q=0.4')
		self.assertEqual('text/turtle', mimetype)
		self.assertEqual('turtle', format)
		# test that turtle is used because our store doesn't have a context
		(mimetype, format) = decide_format('text/turtle;q=0.5, application/n-quads;q=0.9', context_aware=False)
		self.assertEqual('text/turtle', mimetype)
		self.assertEqual('turtle', format)
		# test that quads is used because our store has a context
		(mimetype, format) = decide_format('text/turtle;q=0.5, application/n-quads;q=0.9', context_aware=True)
		self.assertEqual('application/n-quads', mimetype)
		self.assertEqual('nquads', format)
		# test that it returns no valid format
		(mimetype, format) = decide_format('application/n-quads;q=0.9', context_aware=False)
		self.assertEqual(None, mimetype)
		self.assertEqual(None, format)
