# -*- coding: utf-8 -*-

from functools import wraps
from diesel import Application, Service, first, until, sleep, send, log
import traceback
import types

STORAGE_STATUS_STORED = 'STORED'
STORAGE_STATUS_NOT_STORED = 'NOT_STORED'
STORAGE_STATUS_EXISTS = 'EXISTS'
STORAGE_STATUS_NOT_FOUND = 'NOT_FOUND'
STORAGE_STATUSES = set([STORAGE_STATUS_STORED, STORAGE_STATUS_NOT_STORED, STORAGE_STATUS_EXISTS, STORAGE_STATUS_NOT_FOUND])

DELETION_STATUS_DELETED = 'DELETED'
DELETION_STATUS_NOT_FOUND = 'NOT_FOUND'
DELETION_STATUSES = set([DELETION_STATUS_DELETED, DELETION_STATUS_NOT_FOUND])

VALUE_READ_TIMEOUT = 60

class ClientError(Exception): pass
class ServerError(Exception): pass

def register_all_commands(cls):
    if cls._commands is None:
        cls._commands = {}

    for _, method in cls.__dict__.iteritems():
        if hasattr(method, "memcacheliked_command"):
            cls._commands[method.memcacheliked_command] = method

    return cls

class Memcacheliked(object):
    _commands = None

    def __init__(self, timeout=60*60):
        self.timeout = timeout
        for cn in self._commands:
            self._commands[cn] = types.MethodType(self._commands[cn], self, Memcacheliked)

    def connection_handler(self, address):
        try:
            log.info('got incoming connection from <%s>' % (address,))
            while True:
                ev, msg = first(until_eol = True, sleep = self.timeout)
                if ev == 'sleep':
                    log.warn('connection to <%s> timed out' % (address,))
                    break
                else:
                    elements = msg[:-2].split(' ')

                    log.debug('got command parts <%s>' % (elements,))

                    command_name = elements[0]
                    if self._commands is not None and command_name in self._commands:
                        try:
                            self._commands[command_name](*elements)
                        except ServerError as e:
                            send("SERVER_ERROR %s\r\n" % (e.args[0],))
                        except ClientError as e:
                            send("CLIENT_ERROR %s\r\n" % (e.args[0],))
                        except Exception as e:
                            log.critical('got exception, <%s>' % (traceback.format_exc(),))
                            send("SERVER_ERROR internal exception\r\n" % (e.args[0],))
                    else:
                        log.critical('command <%s> unknown' % (command_name,))
                        send("ERROR\r\n")

        except Exception as e:
            log.critical('got exception, <%s>' % (traceback.format_exc(),))
            send("SERVER_ERROR internal exception\r\n")

    def start(self, port=11211):
        app = Application()
        app.add_service(Service(self.connection_handler, port))
        app.run()


def ident(*args):
    return args


def _register_command(f, process_result, process_values=ident, name=None, min_args=None):
    @wraps(f)
    def wrapper(*elements):
        if len(elements) < min_args:
            raise ClientError("not enough parameters (got %s)" % (elements,))

        return process_result(f(*process_values(*elements)))

    if name is None:
        name = f.func_name
        if name.startswith('command_'):
            name = name[len('command_'):]

    wrapper.memcacheliked_command = name
    return wrapper


def storage_command(name=None):
    def wrapping(f):
        def process_result(res):
            if res not in STORAGE_STATUSES: 
                raise ServerError("internal error")
            else:
                send(res + "\r\n")

        def process_values(*elements):
            ev, msg = first(receive = int(elements[5])+2, sleep = VALUE_READ_TIMEOUT)
            if ev == 'sleep':
                raise ClientError("reading timed out")
            else:
                new_elements = list(elements)
                new_elements[5] = msg[:-2]
                return tuple(new_elements)

        return _register_command(f, process_result, process_values=process_values, name=name, min_args=5)
    return wrapping

def retrieval_command(name=None):
    def wrapping(f):
        def process_result(res):
            if not hasattr(res, '__iter__'):
                raise ServerError("internal error")
            else:
                for row in res:
                    if type(row) != tuple or len(row) < 3:
                        log.crit("Engine didn't return proper tuple, but <%s> - skipping" % (row,))
                    elif row[2] is not None:
                        send('VALUE %s %s %i%s\r\n%s\r\n' % (row[0], row[1], len(row[2]), '' if len(row)<4 else ' '+row[3], row[2]))
                    else:
                        pass
                        # key not present, no answer
                send('END\r\n')
                        
        return _register_command(f, process_result, name=name, min_args=2)
    return wrapping

def deletion_command(name=None):
    def wrapping(f):
        def process_result(res):
            if res not in DELETION_STATUSES: 
                raise ServerError("internal error")
            else:
                send(res + "\r\n")
        return _register_command(f, process_result, name=name, min_args=2)
    return wrapping

