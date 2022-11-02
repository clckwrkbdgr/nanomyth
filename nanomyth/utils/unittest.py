from __future__ import absolute_import
from unittest import *
defaultTestLoader.testMethodPrefix = 'should'
try:
	import unittest.mock as mock
except: # pragma: no cover -- py2 only
	import mock
mock.patch.TEST_PREFIX = 'should'
