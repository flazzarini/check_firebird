check_firebird
==============

A nagios plugin to check firebird database connectivity. Following is a sample nagios configuration for this service.

Requirements
------------

::

    pip install fdb


Example Nagios configuration
----------------------------
::

    define command{
            command_name    check_firebird
            command_line    pathto/check_firebird.py -h '$HOSTADDRESS$' -a '$ARG1$' -u '$ARG2$' -p '$ARG3$' -d '$ARG4$'
    }
    
    define host {
            use          generic-host
            host_name    fb21
            alias        fb21
            address      127.0.0.1
    }

    define service {
            use                    generic-service
            host_name              fb21
            service_description    FIREBIRD-test
            check_command          check_firebird!test!sysdba!masterkey  
            ;Optional you could put !3051 for a different port
    }
