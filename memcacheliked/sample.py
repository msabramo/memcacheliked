from . import Memcacheliked, retrieval_command, storage_command, deletion_command, STORAGE_STATUS_STORED, DELETION_STATUS_DELETED, DELETION_STATUS_NOT_FOUND

class SampleServer(Memcacheliked):
    def __init__(self):
        Memcacheliked.__init__(self)
        self.data = {}
        self.flags = {}

    @retrieval_command
    def command_get(self, command_name, *keys):
        print 'getting keys <%s>' % (keys,)
        return [(k, self.flags.get(k), self.data.get(k)) for k in keys]

    @storage_command
    def command_set(self, command_name, key, flags, exptime, value, *opts):
        print 'setting key <%s> to <%s>' % (key, value,)
        self.data[key] = value
        self.flags[key] = flags
        return STORAGE_STATUS_STORED
    
    @deletion_command
    def command_delete(self, command_name, key, *opts):
        print 'deleting key <%s>' % (key,)
        if key not in self.data:
            return DELETION_STATUS_NOT_FOUND
        del self.data[key]
        del self.flags[key]
        return DELETION_STATUS_DELETED
    
if __name__ == "__main__":
    SampleServer().start()

