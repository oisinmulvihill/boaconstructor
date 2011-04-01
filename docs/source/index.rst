==============
BoaConstructor
==============

:URI: http://pypi.python.org/pypi/boaconstructor

.. contents::


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


What is it?
============

The boacontructor is a templating library for *data*. It allows you to construct
Python_ dictionaries from other templates, dictionaries or instances.


How does it work?
=================

The library uses dictionary string values in a particular format. Each format
indicates what should be recovered and assigned.

For example

.. code-block:: python

    from boaconstructor import Template

    common = dict(
        timeout = 30,
        email = "admin@example.com"
    )

    webserver = Template('webserver', dict(
        interface = 'host.$.name',
        port = 32189,
        timeout = 'common.$.timeout',
        alert_email = 'common.$.email',
    ))

    data = webserver.render(dict(
        host=dict(name='myserver1'),
        common=common,
    ))

    print data
    # {'alert_email': 'admin@example.com', 'interface': 'myserver1', 'port': 32189, 'timeout': 30}




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
