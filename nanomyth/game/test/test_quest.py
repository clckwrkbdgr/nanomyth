from ...utils import unittest
from ..quest import Quest, ExternalQuestAction

class TestQuest(unittest.TestCase):
	def should_create_quest_not_started_by_default(self):
		quest = Quest('title', ['foo', 'bar'], ['a', 'b'])
		self.assertIsNone(quest.current_state)
	def should_perform_custom_calls_on_action(self):
		class MyCallback:
			def __init__(self): self.data = []
			def __call__(self, **params): self.data.append(params) if params else None
		class TriggerRegistry:
			def __init__(self, **callbacks):
				self.registry = dict(**callbacks)
			def __call__(self, name):
				return self.registry[name]
		foo_callback = MyCallback()
		bar_callback = MyCallback()
		trigger_registry = TriggerRegistry(
				foo=foo_callback,
				bar=bar_callback,
				)

		quest = Quest('title', ['foo', 'bar'], ['a', 'b'])
		quest.on_state(None, 'a', 'foo')
		quest.on_state('foo', 'a', ExternalQuestAction('foo'))
		quest.on_state('foo', 'a', 'bar')
		quest.on_state('bar', 'b', ExternalQuestAction('bar', value=12345))
		
		action_a = lambda: quest.perform_action('a', trigger_registry=trigger_registry)
		action_b = lambda: quest.perform_action('b', trigger_registry=trigger_registry)

		action_a()
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(quest.current_state, 'foo')
		action_a()
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(quest.current_state, 'bar')
		action_b()
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [{'value':12345}])
		self.assertEqual(quest.current_state, 'bar')
