#!/usr/bin/env python
# coding=utf-8
"""This script uploads a plugin package on the server.
        Authors: A. Pasotti, V. Picavet
        git sha              : $TemplateVCSFormat
"""

import getpass
import sys
import xmlrpclib
from optparse import OptionParser

# Configuration
PROTOCOL = "http"
SERVER = "plugins.qgis.org"
PORT = "80"
ENDPOINT = "/plugins/RPC2/"
VERBOSE = False


def main(parameters, arguments):
    """Main entry point.

    :param parameters: Command line parameters.
    :param arguments: Command line arguments.
    """
    address = "%s://%s:%s@%s:%s%s" % (
        PROTOCOL,
        parameters.username,
        parameters.password,
        parameters.server,
        parameters.port,
        ENDPOINT,
    )
    print("Connecting to: {}".format(hide_password(address)))

    server = xmlrpclib.ServerProxy(address, verbose=VERBOSE)

    try:
        plugin_id, version_id = server.plugin.upload(xmlrpclib.Binary(open(arguments[0]).read()))
        print("Plugin ID: {}".format(plugin_id))
        print("Version ID: {}".format(version_id))
    except xmlrpclib.ProtocolError as err:
        print("A protocol error occurred")
        print("URL: {}".format(hide_password(err.url, 0)))
        print("HTTP/HTTPS headers: {}".format(err.headers))
        print("Error code: {}".format(err.errcode))
        print("Error message: {}".format(err.errmsg))
    except xmlrpclib.Fault as err:
        print("A fault occurred")
        print("Fault code: {}".format(err.faultCode))
        print("Fault string: {}".format(err.faultString))


def hide_password(url, start=6):
    """Returns the http url with password part replaced with '*'.

    :param url: URL to upload the plugin to.
    :type url: str

    :param start: Position of start of password.
    :type start: int
    """
    start_position = url.find(":", start) + 1
    end_position = url.find("@")
    return "%s%s%s" % (
        url[:start_position],
        "*" * (end_position - start_position),
        url[end_position:],
    )


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [options] plugin.zip")
    parser.add_option(
        "-w", "--password", dest="password", help="Password for plugin site", metavar="******"
    )
    parser.add_option(
        "-u", "--username", dest="username", help="Username of plugin site", metavar="user"
    )
    parser.add_option("-p", "--port", dest="port", help="Server port to connect to", metavar="80")
    parser.add_option(
        "-s", "--server", dest="server", help="Specify server name", metavar="plugins.qgis.org"
    )
    options, args = parser.parse_args()
    if len(args) != 1:
        print("Please specify zip file.\n")
        parser.print_help()
        sys.exit(1)
    if not options.server:
        options.server = SERVER
    if not options.port:
        options.port = PORT
    if not options.username:
        # interactive mode
        username = getpass.getuser()
        print("Please enter user name [{}] :".format(username))
        res = raw_input()
        if res != "":
            options.username = res
        else:
            options.username = username
    if not options.password:
        # interactive mode
        options.password = getpass.getpass()
    main(options, args)
