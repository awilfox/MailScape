import configparser
from os.path import expanduser as expand_tilde

config = None

def read_config_in():
    global config

    config = configparser.ConfigParser()
    config.read(expand_tilde('~/.mailscape.cfg'))

def configure_server(server_name, friendly_name, user, pw):
    config['servers'][server_name] = friendly_name
    config[server_name]['user'] = user
    config[server_name]['password'] = pw
    config.write(expand_tilde('~/.mailscape.cfg'))

def configured_servers():
    if config is None:
        read_config_in()

    if 'servers' not in config:
        return {}

    return config.items('servers')

def server_config(server_name):
    if config is None:
        read_config_in()

    return config[server_name]
