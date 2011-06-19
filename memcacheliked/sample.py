from . import Memcacheliked, retrieval_command, storage_command, register_all_commands, STORAGE_STATUS_STORED

@register_all_commands
class SampleServer(Memcacheliked):
    def __init__(self):
        Memcacheliked.__init__(self)
        self.data = {}
        self.flags = {}

    @retrieval_command()
    def command_get(self, command_name, *keys):
        print 'getting keys <%s>' % (keys,)
        return [(k, self.flags.get(k), self.data.get(k)) for k in keys]

    @storage_command()
    def command_set(self, command_name, key, flags, exptime, value, *opts):
        print 'setting key <%s> to <%s>' % (key, value,)
        self.data[key] = value
        self.flags[key] = flags
        return STORAGE_STATUS_STORED

if __name__ == "__main__":
    SampleServer().start()

