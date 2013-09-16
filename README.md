# Memcache(like)d

Memcacheliked is a server created using the Diesel framework which should expose a service that looks like original memcached, but uses a custom backend implementation. Its goal is not high performance (never tested it from that perspective), but rather to:

 - provide a drop-in replacement for testing different scenarios in 3rd party apps
 - provide an alternative data source for applications that can already talk to memcached

# API

For a short example of how to implement a storage behaving like in-memory memcached, look at `memcacheliked/sample.py`. It provides the standard set/get/delete operations. For the specifics check `memcacheliked/__init__.py`. Options should match those defined by the memcached protocol.

Available decorators / expected function signatures are as follows:

    @retrieval_command
    def get_function(self, command_name, *keys):

    @storage_command
    def set_function(self, command_name, key, flags, exptime, value, *opts):

    @deletion_command
    def del_function(self, command_name, key, *opts):
