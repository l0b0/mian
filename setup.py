#!/usr/bin/env python
"""
Setup configuration
"""

from setuptools import setup
from mian import mian as package

setup(
    name=package.__package__,
    version=package.__version__,
    description='Graph blocks to height in a Minecraft save game',
    long_description=package.__doc__,
    url=package.__url__,
    keywords='Minecraft graph graphs block blocks',
    packages=[package.__package__],
    install_requires=['matplotlib', 'nbt', 'numpy'],
    entry_points={
        'console_scripts': [
            '%(package)s=%(package)s.%(package)s:main' % {
                'package': package.__package__}]},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Topic :: Artistic Software',
        'Topic :: Multimedia :: Graphics'],
    test_suite='test.test_package',
    author=package.__author__,
    author_email=package.__email__,
    maintainer=package.__maintainer__,
    maintainer_email=package.__email__,
    download_url='http://pypi.python.org/pypi/mian/',
    platforms=['POSIX', 'Windows'],
    license=package.__license__,
    )
