#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import threading
import os
import tl_server

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


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def show_entries():
    commands = tl_result.get_commands()
    entries = [dict(title=code, text=commands.get(code)) for code in commands]
    return render_template('show_entries.html', entries=entries)


@app.route('/reload', methods=['GET'])
def reload():
    tl_result.init_commands()
    flash('配置文件重载成功')
    return redirect(url_for('show_entries'))


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

    command_server = ss.ThreadingTCPServer((HOST, tl_port), tl_server.TLHandler)
    t1 = threading.Thread(target= command_server.serve_forever)
    t1.start()

    admin_server = ss.ThreadingTCPServer((HOST, admin_port), tl_server.AdminHandler)
    t2 = threading.Thread(target= admin_server.serve_forever)
    t2.start()

    app.run('0.0.0.0', web_port, use_debugger=True, debug=False)
