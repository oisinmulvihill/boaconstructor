==============
BoaConstructor
==============

:URI: http://pypi.python.org/pypi/boaconstructor

.. contents::


What is it?
============

The boacontructor is a templating library for *data*. It allows you to construct
Python_ dictionaries from other templates, dictionaries or instances.


Quickstart
==========

Two quick examples should give a feel for how boaconstructor works.


Basic Example
-------------

I'll let the code and comments do the talking.

.. code-block:: python

    from boaconstructor import Template

    # Some shared information in a dict. This could also be a class instance
    # or something else that supports getattr and hasattr.
    #
    common = dict(
        timeout = 30,
        email = "admin@example.com"
    )

    # This is a template created in a module. You need one of these. I pass in
    # references that are available at this stage. The 'host.$.name' I will pass
    # in at render time.
    #
    webserver_data = Template('webserver',
        dict(
            interface = 'host.$.name',
            port = 32189,
            timeout = 'common.$.timeout',
            alert_email = 'common.$.email',
        ),
        # This is uses common as an 'internal' reference
        references={'common':common}
    )

    # At run time I can pass 'external' references to resolve the hostnames.
    # Maybe I got these from a database or some other source.
    #
    machine_1 = webserver_data.render({'host': {'name': 'myserver1'}}),
    # {'alert_email': 'admin@example.com', 'interface': 'myserver1', 'port': 32189, 'timeout': 30}

    machine_2 = webserver_data.render({'host': {'name': 'myserver2'}}),
    # {'alert_email': 'admin@example.com', 'interface': 'myserver2', 'port': 32189, 'timeout': 30}


    # Now I can pass these to Cheetah/Mako/etc to render a specific type of
    # XML/INI/Text configuration files.



Complex Example
---------------

This shows the construction of a dictionary which make use of referencing,
inclusion and extension.

.. code-block:: python

    import pprint

    from boaconstructor import Template

    common = dict(keep='yes', buffer=4096, timeout=30)

    peter = dict(username='pstoppard', secret='11ed394')
    graham = dict(username='gturner', secret='54jsl31')

    test1 = Template(
        'test1',
        dict(
            name='production',
            options='common.*',
            usernames=['peter.$.username','graham.$.username'],
            users=['peter.*', 'graham.*'],
        ),
    )

    # This entire template will get added to test1 when rendered. This also
    # shows how test1 will fill out place holders for the keys it provides.
    #
    search = dict(
        name = '<over written in rendered output>',
        search = 'google.com',
        timeout = 'common.$.timeout'
    )

    result = test1.render(
        references={
            'common': common,
            'peter': peter,
            'graham': graham,
        },
        derivefrom=search,
    )

    pprint.pprint(result)
    {'name': 'production',
     'options': {'buffer': 4096, 'timeout': 30, 'keep': 'yes'},
     'search': 'google.com',
     'timeout': 30,
     'usernames': ['pstoppard', 'gturner'],
     'users': [{'username': 'pstoppard', 'secret': '11ed394'},
               {'username': 'gturner', 'secret': '54jsl31'}]}




How does it work?
=================

The library uses dictionary string values in a particular format. Each format
indicates what should be recovered and assigned.

There are two types of strings that are recognised. A reference-attribute string
and an all-inclusion string. The power and flexibilty of the template system
comes from how these two types are used.


Reference-Attribute
-------------------

I usually refer to this as a 'refatt' string. It is defined as follows::

    <reference string>.$.<attribute string>

The '.$.' is the deliminator used to work out which part is the reference and
attribute. There must be something either side of the refatt deliminator of the
string is ignored.



All-Inclusion
-------------

I usually refer to this as a 'allinc' string. It is defined as follows::

    <inclusion string>.*

The '.*' is the deliminator at the end of a string. Nothing must appear after
the allinc '.*' or the string will be ignored.






Project Documentation
=====================

.. automodule:: boaconstructor


GitHub Code Repository
----------------------

 * GitHub project: https://github.com/oisinmulvihill/boaconstructor


PyPi Project
------------

 * Pypi page: http://pypi.python.org/pypi/boaconstructor



.. _Python: http://www.python.org/



License
=======

Copyright 2011 Oisin Mulvihill

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

