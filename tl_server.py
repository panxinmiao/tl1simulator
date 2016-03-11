#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import threading
import web_server
import os

try:
    import configparser as cp
except ImportError:
    import ConfigParser as cp

try:
    import socketserver as ss
except ImportError:
    import SocketServer as ss
import tl_result


__author__ = 'Pan Xinmiao'


def get_response(command):
    regex = r'^(.+)::(.*):(\d+)::(.*);$'
    m = re.match(regex, command)
    if m:
        code, pos, ctag, params = m.groups()
        data = tl_result.get_response(code, pos, ctag, params)
    else:
        data = tl_result.get_unknown_cmd().get('text').replace('\n', '\r\n')

    return data


class TLHandler(ss.StreamRequestHandler):
    def read_command(self):
        line = self.rfile.readline().strip().decode('utf-8')
        while not line or line[-1] != ';':
            line = line + self.rfile.readline().strip().decode('utf-8')
        return line

    def commands(self):
        while True:
            yield self.read_command()

    def handle(self):
        print('connected from ',self.client_address)
        commands = self.commands()
        while True:
            line = next(commands)
            # print('%s <======== %s' %(self.client_address, line))
            res = get_response(line)
            self.wfile.write(('%s\r\n' % res).encode('utf-8'))
            # print('%s ========> %s' %(self.client_address, res))


class AdminHandler(ss.StreamRequestHandler):
    def read_command(self):
        line = self.rfile.readline().strip().decode('utf-8')
        return line

    def commands(self):
        while True:
            yield self.read_command()

    def handle(self):
        print('connected from ',self.client_address)
        self.wfile.write(b'Welcome!\r\n==>')
        commands = self.commands()
        while True:
            line = next(commands)
            # print('%s <======== %s' %(self.client_address, line))
            res = ''
            if line == 'reload':
                tl_result.init_commands()
                res = 'config reloaded'
            elif line == 'list':
                for k in tl_result.get_commands():
                    res += k+'\r\n'
            else:
                res = ''

            self.wfile.write(('%s\r\n==>' % res).encode('utf-8'))
            # print('%s ========> %s' %(self.client_address, res))


if __name__ == "__main__":
    tl_result.init_commands()
    HOST = "0.0.0.0"
    cf = cp.ConfigParser()
    if os.path.exists("tl_server.ini"):
        cf.read("tl_server.ini")
    else:
        cf.add_section("Port")
        cf.set("Port", "tl_port", '9822')
        cf.set("Port", "admin_port", '9999')
        cf.set("Port", "web_port", '8888')
        cf.write(open("tl_server.ini", "w"))

    tl_port = int(cf.get("Port", "tl_port"))
    admin_port = int(cf.get("Port", "admin_port"))
    web_port = int(cf.get("Port", "web_port"))
    tl_server = ss.ThreadingTCPServer((HOST, tl_port), TLHandler)
    t1 = threading.Thread(target= tl_server.serve_forever)
    t1.start()

    admin_server = ss.ThreadingTCPServer((HOST, admin_port), AdminHandler)
    t2 = threading.Thread(target= admin_server.serve_forever)
    t2.start()
    web_server.app.run(HOST, web_port, use_debugger=True, debug=False)








