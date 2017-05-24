#!/usr/bin/env python
from __future__ import unicode_literals
from __future__ import print_function

import shutil
import os
import errno
import requests
import json
import sys

from prompt_toolkit import prompt
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.validation import Validator, ValidationError


import op1

# http://python-prompt-toolkit.readthedocs.io/en/stable/pages/building_prompts.html
# https://github.com/jonathanslenders/python-prompt-toolkit/tree/master/examples/tutorial

def mkdir_p(path):
    """
    recursively create directories
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

class OP1Config(object):
    def __init__(self):
        self.configpath = os.path.expanduser('~/.op1fun.json')
        self.config = self._load_config()

    def _load_config(self):
        try:
            with open(self.configpath, 'r') as f:
                return json.loads(f.read())
        except IOError:
            print("Hey dude, you need a config file!")
            print("got you covered, i placed a sample in %s. Make sure to fill it out" % self.configpath)

            # sample config ~/.op1fun.json'
            sample_config = """
            {
              "baseurl": "https://api.op1.fun/v1",
              "mail": "yourmail@example.com",
              "token": "GETITFROMYOURPROFILE",
              "username": "yourusername"
            }
            """
            with open(self.configpath, 'w') as f:
                f.write(sample_config)
            sys.exit(1)


class OP1Fun(object):
    def __init__(self):
        self.config = OP1Config().config
        s = requests.Session()
        s.headers.update({'x-user-email': self.config['mail'], 'x-user-token': self.config['token']})
        self.session = s

        self.op1device = op1.OP1Device()

        self.login_ok()

    def login_ok(self):
        url = "%s/users/%s" % (self.config['baseurl'], self.config['username'])
        r = self.session.get(url)
        if r.status_code == requests.codes.ok:
            return True
        else:
            raise ValueError('Looks like your config is wrong. Error returned:\n %s' % (r.text))


    def get_packs(self):
        packlist = []
        url = "%s/users/%s/packs" % (self.config['baseurl'], self.config['username'])
        r = self.session.get(url)

        for i in r.json()['data']:
            #print(i['attributes']['user-id'], i['attributes']['name'])
            # names and ids differ. that sucks. need to implement that here somehow
            packlist.append(i['attributes']['name'])
            #print(i['attributes'])
        return packlist

    def get_pack(self, packid):
        url = "%s/users/%s/packs/%s" % (self.config['baseurl'], self.config['username'], packid)
        r = self.session.get(url)

        pack = r.json()
        packname = pack['data']['attributes']['name']
        for patch in pack['included']:
            patchtype = patch['attributes']['patch-type']
            if patchtype in ['sampler', 'synth']:
                patchdir = 'synth'
            elif patchtype in ['drum']:
                patchdir = 'drum'
            else:
                patchdir = 'synth'
                #raise ValueError('no idea what to do with %s' % patchtype)

            # make sure the OP-1 is mounted and connected
            mountpoint = self.op1device.mount()
            filepath = "%s/%s/%s" % (mountpoint, patchdir, packname)
            filename = "%s.aif" % patch['attributes']['name']
            fullpath = "%s/%s" % (filepath, filename)

            mkdir_p(filepath)
            print("storing for pack %s to %s as %s - %s" % (packname, patchdir, filename, fullpath))
            self.download_file(patch['links']['file'], fullpath)
        return pack

    def download_file(self, url, filepath):
        """
        downloads a file and stores it at some place
        """
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)


style = style_from_dict({
    Token.Toolbar: '#ffffff bg:#333333',
})

class StringValidator(Validator):
    def validate(self, document):
        text = document.text
        print(text)

        if text and len(text) < 3:
            raise ValidationError(message='At least 3 chars required')


class OP1Runner(object):
    def __init__(self):
        self.of = OP1Fun()

        self.history = InMemoryHistory()

    def get_bottom_toolbar_tokens(self, cli):
        return [(Token.Toolbar, 'OP-1 connected: %s' % self.of.op1device.is_ready())]

    def main(self):
        pack_completer = WordCompleter(self.of.get_packs())

        packname = prompt(
            'Enter name of the pack (you can use tab for completion): ',
            completer=pack_completer,
            get_bottom_toolbar_tokens=self.get_bottom_toolbar_tokens,
            style=style,
            history=self.history,
            validator=StringValidator()
        )
        print('Installing %s to your OP-1' % packname)
        if not self.of.op1device.is_ready():
            print('Hey your OP-1 is not connected')
            sys.exit(1)
        else:
            self.of.get_pack(packname)

if __name__ == "__main__":
    orunner = OP1Runner()
    orunner.main()






#
# api = jsonapi_requests.Api.config({
#  'API_ROOT': 'https://api.op1.fun/v1',
#  'AUTH': ('basic_auth_login', 'basic_auth_password'),
#  'VALIDATE_SSL': False,
#  'TIMEOUT': 5,
# })
#
#
# endpoint = api.endpoint('users/webratz/packs')
#
# response = endpoint.get(headers={
#                 'Content-Type': 'application/vnd.api+json',
#                 'Accept': 'application/vnd.api+json',
#                 'x-user-email': config['mail'],
#                 'x-user-token': config['token']
#            })
