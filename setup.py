#!/usr/bin/env python

from distutils.core import setup
setup(name='memcacheliked',
        version='0.1',
        description='Simple framework for writing daemons using the memcache interface for storing data',
        author='Vicious Red Beam',
        author_email='vicious.red.beam@gmail.com',
        packages=['memcacheliked'],
        requires=['diesel'],
        license='MIT',
		  url='https://bitbucket.org/ViciousRedBeam/memcacheliked',
        )

