import re


WHITESPACE_REGEX = re.compile('\\s+')
LAST_NEW_LINE_REGEX = re.compile('(?s:.*)[\\n\\r]')
NEW_LINE_REGEX = re.compile('^[\\n\\r]')

class StringReader:
    def __init__(self, string, offset=None, parent=None, exceptions=[], skip_whitespace=True):
        self.string = string
        self.offset = offset or 0
        self._revert = []
        self._parent = parent
        self._exceptions = exceptions
        if skip_whitespace:
            self.skip_whitespace()
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.has_next():
            return self.next_token()
        raise StopIteration
    
    def skip_whitespace(self):
        self.match(WHITESPACE_REGEX, False)
    
    def get_line(self):
        lines = self.string.splitlines(keepends=True)
        offset = self.offset

        for _ in range(len(lines)):
            line, length = lines[_], len(lines[_])
            if offset < length:
                return line.strip(), _ + 1, offset
            offset -= length

        return '', -1, 0
    
    def match(self, regex, skip_whitespace=True):
        match = regex.match(self.string, pos=self.offset)
        if match:
            self.offset += len(match.group(0))
        if skip_whitespace:
            self.skip_whitespace()
        return match
    
    def next_token(self, regex):
        return self._match(regex) or self._before_match(regex)
    
    def _match(self, regex):
        match = self.match(regex)
        if match:
            return match.group(0)
        return None

    def _before_match(self, regex):
        match = regex.search(self.string, pos=self.offset)
        if match:
            start = match.span()[0]
            string = self.string[self.offset:start]
            self.offset = start
            return string
        string = self.string[self.offset:]
        self.offset = len(self.string)
        return string
    
    def clone(self):
        return StringReader(self.string, self.offset)
    
    def context(self):
        return StringReader(self.string, self.offset, self, self._exceptions)
    
    def has_next(self):
        return self.offset < len(self.string)
    
    def __str__(self):
        return f'{self.string[self.offset:]}'
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            return exc_type in self._exceptions
        self._parent.offset = self.offset
        return True
    
    def remaining(self):
        return self.string[self.offset:]

def multi_flag(flags):
    if not flags:
        return 0
    out = flags[0]
    for flag in flags[1:]:
        out |= flag
    return out