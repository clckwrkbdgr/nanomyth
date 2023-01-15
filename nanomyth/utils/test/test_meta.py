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
	name = meta.fieldproperty('_name', "Name doc string")
	delegate_foo = meta.Delegate('member', MockOriginalClass.foo)
	bar = meta.Delegate('member', MockOriginalClass.bar)
	def __init__(self):
		self.member = MockOriginalClass()
		self.member.value = 'baz'
		self._name = "John Doe"
	@meta.typed(str, (int, float, None), first=list, second=(dict, None))
	def typed_function(self, arg_str, arg_int, arg_none, first=None, second=None, third=None):
		pass
	@meta.typed(str)
	def typed_function_single_arg(self, arg):
		pass
	@meta.typed('Delegator')
	def self_user(self, self_again):
		pass

class SuperDelegator:
	super_foo = meta.Delegate('submember', Delegator.delegate_foo)
	def __init__(self):
		self.submember = Delegator()

class MockInheritedClass(MockOriginalClass):
	pass

@meta.typed(MockOriginalClass)
def typed_free_function(heir):
	pass

@meta.typed(any, str)
def any_typed_function(first, second):
	pass

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

class TestProperties(unittest.TestCase):
	def should_adjust_docstsring_for_property(self):
		self.assertEqual(inspect.getdoc(Delegator.name), 'Name doc string')
		self.assertEqual(repr(Delegator.name), 'Name doc string')
	def should_access_property(self):
		obj = Delegator()
		self.assertEqual(obj.name, 'John Doe')

class TestTyping(unittest.TestCase):
	def should_check_argument_types_for_explicitly_typed_functions_with_a_single_argument(self):
		obj = Delegator()
		obj.typed_function_single_arg('ok')
		with self.assertRaises(TypeError) as e:
			obj.typed_function_single_arg(666, 1, None, first=['list'], second={'dict':None}, third='something')
		self.assertEqual(str(e.exception), 'Expected str for arg #0, got: int')
	def should_check_argument_types_for_explicitly_typed_functions(self):
		obj = Delegator()
		obj.typed_function('ok', 1, None, first=['list'], second={'dict':None}, third='something')

		obj.typed_function('ok', 1.2345, None, first=['list'], second={'dict':None}, third='optional values')
		obj.typed_function('ok', None, None, first=['list'], second={'dict':None}, third='optional values')

		obj.typed_function('ok', 1, None, first=['list'], second=None, third='optional values')

		with self.assertRaises(TypeError) as e:
			obj.typed_function(666, 1, None, first=['list'], second={'dict':None}, third='something')
		self.assertEqual(str(e.exception), 'Expected str for arg #0, got: int')

		with self.assertRaises(TypeError) as e:
			obj.typed_function('ok', 'not a number', None, first=['list'], second={'dict':None}, third='something')
		self.assertEqual(str(e.exception), 'Expected int, float, None for arg #1, got: str')

		obj.typed_function('ok', 1, 'should not raise because this argument is not checked', first=['list'], second={'dict':None}, third='something')

		with self.assertRaises(TypeError) as e:
			obj.typed_function('ok', 1, None, first='not a list', second={'dict':None}, third='something')
		self.assertEqual(str(e.exception), 'Expected list for arg {0}, got: str'.format(repr('first')))

		with self.assertRaises(TypeError) as e:
			obj.typed_function('ok', 1, None, first=['list'], second='not a dict', third='something')
		self.assertEqual(str(e.exception), 'Expected dict, None for arg {0}, got: str'.format(repr('second')))

		obj.typed_function('ok', 1, None, first=['list'], second={'dict':None}, third='should not raise because this argument is not checked')
	def should_consider_class_inherintance_when_doing_type_check(self):
		typed_free_function(MockOriginalClass())
		typed_free_function(MockInheritedClass())
	def should_pass_any_type(self):
		any_typed_function(1, 'str')
		any_typed_function('str', 'str')
		any_typed_function(MockOriginalClass(), 'str')
		with self.assertRaises(TypeError) as e:
			any_typed_function(MockOriginalClass(), 1)
	def should_accept_types_by_name(self):
		obj = Delegator()
		obj.self_user(obj)
		with self.assertRaises(TypeError) as e:
			obj.self_user('not self')
		self.assertEqual(str(e.exception), 'Expected Delegator for arg #0, got: str')
