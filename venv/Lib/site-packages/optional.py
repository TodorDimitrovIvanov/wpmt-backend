#!/usr/bin/env python3
"""
A mostly transparent optional class implemention
"""
import sys


class _optional(object):
    """ Optional Object Functionality """
    def __init__(self, *args, **kwargs):
        self._is_set, self._default = False, None

    def set_value(self, value):
        """ Return a new optional to overwrite the old one """
        new_optional = optional(value, self.default)
        new_optional.is_set = value is not None
        return new_optional

    @property
    def is_set(self):
        """ Return true if the optional has an explicit value """
        return self._is_set

    @is_set.setter
    def is_set(self, is_set):
        """ Set if this optional has an explicit value """
        self._is_set = is_set

    @property
    def default(self):
        """ Return the default to use if not explicity set """
        return self._default

    @default.setter
    def default(self, value):
        """ Set the default to use when not explicitly set """
        self._default = value

    @property
    def is_default(self):
        """ Return true if using default value rather than explicit value """
        if not self.is_set:
            return self.default == self
        return False


class _OptionalWrapper(type):
    """ Metaclass to make in instance of the value type with the optional behavior """
    def __call__(cls, value=None, default=None):
        """ Called on instance constructions """
        value_type, default_type, none_type = type(value), type(default), type(None)
        instance_type = value_type if value_type is not none_type else default_type
        instance_value = value if value_type is not none_type else default
        # If we have a value or default lets make and instance of one of them
        if instance_type is not none_type:
            # Create a new instance of of the type but adding the _optional base class
            new_value_class = type(
                '%s(%s)' % (cls.__name__, instance_value),
                (instance_value.__class__, _optional),
                {})
            try:
                instance = new_value_class(instance_value)
            except:
                # constructor can not take an instance. So lets create an uninitialised
                # instance and then copt the state across
                instance = new_value_class.__new__(new_value_class)
                instance.__dict__ = instance_value.__dict__.copy()
            instance.is_set = True if value_type is not none_type else False
            instance.default = default
        else:
            # Otherwise lets just make an instance of _optional
            new_value_class = type('%s(%s)' % (cls.__name__, 'None'), (_optional,), {})
            instance = new_value_class()
            instance._value = None
            instance.is_set = False
            instance.default = default
        return instance


PY3_OPTIONAL_DEFINITION = """
class optional(metaclass=_OptionalWrapper):
    ''' Face on optional meta/class '''
"""


PY2_OPTIONAL_DEFINITION = """
class optional(object):
    ''' Face on optional meta/class '''
    __metaclass__ = _OptionalWrapper
"""


if sys.version_info >= (3,0):
    exec(PY3_OPTIONAL_DEFINITION)
else:
    exec(PY2_OPTIONAL_DEFINITION)

