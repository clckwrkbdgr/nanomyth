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
	foo = meta.Delegate('member', MockOriginalClass.foo)
	bar = meta.Delegate('member', MockOriginalClass.bar)
	def __init__(self):
		self.member = MockOriginalClass()
		self.member.value = 'baz'

class SuperDelegator:
	foo = meta.Delegate('member', Delegator.foo)
	def __init__(self):
		self.member = Delegator()

class TestDelegatedMethods(unittest.TestCase):
	def should_adjust_docstsring_for_delegated_methods(self):
		self.assertEqual(inspect.getdoc(Delegator.foo), 'Description of foo. \n\nNote: See MockOriginalClass.foo for details.')
		self.assertEqual(inspect.getdoc(Delegator.bar), "Bar's description. \n\nNote: See MockOriginalClass.bar for details.")
	def should_call_delegated_method(self):
		delegator = Delegator()
		self.assertEqual(delegator.foo(), 'foo called')
		self.assertEqual(delegator.foo(), 'foo called')
		self.assertEqual(delegator.bar(), 'bar called: baz')
	def should_delegate_method_through(self):
		delegator = SuperDelegator()
		self.assertEqual(delegator.foo(), 'foo called')
