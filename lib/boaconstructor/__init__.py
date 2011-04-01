"""
.. module::`boaconstructor`
    :platform: Unix, Windows
    :synopsis: boacontructor is a templating library for *data*.

The Template class
------------------

This is the high level class most commonly used.

.. autoclass:: Template
    :members:


The utils module
----------------

The :py:class:`Template` class wraps the functionality hiding most of the
details of this module.

.. automodule:: boaconstructor.utils

"""
import utils
import core

from core import Template
from core import TemplateError