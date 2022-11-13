from ...utils import unittest
from ..quest import Quest

class TestQuest(unittest.TestCase):
	def should_create_quest_not_started_by_default(self):
		quest = Quest('title', ['foo', 'bar'], ['a', 'b'])
		self.assertIsNone(quest.current_state)
	def should_perform_custom_calls_on_action(self):
		class MyCallback:
			def __init__(self): self.data = []
			def __call__(self, *params): self.data.append(params)

		quest = Quest('title', ['foo', 'bar'], ['a', 'b'])
		foo_callback = MyCallback()
		bar_callback = MyCallback()
		quest.on_state(None, 'a', 'foo')
		quest.on_state('foo', 'a', foo_callback)
		quest.on_state('foo', 'a', 'bar')
		quest.on_state('bar', 'b', bar_callback)
		
		action_a = lambda *params: quest.perform_action('a', *params)
		action_b = lambda *params: quest.perform_action('b', *params)

		action_a('start quest')
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(quest.current_state, 'foo')
		action_a('first step')
		self.assertEqual(foo_callback.data, [('first step',)])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(quest.current_state, 'bar')
		action_b('second step')
		self.assertEqual(foo_callback.data, [('first step',)])
		self.assertEqual(bar_callback.data, [('second step',)])
		self.assertEqual(quest.current_state, 'bar')
