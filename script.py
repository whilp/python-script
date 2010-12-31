#!/usr/bin/env python
"""`This`_ is what an ideal Python script might look like.

.. _This:   https://github.com/wcmaier/python-script/blob/master/script.py

It's written to have several important properties; namely:

  * readability: follows :PEP:`8`.
  * portability: uses portable components where necessary.
  * testability: unit and functional tests that can be run without causing side
    effects (and these tests are tested).
  * configurability: command line configuration of logging and other details.

`Git`_ and `Mercurial`_ repositories for this script can be found at `Github`_ and
`Bitbucket`_, respectively::
    
    $ git clone git://github.com/wcmaier/python-script.git
    $ hg clone http://bitbucket.org/wcmaier/python-script

.. _Git:        http://git-scm.com/
.. _Mercurial:  http://mercurial.selenic.com/
.. _Github:     http://github.com/wcmaier/python-script
.. _Bitbucket:  http://bitbucket.org/wcmaier/python-script
"""
__license__ = """\
Copyright (c) 2010 Will Maier <willmaier@ml1.net>

Permission to use, copy, modify, and distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.\
"""

import logging
import optparse
import sys

# NullHandler was added in Python 3.1.
try:
    NullHandler = logging.NullHandler
except AttributeError:
    class NullHandler(logging.Handler):
        def emit(self, record): pass

# Add a do-nothing NullHandler to the module logger to prevent "No handlers
# could be found" errors. The calling code can still add other, more useful
# handlers, or otherwise configure logging.
log = logging.getLogger(__name__)
log.addHandler(NullHandler())

def parseargs(argv):
    """Parse command line arguments.

    Returns a tuple (*opts*, *args*), where *opts* is an
    :class:`optparse.Values` instance and *args* is the list of arguments left
    over after processing.

    :param argv: a list of command line arguments, usually :data:`sys.argv`.
    """
    prog = argv[0]
    parser = optparse.OptionParser(prog=prog)
    parser.allow_interspersed_args = False

    defaults = {
        "quiet": 0,
        "silent": False,
        "verbose": 0,
    }

    # Global options.
    parser.add_option("-q", "--quiet", dest="quiet",
        default=defaults["quiet"], action="count",
        help="decrease the logging verbosity")
    parser.add_option("-s", "--silent", dest="silent",
        default=defaults["silent"], action="store_true",
        help="silence the logger")
    parser.add_option("-v", "--verbose", dest="verbose",
        default=defaults["verbose"], action="count",
        help="increase the logging verbosity")

    (opts, args) = parser.parse_args(args=argv[1:])
    return (opts, args)

def main(argv, out=None, err=None):
    """Main entry point.

    Returns a value that can be understood by :func:`sys.exit`.

    :param argv: a list of command line arguments, usually :data:`sys.argv`.
    :param out: stream to write messages; :data:`sys.stdout` if None.
    :param err: stream to write error messages; :data:`sys.stderr` if None.
    """
    if out is None: # pragma: nocover
        out = sys.stdout
    if err is None: # pragma: nocover
        err = sys.stderr
    (opts, args) = parseargs(argv)
    level = logging.WARNING - ((opts.verbose - opts.quiet) * 10)
    if opts.silent:
        level = logging.CRITICAL + 1

    format = "%(message)s"
    handler = logging.StreamHandler(err)
    handler.setFormatter(logging.Formatter(format))
    log.addHandler(handler)
    log.setLevel(level)

    log.debug("Ready to run")

if __name__ == "__main__": # pragma: nocover
    sys.exit(main(sys.argv))

# Script unit and functional tests. These tests are defined after the '__name__
# == "__main__"' idiom so that they aren't loaded when the script is executed.
# If the script (or a symlink to the script) has the usual .py filename
# extension, these tests may be run as follows:
# 
#   $ python -m unittest path/to/script.py (Python 3.X/unittest2)
#   $ nosetests path/to/script.py
#
# If the script does not have the .py extension, the scriptloader nose plugin
# can be used instead:
#
#   $ pip install scriptloader
#   $ nosetests --with-scriptloader path/to/script

# Override the global logger instance with one from a special "tests" namespace.
log = logging.getLogger("%s.tests" % __name__)

import os
import shutil
import subprocess
import tempfile
import unittest

def getpyfile(filename, split=os.path.splitext, exists=os.path.exists):
    """Return the .py file for a filename.

    Resolves things like .pyo and .pyc files to the original .py. If *filename*
    doesn't have a .py extension, it will be returned as-is.

    :param filename: the path to a file.
    :param split: a function to split extensions from basenames, usually :func:`os.path.splitext`.
    :param exists: a function to determine whether a file exists, usually :func:`os.path.exists`.
    """
    sourcefile = filename
    base, ext = split(filename)
    if ext[:3] == ".py":
        sourcefile = base + ".py"
    if not exists(sourcefile):
        sourcefile = filename
    return sourcefile

class TestMain(unittest.TestCase):

    def test_aunittest(self):
        """This is a dummy unit test."""
        self.assertEqual(1 + 1, 2)

class TestFunctional(unittest.TestCase):
    """Functional tests.

    These tests build a temporary environment and run the script in it.
    """

    def setUp(self):
        """Prepare for a test.

        This method builds an artificial runtime environment, creates a
        temporary directory and sets it as the working directory.
        """
        unittest.TestCase.setUp(self)

        self.processes = []
        self.env = {
            "PATH": os.environ["PATH"],
            "LANG": "C",
        }
        self.tmpdir = tempfile.mkdtemp(prefix=__name__ + "-test-")
        self.oldcwd = os.getcwd()

        log.debug("Initializing test directory %r", self.tmpdir)
        os.chdir(self.tmpdir)

    def tearDown(self):
        """Clean up after a test.

        This method destroys the temporary directory, resets the working
        directory and reaps any leftover subprocesses.
        """
        unittest.TestCase.tearDown(self)
        log.debug("Cleaning up test directory %r", self.tmpdir)
        shutil.rmtree(self.tmpdir)
        os.chdir(self.oldcwd)

        while self.processes:
            process = self.processes.pop()
            log.debug("Reaping test process with PID %d", process.pid)
            try:
                process.kill()
            except OSError, e:
                if e.errno != 3:
                    raise

    def sub(self, *args, **kwargs):
        """Run a subprocess.

        Returns a tuple (*process*, *stdout*, *stderr*). If the *communicate*
        keyword argument is True, *stdout* and *stderr* will be strings.
        Otherwise, they will be None. *process* is a :class:`subprocess.Popen`
        instance. By default, the path to the script itself will be used as the
        executable and *args* will be passed as arguments to it.

        .. note::
            The value of *executable* will be prepended to *args*.

        :param args: arguments to be passed to :class:`subprocess.Popen`.
        :param kwargs: keyword arguments to be passed to :class:`subprocess.Popen`.
        :param communicate: if True, call :meth:`subprocess.Popen.communicate` after creating the subprocess.
        :param executable: if present, the path to a program to execute instead of this script.
        """
        _kwargs = {
            "executable": os.path.abspath(getpyfile(__file__)),
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "env": self.env,
        }
        communicate = kwargs.pop("communicate", True)
        _kwargs.update(kwargs)
        kwargs = _kwargs
        args = [kwargs["executable"]] + list(args)
        log.debug("Creating test process %r, %r", args, kwargs)
        process = subprocess.Popen(args, **kwargs)

        if communicate is True:
            stdout, stderr = process.communicate()
        else:
            stdout, stderr = None, None
            self.processes.append(process)

        return process, stdout, stderr

    def test_functionaltest(self):
        """This is a dummy functional test."""
        proc, stdout, stderr = self.sub("-h")

        self.assertEqual(proc.returncode, 0)
        self.assertTrue("script.py" in stdout)
