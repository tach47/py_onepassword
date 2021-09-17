#!/usr/bin/env python3

import json
import os
import subprocess
import sys

import toml


currDir = os.path.dirname(os.path.realpath(__file__))

OP_VARS = toml.load('%s/1password.toml' % currDir)
OP_ACCOUNT = OP_VARS['1password']['account_name']
OP_DEFAULT_VAULT = OP_VARS['1password']['vault_name']
OP_VAULT = OP_DEFAULT_VAULT
SESSION_ID = ''
VAULT_UUID = ''


def initialize():
    global SESSION_ID
    try:
        SESSION_ID = os.environ['OP_SESSION_%s' % OP_ACCOUNT]
        check_login()
    except KeyError:
        check_login()
    get_vault_info(OP_VAULT)


def check_login():
    global SESSION_ID
    command = 'op signin --raw --session %s' % SESSION_ID
    status, output = call_op(command, 'plaintext')
    if status == 0:
        SESSION_ID = output
        os.environ['OP_SESSION_%s' % OP_ACCOUNT] = output
        return True
    else:
        try:
            SESSION_ID = login()
            if len(SESSION_ID) > 0:
                return True
        except:
            sys.exit('Exit code %s: %s' % (status, output))


def get_vault_info(vault_name):
    global VAULT_UUID
    check_login()
    vaults = get_vaults()
    vault_info = {}
    try:
        if len(VAULT_UUID) == 0:
            VAULT_UUID = vaults['%s' % vault_name]
    except KeyError:
        from pprint import pprint 
        pprint(vaults.keys())
        sys.exit('Invalid vault_name listed in 1password.toml')
    command = 'op get vault %s' % VAULT_UUID
    status, output = call_op(command)
    vault_info = output
    return vault_info


def get_vaults():
    vault_ids = {}
    command = 'op list vaults'
    status, output = call_op(command)
    for vault in output:
        vault_ids['%s' % vault['name']] = '%s' % vault['uuid']
    return vault_ids


def get_items(vault_name):
    items = {}
    command = 'op list items --vault "%s"' % vault_name
    status, output = call_op(command)
    for item in output:
        items['%s' % item['overview']['title']] = item['uuid']
    return items


def get_item_by_uuid(uuid):
    item = {}
    command = 'op get item %s' % uuid
    status, output = call_op(command)
    for field in output['details']['fields']:
        item['%s' % field['designation']] = field['value']
    return item


def search_for_uuid(search):
    items = get_items(OP_VAULT)
    for item in items:
        if search in item:
            return items['%s' % item]
        else:
            continue
    return ''


def login():
    command = 'op signin --raw'
    status, output = call_op(command, 'plaintext')
    if status != 0:
        sys.exit('Unable to login')
    else:
        return output


def get_password(search):
    check_login()
    secret = ''
    uuid = search_for_uuid(search)
    secret = get_item_by_uuid(uuid)
    return secret['password']


def get_username(search):
    check_login()
    secret = ''
    uuid = search_for_uuid(search)
    secret = get_item_by_uuid(uuid)
    return secret['username']


def call_op(command, format='JSON'):
    status, output = subprocess.getstatusoutput(command)
    try:
        if status == 0:
            if format == 'plaintext':
                returned_output = output
            else:
                returned_output = json.loads(output)
        else:
            returned_output = {}
    except json.decoder.JSONDecodeError:
        print(output)
    return (status, returned_output)
