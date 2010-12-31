import logging
import unittest

from StringIO import StringIO

class TestArgParsing(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        from script import parseargs

        self.parseargs = parseargs

    def test_parseargs(self):
        opts, args = self.parseargs(["foo"])

        self.assertEqual(opts.silent, False)
        self.assertEqual(args, [])

class TestMain(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        root = logging.getLogger()
        buffer = logging.handlers.BufferingHandler(100)
        root.addHandler(buffer)
        self.buffer = buffer.buffer
        self.out = StringIO()
        self.err = StringIO()

    def main(self, *args, **kwargs):
        from script import main

        _kwargs = {
            "out": self.out,
            "err": self.err,
        }
        _kwargs.update(kwargs)
        return main(*args, **_kwargs)

    def test_main(self):
        result = self.main(["foo"])

        self.assertEqual(result, None)
        self.assertEqual(self.buffer, [])

    def test_main_verbose(self):
        result = self.main(["foo", "-vv"])

        self.assertEqual(result, None)
        self.assertEqual(len(self.buffer), 1)
        self.assertEqual(self.buffer[0].msg, "Ready to run")
        self.assertTrue("Ready to run" in self.err.getvalue())
