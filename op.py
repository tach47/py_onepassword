#!/usr/bin/env python3

import json
import os
import subprocess
import sys

import tomllib


currDir = os.path.dirname(os.path.realpath(__file__))


with open("%s/1password.toml" % currDir, "rb") as f:
    OP_VARS = tomllib.load(f)
OP_ACCOUNT = OP_VARS['1password']['account_name']
OP_DEFAULT_VAULT = OP_VARS['1password']['vault_name']
OP_VAULT = OP_DEFAULT_VAULT
SESSION_ID = ''
VAULT_UUID = ''


def initialize():
    get_vault_info(OP_VAULT)


def get_vault_info(vault_name):
    global VAULT_UUID
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
    command = 'op item list --vault "%s" --format=json' % vault_name
    status, output = call_op(command)
    for item in output:
        items['%s' % item['title']] = item['id']
    return items


def get_item_by_uuid(uuid):
    item = {}
    command = 'op item get %s --format=json' % uuid
    status, output = call_op(command)
    for field in output['fields']:
        try:
            item['%s' % field['label']] = field['value']
        except:
            next
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
    status, output = call_op(command)
    if status != 0:
        sys.exit('Unable to login')
    else:
        return output


def get_password(search):
    secret = ''
    uuid = search_for_uuid(search)
    secret = get_item_by_uuid(uuid)
    return secret['password']


def get_username(search):
    secret = ''
    uuid = search_for_uuid(search)
    secret = get_item_by_uuid(uuid)
    return secret['username']

def call_op(command):
    status, output = subprocess.getstatusoutput(command)
    try:
        if status == 0:
            returned_output = json.loads(output)
        else:
            returned_output = {}
    except json.decoder.JSONDecodeError:
        print(output)
    return (status, returned_output)

