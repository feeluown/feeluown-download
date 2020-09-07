"""
一些辅助类

.. note::

     ContentRange, Range, parse_range_header, parse_content_range_header
     四个实现均是从 werkzeug 项目中拷贝过来。
"""


class ContentRange(object):

    """Represents the content range header.

    .. versionadded:: 0.7
    """

    def __init__(self, units, start, stop, length=None, on_update=None):
        assert is_byte_range_valid(start, stop, length), \
            'Bad range provided'
        self.on_update = on_update
        self.set(start, stop, length, units)

    def _callback_property(name):
        def fget(self):
            return getattr(self, name)

        def fset(self, value):
            setattr(self, name, value)
            if self.on_update is not None:
                self.on_update(self)
        return property(fget, fset)

    #: The units to use, usually "bytes"
    units = _callback_property('_units')
    #: The start point of the range or `None`.
    start = _callback_property('_start')
    #: The stop point of the range (non-inclusive) or `None`.  Can only be
    #: `None` if also start is `None`.
    stop = _callback_property('_stop')
    #: The length of the range or `None`.
    length = _callback_property('_length')

    def set(self, start, stop, length=None, units='bytes'):
        """Simple method to update the ranges."""
        assert is_byte_range_valid(start, stop, length), \
            'Bad range provided'
        self._units = units
        self._start = start
        self._stop = stop
        self._length = length
        if self.on_update is not None:
            self.on_update(self)

    def unset(self):
        """Sets the units to `None` which indicates that the header should
        no longer be used.
        """
        self.set(None, None, units=None)

    def to_header(self):
        if self.units is None:
            return ''
        if self.length is None:
            length = '*'
        else:
            length = self.length
        if self.start is None:
            return '%s */%s' % (self.units, length)
        return '%s %s-%s/%s' % (
            self.units,
            self.start,
            self.stop - 1,
            length
        )

    def __nonzero__(self):
        return self.units is not None

    __bool__ = __nonzero__

    def __str__(self):
        return self.to_header()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))


class Range(object):

    """Represents a range header.  All the methods are only supporting bytes
    as unit.  It does store multiple ranges but :meth:`range_for_length` will
    only work if only one range is provided.

    .. versionadded:: 0.7
    """

    def __init__(self, units, ranges):
        #: The units of this range.  Usually "bytes".
        self.units = units
        #: A list of ``(begin, end)`` tuples for the range header provided.
        #: The ranges are non-inclusive.
        self.ranges = ranges

    def range_for_length(self, length):
        """If the range is for bytes, the length is not None and there is
        exactly one range and it is satisfiable it returns a ``(start, stop)``
        tuple, otherwise `None`.
        """
        if self.units != 'bytes' or length is None or len(self.ranges) != 1:
            return None
        start, end = self.ranges[0]
        if end is None:
            end = length
            if start < 0:
                start += length
        if is_byte_range_valid(start, end, length):
            return start, min(end, length)

    def make_content_range(self, length):
        """Creates a :class:`~werkzeug.datastructures.ContentRange` object
        from the current range and given content length.
        """
        rng = self.range_for_length(length)
        if rng is not None:
            return ContentRange(self.units, rng[0], rng[1], length)

    def to_header(self):
        """Converts the object back into an HTTP header."""
        ranges = []
        for begin, end in self.ranges:
            if end is None:
                ranges.append(begin >= 0 and '%s-' % begin or str(begin))
            else:
                ranges.append('%s-%s' % (begin, end - 1))
        return '%s=%s' % (self.units, ','.join(ranges))

    def to_content_range_header(self, length):
        """Converts the object into `Content-Range` HTTP header,
        based on given length
        """
        range_for_length = self.range_for_length(length)
        if range_for_length is not None:
            return '%s %d-%d/%d' % (self.units,
                                    range_for_length[0],
                                    range_for_length[1] - 1, length)
        return None

    def __str__(self):
        return self.to_header()

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, str(self))


def is_byte_range_valid(start, stop, length):
    """Checks if a given byte content range is valid for the given length.

    .. versionadded:: 0.7
    """
    if (start is None) != (stop is None):
        return False
    elif start is None:
        return length is None or length >= 0
    elif length is None:
        return 0 <= start < stop
    elif start >= stop:
        return False
    return 0 <= start < length


def parse_range_header(value, make_inclusive=True):
    """Parses a range header into a :class:`~werkzeug.datastructures.Range`
    object.  If the header is missing or malformed `None` is returned.
    `ranges` is a list of ``(start, stop)`` tuples where the ranges are
    non-inclusive.

    .. versionadded:: 0.7
    """
    if not value or '=' not in value:
        return None

    ranges = []
    last_end = 0
    units, rng = value.split('=', 1)
    units = units.strip().lower()

    for item in rng.split(','):
        item = item.strip()
        if '-' not in item:
            return None
        if item.startswith('-'):
            if last_end < 0:
                return None
            try:
                begin = int(item)
            except ValueError:
                return None
            end = None
            last_end = -1
        elif '-' in item:
            begin, end = item.split('-', 1)
            begin = begin.strip()
            end = end.strip()
            if not begin.isdigit():
                return None
            begin = int(begin)
            if begin < last_end or last_end < 0:
                return None
            if end:
                if not end.isdigit():
                    return None
                end = int(end) + 1
                if begin >= end:
                    return None
            else:
                end = None
            last_end = end
        ranges.append((begin, end))

    return Range(units, ranges)


def parse_content_range_header(value, on_update=None):
    """Parses a range header into a
    :class:`~werkzeug.datastructures.ContentRange` object or `None` if
    parsing is not possible.

    .. versionadded:: 0.7

    :param value: a content range header to be parsed.
    :param on_update: an optional callable that is called every time a value
                      on the :class:`~werkzeug.datastructures.ContentRange`
                      object is changed.
    """
    if value is None:
        return None
    try:
        units, rangedef = (value or '').strip().split(None, 1)
    except ValueError:
        return None

    if '/' not in rangedef:
        return None
    rng, length = rangedef.split('/', 1)
    if length == '*':
        length = None
    elif length.isdigit():
        length = int(length)
    else:
        return None

    if rng == '*':
        return ContentRange(units, None, None, length, on_update=on_update)
    elif '-' not in rng:
        return None

    start, stop = rng.split('-', 1)
    try:
        start = int(start)
        stop = int(stop) + 1
    except ValueError:
        return None

    if is_byte_range_valid(start, stop, length):
        return ContentRange(units, start, stop, length, on_update=on_update)


def cook_filename(title, artists_name):
    return f'{title} - {artists_name}.mp3'
