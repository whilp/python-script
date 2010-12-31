import unittest

class TestArgParsing(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        from script import parseargs

        self.parseargs = parseargs

    def test_parseargs(self):
        opts, args = self.parseargs(["foo"])

        self.assertEqual(opts.silent, False)
        self.assertEqual(args, [])
