import inspect
from .. import unittest
from .. import meta

class MockOriginalClass:
	def foo(self):
		""" Description of foo. """
		return 'foo called'
	def bar(self):
		""" Bar's description. """
		return 'bar called: {0}'.format(self.value)

class Delegator:
	delegate_foo = meta.Delegate('member', MockOriginalClass.foo)
	bar = meta.Delegate('member', MockOriginalClass.bar)
	def __init__(self):
		self.member = MockOriginalClass()
		self.member.value = 'baz'

class SuperDelegator:
	super_foo = meta.Delegate('submember', Delegator.delegate_foo)
	def __init__(self):
		self.submember = Delegator()

class TestDelegatedMethods(unittest.TestCase):
	def should_adjust_docstsring_for_delegated_methods(self):
		self.assertEqual(inspect.getdoc(Delegator.delegate_foo), 'Description of foo. \n\nNote: See MockOriginalClass.foo for details.')
		self.assertEqual(inspect.getdoc(Delegator.bar), "Bar's description. \n\nNote: See MockOriginalClass.bar for details.")
	def should_call_delegated_method(self):
		delegator = Delegator()
		self.assertEqual(delegator.delegate_foo(), 'foo called')
		self.assertEqual(delegator.delegate_foo(), 'foo called')
		self.assertEqual(delegator.bar(), 'bar called: baz')
	def should_delegate_method_through(self):
		delegator = SuperDelegator()
		self.assertEqual(delegator.super_foo(), 'foo called')
