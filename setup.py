from __future__ import print_function
from setuptools import setup
from setuptools.command.test import test as TestCommand
import io
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

__version__ = '0.9.6.2'


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='python-ixia',
    version=__version__,
    url='https://github.com/shmir/python-ixia/',
    license='GNU Lesser General Public License v2 (LGPLv2)',
    author='Michael Walle',
    tests_require=[],
    install_requires=['paramiko'],
    cmdclass={},
    author_email='michael.walle@kontron.com',
    description='Python OO API package to automate Ixia IxExplorer traffic generator',
    long_description=long_description,
    packages=['pyixia', 'examples', 'bin'],
    include_package_data=True,
    platforms='any',
    test_suite='ixnetwork.test',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing :: Traffic Generation'],
    extras_require={}
)
