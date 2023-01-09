from ...utils import unittest
from ..quest import Quest, ExternalQuestAction, HistoryMessage

class TestQuest(unittest.TestCase):
	def should_create_quest_not_started_by_default(self):
		quest = Quest('quest_id', 'title', ['foo', 'bar'], ['a', 'b'])
		self.assertIsNone(quest._current_state)
		self.assertFalse(quest.is_active())
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
		start_callback = MyCallback()
		finish_callback = MyCallback()
		trigger_registry = TriggerRegistry(
				foo=foo_callback,
				bar=bar_callback,
				start=start_callback,
				finish=finish_callback,
				)

		quest = Quest('quest_id', 'title', ['foo', 'bar', 'end'], ['a', 'b'], finish_states=['end'])
		quest.on_state(None, 'a', 'foo')
		quest.on_state('foo', 'a', ExternalQuestAction('foo'))
		quest.on_state('foo', 'a', HistoryMessage('Hello world!'))
		quest.on_state('foo', 'a', 'bar')
		quest.on_state('bar', 'b', ExternalQuestAction('bar', value=12345))
		quest.on_state('bar', 'b', HistoryMessage('Lorem ipsum...'))
		quest.on_state('bar', 'a', 'end')
		quest.on_state('end', 'b', ExternalQuestAction('bar', value=67890))
		quest.on_start('start')
		quest.on_finish('finish')

		self.assertFalse(quest.is_active())
		self.assertEqual(start_callback.data, [])
		
		action_a = lambda: quest.perform_action('a', trigger_registry=trigger_registry)
		action_b = lambda: quest.perform_action('b', trigger_registry=trigger_registry)

		action_a()
		self.assertTrue(quest.is_active())
		self.assertEqual(start_callback.data, [{'quest':'quest_id'}])
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(finish_callback.data, [])
		self.assertEqual(quest._current_state, 'foo')
		self.assertEqual(quest.get_history(), [])
		self.assertEqual(quest.get_last_history_entry(), None)

		action_a()
		self.assertTrue(quest.is_active())
		self.assertEqual(start_callback.data, [{'quest':'quest_id'}])
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [])
		self.assertEqual(finish_callback.data, [])
		self.assertEqual(quest._current_state, 'bar')
		self.assertEqual(quest.get_history(), ['Hello world!'])
		self.assertEqual(quest.get_last_history_entry(), 'Hello world!')

		action_b()
		self.assertTrue(quest.is_active())
		self.assertEqual(start_callback.data, [{'quest':'quest_id'}])
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [{'value':12345}])
		self.assertEqual(finish_callback.data, [])
		self.assertEqual(quest._current_state, 'bar')
		self.assertEqual(quest.get_history(), ['Hello world!', 'Lorem ipsum...'])
		self.assertEqual(quest.get_last_history_entry(), 'Lorem ipsum...')

		action_a()
		self.assertEqual(quest._current_state, 'end')
		self.assertEqual(start_callback.data, [{'quest':'quest_id'}])
		self.assertFalse(quest.is_active())
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [{'value':12345}])
		self.assertEqual(finish_callback.data, [{'quest':'quest_id'}])
		self.assertEqual(quest.get_history(), ['Hello world!', 'Lorem ipsum...'])
		self.assertEqual(quest.get_last_history_entry(), 'Lorem ipsum...')

		action_b()
		self.assertEqual(quest._current_state, 'end')
		self.assertEqual(start_callback.data, [{'quest':'quest_id'}])
		self.assertFalse(quest.is_active())
		self.assertEqual(foo_callback.data, [])
		self.assertEqual(bar_callback.data, [{'value':12345}, {'value':67890}])
		self.assertEqual(finish_callback.data, [{'quest':'quest_id'}])
		self.assertEqual(quest.get_history(), ['Hello world!', 'Lorem ipsum...'])
		self.assertEqual(quest.get_last_history_entry(), 'Lorem ipsum...')
