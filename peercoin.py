"Peercoin Blockchain - Database for The Great Library of Peercoin."

import base64
import json
from os.path import expanduser
from random import randint
from time import time
from urllib.request import Request, urlopen


def get_ppcoin_conf_settings():
    'Returns a dictionary of settings from the peercon config file.'
    settings = {
        'rpcuser': None,
        'rpcpassword': None,
        'port': None,
    }

    with open(expanduser('~') + '/.ppcoin/ppcoin.conf') as conf_file:
        conf_lines = conf_file.readlines()

    for conf_line in conf_lines:

        parts = conf_line.strip().split("=", 1) # up to 2 parts

        if parts[0] == 'rpcport':
            settings['port'] = int(parts[1])

        elif parts[0] == 'rpcuser':
            settings['rpcuser'] = parts[1]

        elif parts[0] == 'rpcpassword':
            settings['rpcpassword'] = parts[1]

    return settings


def call_peercoin_rpc(command, *args):
    '''Returns a dictionary of the peercoin rpc result for the passed command
    and arguments.
    '''
    request = {
        'id': str(time())+'-'+str(randint(100000,999999)),
        'method': command,
        'params': args,
    }

    settings = get_ppcoin_conf_settings()

    rpcuser = settings['rpcuser']
    rpcpassword = settings['rpcpassword']
    port = settings['port'] if settings['port'] else 9902

    if not rpcuser or not rpcpassword:
        raise Exception('"rpcuser" and "rpcpassword" must be set in your ppcoin.conf file.')

    url = 'http://127.0.0.1:' + str(port) + '/'

    request = Request(url, json.dumps(request).encode('utf-8'))

    user_password = base64.encodestring(('%s:%s' % (rpcuser, rpcpassword)).encode('utf-8')).decode().replace('\n','')
    request.add_header('Authorization','Basic %s' % user_password)

    response = json.loads(urlopen(request).read().decode('utf-8'))

    return response['result']
