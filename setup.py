#!/usr/bin/env python
"""
Setup configuration
"""

from setuptools import find_packages, setup
from mian.mian import __author__ as module_author, __doc__ as module_doc, __email__ as module_email, __license__ as module_license, __maintainer__ as module_maintainer

setup(
    name = 'mian',
    version = '0.7',
    description = 'Graph blocks to height in a Minecraft save game',
    long_description = module_doc,
    url = 'http://pepijndevos.nl/where-to-dig-in-minecraft',
    keywords = 'Minecraft graph graphs block blocks',
    packages = find_packages(exclude=['tests']),
    install_requires = ['nbt'],
    entry_points = {
        'console_scripts': ['mian = mian.mian:main']},
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics'
    ],
    test_suite = 'tests.tests',
    author = module_author,
    author_email = module_email,
    maintainer = module_maintainer,
    maintainer_email = module_email,
    download_url = 'http://github.com/l0b0/mian',
    platforms = ['POSIX', 'Windows'],
    license = module_license,
    )
