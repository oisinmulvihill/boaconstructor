The boaconstructor lib
======================

License
-------

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

Links
-----

Source Code:

  * GitHub: <a href="https://github.com/oisinmulvihill/boaconstructor">https://github.com/oisinmulvihill/boaconstructor</a>

Documentation:

  * <a href="http://packages.python.org/boaconstructor">http://packages.python.org/boaconstructor/</a>

Python Package Index:

  * <a href="http://pypi.python.org/pypi/boaconstructor">http://pypi.python.org/pypi/boaconstructor</a>


What is it?
-----------

boacontructor is a templating library for *data*. It allows you to construct
Python dictionaries from other templates, dictionaries or instances.

<pre>

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

</pre>

Have a look at tests/testboacontructor.py for usage examples. For detailed
documentation why not head over <a href="http://packages.python.org/boaconstructor">here</a>.

 * <a href="http://packages.python.org/boaconstructor">http://packages.python.org/boaconstructor/</a>


Releases
--------

0.3.0
~~~~~

 * Introduces "derivefrom.[]" operation which can now be used in dictionary values.

 * Increased test coverage and Sphinx generated documentation.
