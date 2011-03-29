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


Introduction
------------

The boacontructor module is a templating library for data. It allows you to
construct python dictionaries from common and specific parts.

<pre>

from boaconstructor import Template

# Data to be used in host1 and host2
common = Template('common', {
    "timeout": 42,
    "buffer": 4096,
})

# Uses data from common:
host1 = Template('host1', {
        "host": "1.2.3.4",
        "flag": False,
        "timeout": 'common.$.timeout',
        "buffer": 'common.$.buffer',
    },
    references = {'common':common}
)

# Render the 'host1' dict:
result = host1.render()
>> result  = {"host":"1.2.3.4","flag":False,"timeout":42,"buffer":4096}


# Uses data from common and host1
host2 = Template('host2', {
        "host": "4.3.2.1",
        "flag": 'host.$.flag',
        "timeout": 'common.$.timeout',
        "recv": 'host.$.buffer'
    },
    references = {
        'common': common,
        'host': host1,
    }
)

# Render the 'host2' dict which should resolve and construct result:
result = host2.render()
>> result = {"host":"4.3.2.1","flag":False,"timeout":42,"recv":4096}

</pre>

Have a look at tests/testboacontructor.py for usage. More docs to follow...

