#!/usr/bin/env python
# -*- coding: utf-8 -*-  
# Firebird Nagios plugin
#
# A plugin for Nagios which checks the firebird connection to a specific host
# by connecting to it and executing an SQL Statement which should return all
# relations between the tables which are in the database, be aware if you have
# an empty database without any tables you will get a critical error.
#
# Based on a template from
# http://bsd.dischaos.com/2009/04/29/nagios-plugin-template-in-python/
#
# Requirements :
#    fdb
#
# Example :
#    check_firebird.py -h 192.168.1.1 -a employee -u sysdba -p masterkey -d 3050 
#
#
__author__  = 'Frank Lazzarini'
__contact__ = 'flazzarini at gmail.com'
__version__ = '0.4.0'
__license__ = 'GPLv3'
 
try:
    import fdb
except ImportError, _:
    pass
 
import sys, getopt, socket
 
 
NAGIOS_CODE = {'OK': 0,
               'WARNING': 1,
               'CRITICAL': 2,
               'UNKNOWN': 3,
               'DEPENDENT': 4}
 
 
def usage():
    """
    Show Usage

    Returns the nagios status UNKOWN with a usage description
    """
    nagios_return('UNKNOWN',
                  'usage: {0} -h <host> -a <alias> -u <username> -p <password>'
                  ' -d <optional destionport default:3050)'.format(sys.argv[0]))
 
 
def nagios_return(code, response):
    """
    Prints the response message and exits the script with one of the defined
    exit codes.
    """
    print code + ': ' + response
    sys.exit(NAGIOS_CODE[code])
 
 
def check_condition(host, destport, alias, username, password):
    """
    Tries to connect to the given firebird database and execute a SQL statement
    which should return a list of available tables. Be aware this doesn't
    work if your database has no tables.

    @param host    : hostname/ip
    @param alias   : database alias
    @param username: username
    @param password: password
    """
    try :
        dsnstring  = host + "/" + destport + ":" + alias
        connection = fdb.connect(dsn=dsnstring,
                                 user=username,
                                 password=password)
        connection.begin()
        version = connection.server_version
 
        # Execute an sql on the connection
        cur = connection.cursor()
        cur.execute('SELECT DISTINCT RDB$RELATION_NAME FROM RDB$RELATION_FIELDS'
                    ' WHERE RDB$SYSTEM_FLAG=0;')
 
        if len(cur.fetchall()) < 1:
            connection.close()
            return {'code': 'CRITICAL',
                    'message': dsnstring + ' problem with the database,'
                                           ' maybe corrupted!'}
        connection.close()
 
    except fdb.OperationalError, msg:
        return {'code': 'CRITICAL',
                'message': dsnstring + ' ' + msg[1].rstrip('\n')}
 
    return {'code': 'OK', 'message': host + ' Version:' + version}
 
 
def is_valid_ipv4_address(address):
    """
    Returns true if IP address is in a valid ipv4 format
    """
    try:
        addr = socket.inet_pton(socket.AF_INET, address)
    except AttributeError: # no inet_pton here, sorry
        try:
            addr = socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error: # not a valid address
        return False
 
    return True
 
def is_valid_ipv6_address(address):
    """
    Returns true if IP address is in a valid ipv6 format
    """
    try:
        addr = socket.inet_pton(socket.AF_INET6, address)
    except socket.error: # not a valid address
        return False
    return True
 
 
def main():
    """
    Check if argument length is not less than 5 which means that 
    "-h <host> -a <alias>" must be given as a parameter otherwise
    the script will print the usage description using nagios_return()
    function, else parse/verify the parameters
    """
    if len(sys.argv) < 8:
        usage()
 
    try:
        opts , args = getopt.getopt(sys.argv[1:],
                                    'h:a:u:p:d:',
                                    ['host=',
                                     'pass=',
                                     'alias=',
                                     'user=',
                                     'password=',
                                     'destport='])
    except getopt.GetoptError:
        usage()
 
    # If destport is not given an argument assume 
    # default Firebird Port 3050
    if not ('-d', '--destport') in opts:
        destport = '3050'
 
    # Run through the opts and get the parameters
    for o, value in opts:
        if o in ('-h', '--host'):
            if not is_valid_ipv4_address(value): 
                nagios_return('UNKNOWN',
                              value + ' is not a valid ipv4 address.'.format(sys.argv[0]))
            else :
                host = value
        elif o in ('-a', '--alias'):
            dbalias = value
        elif o in ('-u', '--user'):
            username = value
        elif o in ('-p', '--pass'):
            password = value
        elif o in ('-d', '--destport'):
            destport = value
        else:
            usage()
 
    result = check_condition(host, destport, dbalias, username, password)
    nagios_return(result['code'], result['message'])
 
if __name__ == '__main__':
    main()
