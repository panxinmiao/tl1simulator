#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time
try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


__author__ = 'Pan Xinmiao'


__commands = {}


def init_commands():
    __commands.clear()
    if not os.path.exists('commands'):
        os.mkdir('commands')
    files = [x for x in os.listdir('commands') if os.path.isfile(os.path.join('commands', x)) and os.path.splitext(x)[1] == '.xml']
    for file in files:
        try:
            tree = ET.parse(os.path.join('commands', file))
            root = tree.getroot()
            command = root.find('Service').find('Commond')
            code = command.get('code')
            results = [{'match' : result.get('match'), 'text' : result.text} for result in command.findall('CommodResult')]
            __commands[code] = results
        except Exception as e:
            print("Error:cannot parse file: %s" % file)


def get_commands():
    return __commands


def match(pos, params):
    def f(result):
            return result.get('match') and (result.get('match') in pos or result.get('match') in params)
    return f


def get_unknown_cmd():
    return __commands.get('CMD-NOT-FOUND::')[0]


def get_result(code, pos, ctag, params):
    results = __commands.get(code+'::')
    if not results:
        return get_unknown_cmd()
    match_res = list(filter(match(pos, params), results))
    if match_res:
        return match_res[0]
    else:
        return next(filter(lambda x: not x.get('match'), results))


def get_current_time():
    return time.strftime('%Y-%m-%d %X', time.localtime())


def get_response(code, pos, ctag, params):
    result = get_result(code, pos, ctag, params)
    res = result.get('text').replace('\n', '\r\n')
    pdict = {'M': ctag, 'CurrentTime': get_current_time()}
    entry = []
    if pos:
        entry += pos.split(',')
    if params:
        entry += params.split(',')

    for e in entry:
        p = e.split('=')
        if len(p) < 2:
            print('-------%s--------' % p)
        else :
            pdict[p[0]] = p[1]

    for pk in pdict:
        res = res.replace('%{'+pk+'}%', pdict.get(pk))

    return res.replace('\n', '\r\n')


if __name__ == "__main__":
    init_commands()
    for k in __commands:
        print(k)
        print(__commands[k])