==============
BoaConstructor
==============

:URI: http://pypi.python.org/pypi/boaconstructor

.. contents::


What is it?
============

The boacontructor is a templating library for *data*. It allows you to construct
Python_ dictionaries from other Template instances, dictionaries or object
instances.


How does it work?
=================

The library uses dictionary string values in a particular format. Each format
indicates what should be recovered and assigned. The top level data template
must be a dictionary. The operations can be nested meaning an operation string
can resolve to point at another operation.

There are three types of operation strings which are recognised. A
reference-attribute, all-inclusion or a derivefrom string. The power and
flexibilty of the template system comes from how and where these are used.


Reference-Attribute
-------------------

I usually refer to this as a 'refatt' string. It is defined as follows::

    <reference string>.$.<attribute string>

The '.$.' is the deliminator used to work out which part is the reference and
attribute. There must be something either side of the refatt deliminator or the
string is ignored.

Example:

.. code-block:: python

    # reference "common" data:
    common = {"timeout": 10}

    # Template
    {
      "timeout": "common.$.timeout",
    }

    # Render time result:
    {
      "timeout": 10,
    }

The timeout string value is interpreted as find the value of "timeout", which is
an attribute of the reference "common". When the dict is "rendered" timeout will
contain the value 10. The type of the resolved value is preserved.


All-Inclusion
-------------

I usually refer to this as a 'allinc' string. It is defined as follows::

    <inclusion string>.*

The '.*' is the deliminator at the end of a string. Nothing must appear after
the allinc '.*' or the string will be ignored.

For Example:

.. code-block:: python

    machine = {"address": '127.0.0.1', "port": 8080}

    # Template
    {
      "host": "machine.*",
    }

    # Render time result
    {
      "host": {"address": '127.0.0.1', "port": 8080}
    }

The value of "host" becomes whatever machine resolves as.

There is currently no restriction on machine being a dict. Anything machine
points at will be placed as-is. This could be another data type for example
string, number, list.

Where the value pointed at is a dictionary, it will be processed until all its
references are resolved. The result of this processing will then become the
value.

For example:

.. code-block:: python

  common = {"timeout": 10}

  machine = {"address": '127.0.0.1', "port": 8080, "wait": 'common.$.timeout'}

  # Template
  {
    "machine": "machine.*",
  }

  # Render time result
  {
    "machine": {"address": '127.0.0.1', "port": 8080, "wait": 10}
  }


Derive-From
-----------

It is defined as follows::

    derivefrom.[<reference string>]

The reference string between the [] brackets referes to the data which will be
derived from.

For example:

.. code-block:: python

    common = {"timeout": 10}

    # The "base" data:
    machine = {"address": 'localhost', "port": 8080, "wait": 'common.$.timeout'}

    # Template (child of parent base):
    {
      "": "derivefrom.[machine]",
      "address": "example.com"
    }

    # Render time result
    {
      "address": 'example',
      "port": 8080,
      "wait": 10
    }

The template derives from machine and then overrides the address. Multiple
derivefrom operations are not supported. Only one can be used. By convention the
key of a derivefrom is left empty or used as a comment.


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

This shows the construction of a dictionary which makes use of
reference-attributes, all inclusion and derive from.

.. code-block:: python

    import pprint

    from boaconstructor import Template

    common = dict(keep='yes', buffer=4096, timeout=30)

    peter = dict(username='pstoppard', secret='11ed394')
    graham = dict(username='gturner', secret='54jsl31')

    # "base" data test1 will derive from an provide an
    # alternative name
    search = dict(
        name = '<over written in rendered output>',
        search = 'google.com',
        timeout = 'common.$.timeout'
    )

    test1 = Template(
        'test1',
        {
            "": "derivefrom.[search]",
            "name": 'production',
            "options": 'common.*',
            "usernames": ['peter.$.username','graham.$.username'],
            "users": ['peter.*', 'graham.*'],
        },
    )

    result = test1.render(
        references={
            'common': common,
            'peter': peter,
            'graham': graham,
            'search': search,
        },
    )

    pprint.pprint(result)
    {'name': 'production',
     'options': {'buffer': 4096, 'timeout': 30, 'keep': 'yes'},
     'search': 'google.com',
     'timeout': 30,
     'usernames': ['pstoppard', 'gturner'],
     'users': [{'username': 'pstoppard', 'secret': '11ed394'},
               {'username': 'gturner', 'secret': '54jsl31'}]}



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
