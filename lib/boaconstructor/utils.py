"""

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
import types
import pprint


import core


# The default string marker either side of which is the reference and attribute.
REFATT_MARKER = '.$.'


def is_ref_attr(value, output=['',''], marker=REFATT_MARKER):
    """Test if the given value is a reference-attribute."""
    returned = False

    if type(value) in types.StringTypes:
        # Only bother with strings, ignore everything else.
#        print("value: '%s'" % value)
        out = value.split(marker)
        # two items and they are actually something
        if len(out) == 2:
            if out[0] and out[1]:
                returned = True
                output[0] = out[0]
                output[1] = out[1]

    return returned


def parse_value(value, marker=REFATT_MARKER):
    """Recover the reference-attribute from the given value.

    :param value: This is a string in the form "<reference>.$.<attribute>".
    The ".$." in the string makes this a reference-attribute. Only strings
    are looked at. All other types are ignored.

    :param marker: This is the default '.$.' string on either side of
    which the reference and attribute will be found. It can be changed if
    needed.

    :returns: (reference, attribute)

        If the val is not a reference-attribute then ('', '') is returned.
        Otherwise ('<reference>', '<attribute>') strings are returned.

    """
    returned = ['','']

    # Called like this: returned is set up if the value is a ref-attr
    is_ref_attr(value, returned, marker=marker)

    return returned


class ReferenceError(Exception):
    """Raised when a reference name could not found in references given."""


class AttributeError(Exception):
    """Raised when an attribute was not found for the references given."""


def has(reference, attribute):
    """Check if the dict, instance or Template instance has a given attribute.

    :param reference: A dict, Template instance or a object instance.

    :param attribute: A string representing the key/member variable
    to recover.

    :returns: True yes, False no.

    """
    returned = False

    if type(reference) in (types.DictType, types.DictProxyType):
        returned = attribute in reference

    elif hasattr(reference, 'content'):
        # core.Template like: Look inside the content and not the
        # Template object itself.
        returned = attribute in getattr(reference, 'content')

    else:
        # Assume it is an instance of some kind which supports hasattr:
        returned = hasattr(reference, attribute)

    return returned


def get(reference, attribute):
    """Get the attribute value from the given dict, object instance or Template
    instance.

    :param reference: A dict, Template instance or a object instance.

    :param attribute: A string representing the key/member variable
    to recover.

    :returns: The value found. If nothing could be recovered then
    AttributeError will be raised.

    """
    found = False
    returned = False

    if type(reference) in (types.DictType, types.DictProxyType):
        if attribute in reference:
            found = True
            returned = reference[attribute]


    elif hasattr(reference, 'content'):
        # core.Template like: Look inside the content and not the
        # Template object itself.
        r = getattr(reference, 'content')
        if attribute in r:
            found = True
            returned = r[attribute]

    else:
        # Assume it is an instance of some kind which supports getattr:
        if hasattr(reference, attribute):
            found = True
            returned = getattr(reference, attribute)

    if not found:
        raise AttributeError("The attribute '%s' in any reference!" % attribute)

    return returned


def resolve_references(reference, attribute, int_references, ext_references={}):
    """Work out the attribute value for a reference from the internal or
    external references.

    This is usually call by the Template.resolve method.

    :param reference: This is the <reference> string recovered
    from a call to parse_value.

    :param attribute: This is the dict key we must look up in the
    references. This is the <attribute> recovered from a call to
    parse_value.

    :param int_references: This the reference dict usually representing the
    reference stored as a member of the Template class.

    :param ext_references: This the reference dict usually representing the
    reference given as an argument to render.

    The ext_references is given priority over the int_references. If a
    reference-attribute is found, then int_references will not be consulted.

    If the reference is not found in int_references or ext_references then
    ReferenceError will be raised.

    If the attribute is not found in in the any of the reference dicts, then
    AttributeError will be raised.

    """
    found = False
    returned = ""

    #print("\n\nreference '%s' attribute '%s'\nint_references: '%s'\next_references: '%s'\n\n" % (reference, attribute, int_references, ext_references))

    ref_present = reference in ext_references or reference in int_references
    if not ref_present:
        # The reference is not present at all, abandon.
        raise ReferenceError("The reference '%s' could not be resolved!" % reference)

    # Look for the attribute in the ext_references:
    ext_result = None
    if has(ext_references, reference):
        r = get(ext_references, reference)
        if has(r, attribute):
            # Success, skip int_references lookup:
            found = True
            returned = get(r, attribute)

    int_result = None
    if not found and has(int_references, reference):
        # Nothing was found in externals so try in the internal references.
        r = get(int_references, reference)
        if has(r, attribute):
            found = True
            # Hurragh, its here.
            returned = get(r, attribute)

    if not found:
        raise AttributeError("The attribute '%s' in any reference!" % attribute)

    return returned


def build_ref_cache(int_refs, ext_refs):
    """Work out all the references and child references from the internal and
    externally given references.

    This in effect flattens the references and making lookup faster for
    recursive_render.

    :param int_refs: a dict of 'dicts and/or Template' instances.

    :param ext_refs: a dict of 'dicts and/or Template' instances.

    :returns: a dict with the results in the form

        results = {
            'int':{ ... },
            'ext':{ ... }
        }

    For an example of this see tests/testboacontructor.py:DataTemplate and
    'testBuildRefCache()'.

    """
    reference_cache = {'int':{}, 'ext':{}}

    def recover(items, dest):
        # Store the references:
        for reference, source in items:
            reference_cache[dest][reference] = source
            # Unpack and store the 'child' references if any are present:
            if hasattr(source, 'references'):
                children = getattr(source,'references').items()
                recover(children, dest)

    recover(int_refs.items(), dest='int')
    recover(ext_refs.items(), dest='ext')

    return reference_cache


def render(top_level_items, int_refs, ext_refs):
    """Construct the final dictionary after resolving all references to get
    their actual values.
    """
    returned = {}
    loop_count = 0

    # Work out all the references, in effect flattening the
    # references and making lookup faster later on.
    reference_cache = build_ref_cache(int_refs, ext_refs)

    print("\n\nreference_cache:\n%s\n\n" % pprint.pformat(reference_cache))

    for reference, attribute in top_level_items:
        # Add to what is returned. We'll replace the ref-attr shortly:
        top_ref = reference
        returned[top_ref] = attribute

        # Hunt for the last non reference-attribute i.e the actual value
        output = ['','']
        while is_ref_attr(attribute, output):
            # Resolve what this reference points at. Then loop to
            # check if this is also really a reference. Progress in
            # this way until no more ref-attrs are found. I.e. we've
            # got the actual value at the end of the pointer rainbow.
            #
            reference, attribute = output

            print("loop_count '%s', reference '%s', attribute: '%s'" %(loop_count, reference, attribute))

            if reference:
                attribute = resolve_references(
                        reference,
                        attribute,
                        reference_cache['int'],
                        reference_cache['ext'],
                )

            loop_count += 1

        # At this point the value is a non ref-attr. I can say this as a
        # reference or attribute error exceptions would have been raised
        # otherwise.
        returned[top_ref] = attribute

    return returned