# -*- coding: utf-8 -*-

import multiprocessing
import unittest
import memcache
import time
from memcacheliked.sample import SampleServer

class GetSetProtocol(unittest.TestCase):
    def setUp(self):
        self.server = SampleServer()
        self.server_process = multiprocessing.Process(target=self.server.start)
        self.server_process.start()
        time.sleep(0.1)
        self.c = memcache.Client(['127.0.0.1:11211'])

    def tearDown(self):
        self.server_process.terminate()

    def test_get_empty(self):
        self.assertTrue(self.c.get('wrong') is None)

    def test_set_get(self):
        self.c.set('right', 'blah')
        self.assertEquals('blah', self.c.get('right'))
    
    def test_multi_get(self):
        self.c.set('first', 'foo')
        self.c.set('second', 'bar')
        res = {'first': 'foo', 'second': 'bar'}
        self.assertEquals(res, self.c.get_multi(['first', 'second']))
    
    def test_multi_empty(self):
        self.assertEquals({}, self.c.get_multi(['wrong1', 'wrong2']))

    def test_delete(self):
        self.c.set('disappearing', 'aaa')
        self.c.delete('disappearing')
        self.assertEquals(None, self.c.get('disappearing'))
    
    def test_delete_multi(self):
        self.c.set('disappearing1', 'aaa')
        self.c.set('disappearing2', 'aaa')
        self.c.delete_multi(['disappearing1', 'disappearing2', 'wrong'])
        self.assertEquals({}, self.c.get_multi(['disappearing1', 'disappearing2', 'wrong']))

