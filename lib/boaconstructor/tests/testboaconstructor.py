"""
Tests to verify the boaconstructor functionality.

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

"""
import pprint
import unittest

import boaconstructor
from boaconstructor import utils
from boaconstructor import Template


class BoaConstructor(unittest.TestCase):


    def testTemplateExtending(self):
        """Test using the render extend argument.
        """
        common = dict(buffer=4096)

        auth = dict(target='<to replace by test1>', user='james', secret='11ed394')

        test1 = Template(
            'test1',
            {
                # This will overwrite the place holder in auth 'target'
                'target': 'production',

                'system':'Live00',
                'recv': 'common.$.buffer',

                # The rest of auth will end up here
            },
        )

        result = test1.render(
            dict(
                common=common,
            ),
            # Extend the rendered dict with all the resolve key,values
            # from the given dict. It will also be processed using the
            # references:
            extendwith=auth,
        )

        correct = dict(
            target='production',
            system='Live00',
            recv=4096,
            user='james',
            secret='11ed394',
        )

        # aid visual debug:
        err_msg = """result != correct
result:
%s

correct:
%s
        """ % (pprint.pformat(result), pprint.pformat(correct))

        self.assertEquals(result, correct, err_msg)


    def testListsAndTemplateIncludes(self):
        """Test the 'reference.*' which includes all the content of a template
        in another and its use in lists.

        """
        common = dict(keep='yes', buffer=4096)

        auth = dict(user='james', secret='11ed394')

        test1 = Template(
            'test1',
            dict(
                port=2394,
                hostname='bob',
                user='auth.$.user',
                password='auth.$.secret',
            ),
        )

        # This includes all of test1 as 'host' at render time. The test1
        # template will also require the auth reference to be made available
        # in order for it to render without Attribute/Reference Errors.
        #
        test2 = Template(
            'test2',
            dict(host='test1.*', keep='com.$.keep'),
            references=dict(
                com=common,
                test1=test1,
            ),
        )

        # simulate only known authentication details at run/render time:
        result = test2.render(dict(
            auth=auth,
        ))

        correct = dict(
            host=dict(
                port=2394,
                hostname='bob',
                user='james',
                password='11ed394'
            ),
            keep='yes'
        )

        # aid visual debug:
        err_msg = """result != correct
result:
%s

correct:
%s
        """ % (pprint.pformat(result), pprint.pformat(correct))

        self.assertEquals(result, correct, err_msg)


        # Now, add list of ref-attr or all-inclusions into the mix and see
        # that these are correctly resolved and replaced.
        common = dict(keep='yes', buffer=4096)

        peter = dict(username='pstoppard', secret='11ed394')
        graham = dict(username='gturner', secret='54jsl31')

        test1 = Template(
            'test1',
            dict(
                options='common.*',
                usernames=['peter.$.username','graham.$.username'],
                users=['peter.*', 'graham.*'],
            ),
        )

        result = test1.render(
            references={
                'common': common,
                'peter': peter,
                'graham': graham,
            }
        )

        # I need to sort so it will order as python would order the dicts.
        u = [
            dict(username='pstoppard', secret='11ed394'),
            dict(username='gturner', secret='54jsl31'),
        ]
        u.sort()
        correct = dict(
            options=dict(keep='yes', buffer=4096),
            usernames=['pstoppard', 'gturner'],
            users=u,
        )

        err_msg = """result != correct
result:
%s

correct:
%s
        """ % (pprint.pformat(result), pprint.pformat(correct))

        self.assertEquals(result, correct, err_msg)



    def testRender(self):
        """Test the utils module render which is used by the Template class.
        """
        common = dict(keep='yes', buffer=4096)

        test1 = Template(
            'test1',
            dict(keep='yes', buffer='data.$.buffer', hostname='bob'),
            references={
                'data':common,
            }
        )

        test2 = Template(
            'test2',
            dict(buffer='test1.$.buffer', hostname='bob', keep='common.$.keep'),
            references={
                'test1':test1,
            }
        )

        # 'Render' test2 into a dict using the internal utils function:
        result = utils.render(
            test2.content.items(),
            int_refs=test2.references,
            ext_refs={'common':common}
        )

        correct = dict(
            buffer=4096,
            hostname='bob',
            keep='yes'
        )

        # aid visual debug:
        err_msg = """result != correct
result:
%s

correct:
%s
        """ % (pprint.pformat(result), pprint.pformat(correct))

        self.assertEquals(result, correct, err_msg)


    def testBuildRefCache(self):
        """Test the build reference cache generation works as I expect it too.

        This is used by render when it preprocesses the references.

        """
        common = dict(keep='yes', buffer=4096)

        test1 = Template(
            'test1',
            dict(keep='yes', buffer='data.$.buffer', hostname='bob'),
            references={
                'data':common,
            }
        )

        test2 = Template(
            'test2',
            dict(buffer='test1.$.buffer', hostname='bob', keep='common.$.keep'),
            references={
                'test1':test1,
            }
        )

        # The ref cache is a quick lookup used by the resolve process
        # to find references and child references. This is important
        # when finding reference-to-reference attributes
        #
        int_refs = {
            "test1":test1
        }

        ext_refs = {
            "common": common
        }

        # This should correctly identify data test1 refers to.as an internal
        # reference:
        #
        result = utils.build_ref_cache(int_refs, ext_refs)

        correct = {
            'int': {
                'test1':test1,
                'data': common
            },
            'ext': {
                'common': common,
            }
        }

        # aid visual debug:
        err_msg = """result != correct
result:
%s

correct:
%s
        """ % (pprint.pformat(result), pprint.pformat(correct))

        self.assertEquals(result, correct, err_msg)


    def testHasGet(self):
        """Test the special reference-attribute has/getter.
        """
        ref = dict(abc=123)
        att = 'abc'
        result = True
        self.assertEquals(utils.has(ref, att), result)
        self.assertEquals(utils.get(ref, att), 123)

        ref = Template('test', dict(abc=123))
        att = 'abc'
        result = True
        self.assertEquals(utils.has(ref, att), result)
        self.assertEquals(utils.get(ref, att), 123)

        class Data:
            abc = 123

        ref = Data
        att = 'abc'
        result = True
        self.assertEquals(utils.has(ref, att), result)
        self.assertEquals(utils.get(ref, att), 123)

        class Data:
            def __init__(self):
                self.abc = 123

        ref = Data()
        att = 'abc'
        result = True
        self.assertEquals(utils.has(ref, att), result)
        self.assertEquals(utils.get(ref, att), 123)



    def testReferenceResolving(self):
        """Test the resolution of refrence,attributes.
        """
        # Test reference not found:
        ref = "common"
        att = ""
        int_refs = dict()
        ext_refs = dict()

        self.assertRaises(
            utils.ReferenceError,
            utils.resolve_references,
            ref, att, int_refs, ext_refs
        )

        # Test attribute not found:
        ref = "common"
        att = "hostname"
        int_refs = dict(common=dict(interface='1.2.3.4'))
        ext_refs = dict()

        self.assertRaises(
            utils.AttributeError,
            utils.resolve_references,
            ref, att, int_refs, ext_refs
        )

        ref = "common"
        att = "hostname"
        int_refs = dict()
        ext_refs = dict(common=dict(interface='1.2.3.4'))

        self.assertRaises(
            utils.AttributeError,
            utils.resolve_references,
            ref, att, int_refs, ext_refs
        )

        # Test attribute found in reference:
        ref = "common"
        att = "hostname"
        int_refs = dict()
        ext_refs = dict(common=dict(hostname='example.com'))
        results = utils.resolve_references(ref, att, int_refs, ext_refs)
        correct = "example.com"
        self.assertEquals(results, correct)

        # Dots are allowed in references, nothing is done yet with this.
        ref = "machines.common"
        att = "hostname"
        int_refs = {'machines.common': dict(hostname='example.com')}
        ext_refs = {}
        results = utils.resolve_references(ref, att, int_refs, ext_refs)
        correct = "example.com"
        self.assertEquals(results, correct)

        # Test ext_refs priority over int_refs:
        ref = "common"
        att = "hostname"
        int_refs = dict(common=dict(hostname='example.com'))
        ext_refs = dict(common=dict(hostname='localhost'))
        results = utils.resolve_references(ref, att, int_refs, ext_refs)
        correct = "localhost"
        self.assertEquals(results, correct)

        # Test all inclusion reference resolving i.e. attribute is None
        # and only the reference is important.
        #
        ref = "common"
        att = None
        int_refs = dict(common=dict(hostname='example.com'))
        ext_refs = dict(common=dict(hostname='localhost'))
        results = utils.resolve_references(ref, att, int_refs, ext_refs)
        correct = dict(hostname='localhost')
        self.assertEquals(results, correct)

        ref = "common"
        att = None
        int_refs = dict(common=dict(hostname='example.com'))
        ext_refs = {}
        results = utils.resolve_references(ref, att, int_refs, ext_refs)
        correct = dict(hostname='example.com')
        self.assertEquals(results, correct)



    def testMixedDictTemplateAndInstanceResolution(self):
        """Test the mixed use of dicts, template instances and class instances
        as references. This also tests basic recursive resolution.
        """
        class SomeData(object):
            def __init__(self):
                self.packet_size = 2048
                self.live = True

        somedata = SomeData()

        # Set up common point at somedata. This will need recursion in host2
        # as it will refere to common.$.buffer.
        #
        common = Template('common', {
                "timeout": 42,
                "buffer": 'data.$.packet_size',
            },
            references=dict(data=somedata),
        )

        # Render the 'host1' dict which uses dict+instance references. This
        # doesn't need recursion as no reference refers to another.
        #
        host1 = Template('host1', {
                "host": "1.2.3.4",
                "flag": False,
                "timeout": 'common.$.timeout',
                "packet_size": 'data.$.packet_size',
                "live": 'data.$.live',
            },
            references = {
                'common':common,
                'data': somedata,
            }
        )

        result = host1.render()

        correct = {
            "host":"1.2.3.4","flag":False,"timeout":42,
            "packet_size":somedata.packet_size, "live": somedata.live,
        }
        for key in correct:
            self.assertEquals(result[key], correct[key])


        # Render 'host2' which uses mixed dict+template. Recursion will also
        # be needed to work out that host.$.packet size comes from somedata i.e.
        # host1 -> common -> somedata. In the final rendered host2 result buffer
        # should be 2048
        #
        host2 = Template('host2', {
                "host": "4.3.2.1",
                "flag": 'host.$.flag',
                "timeout": 'common.$.timeout',
                "buffer": 'common.$.buffer',
            },
            references = {
                'common': common,
                'host': host1,
            }
        )

        result = host2.render()
        self.assertEquals(result['host'], '4.3.2.1')
        self.assertEquals(result['flag'], False)
        self.assertEquals(result['timeout'], 42)
        # This should be a value and not a reference:
        self.assertEquals(result['buffer'], 2048)


    def testValueParsing(self):
        """Test parsing a dict entries value to recover the reference and
        attribute.

        """
        # Test entries that are not reference-attribute values:
        #
        ignore = [
            1, None, '1', '', 'bob', object(), 'abc.efg', 1.02,
            Exception, dir(), "abc$efg", "abc$.efg", "abc.$efg",
            'bob*','bob.', '.*', 'abc.*.stuff'
        ]
        for value in ignore:
            correct = dict(found=None,reference='',attribute='',allfrom='')
            result = utils.parse_value(value)
            self.assertEquals(result, correct)

        # Now check the recovery of valid reference-attributes:
        value = 'abc.$.efg'
        correct = dict(found='refatt',reference='abc',attribute='efg',allfrom='')
        result = utils.parse_value(value)
        self.assertEquals(result, correct)

        value = 'settings.host.$.timeout'
        correct = dict(found='refatt',reference='settings.host',attribute='timeout',allfrom='')
        result = utils.parse_value(value)
        self.assertEquals(result, correct)

        # Now try all inclusion entries:
        #
        value = 'settings.host.*'
        correct = dict(found='all',reference='',attribute='',allfrom='settings.host')
        result = utils.parse_value(value)
        self.assertEquals(result, correct)

        value = 'abc.*'
        correct = dict(found='all',reference='',attribute='',allfrom='abc')
        result = utils.parse_value(value)
        self.assertEquals(result, correct)


    def testBasicExampleUsage(self):
        """Test the reference lookup and basic template render used as an example.
        """
        # Data to be used in host1 and host2
        common = Template('common', {
            "timeout": 42
        })

        # Uses data from common:
        host1 = Template('host1', {
                "host": "1.2.3.4",
                "flag": False,
                "timeout": 'common.$.timeout'
            },
            references = {'common':common}
        )

        # Uses data from common and host1
        host2 = Template('host2', {
                "host": "4.3.2.1",
                "flag": 'host.$.flag',
                "timeout": 'common.$.timeout',
            },
        )

        # Render the 'host1' dict:
        result = host1.render()
        correct = {"host":"1.2.3.4","flag":False,"timeout":42}
        self.assertEquals(result, correct)

        # Render the 'host2' dict:
        result = host2.render(
            references = {
                'common': common,
                'host': host1,
            }
        )
        correct = {"host":"4.3.2.1","flag":False,"timeout":42}
        self.assertEquals(result, correct)
