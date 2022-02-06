import re
import json

from .utils import StringReader, multi_flag


class TokenizeException(Exception):
    pass

class ParseTree:
    def __init__(self, children=None, name='root'):
        self.name = name

        if children is None:
            self.children = []
        else:
            self.children = children
        
        self.temp_children = []
        
    def add_children(self, *children):
        self.temp_children.extend(children)

    def clean(self):
        self.children.extend(self.temp_children)
        self.temp_children.clear()
        for child in self.children:
            child.clean()
    
    def revert(self):
        self.temp_children.clear()
        for child in self.children:
            child.revert()

    def __repr__(self):
        return json.dumps(self.as_json(), indent=4)

    def __str__(self):
        return json.dumps(self.as_json(), indent=4)

    def as_json(self):
        return {
            'name': self.name,
            'children': [
                child.as_json() for child in self.children
            ]
        }
    
    def save(self, file_name):
        with open(file_name, 'w') as file:
            json.dump(self.as_json(), file)

class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f'{self.name} "{self.value}"'
    
    def clean(self):
        pass
    
    def revert(self):
        pass

    def as_json(self):
        return {
            'name': self.name,
            'value': self.value
        }

class BaseTokenizer:
    name = 'BASE'

    def resolve(self, lookup):
        pass

class FirstGroupTokenizer(BaseTokenizer):
    def __init__(self, name, *tokenizers):
        self.name = name
        self.tokenizers = tokenizers
    
    def __str__(self):
        return f'{self.name} ({", ".join(str(tokenizer) for tokenizer in self.tokenizers)})'
    
    def tokenize(self, tree, reader, lookup):
        for tokenizer in self.tokenizers:
            with reader.context() as temp_reader:
                tokenizer.tokenize(tree, temp_reader, lookup)
                return
        raise TokenizeException('Failed to tokenize')

class GroupTokenizer:
    def __init__(self, name, *tokenizers):
        self.name = name
        self.tokenizers = tokenizers
    
    def __str__(self):
        return f'{self.name} ({", ".join(str(tokenizer) for tokenizer in self.tokenizers)})'
    
    def tokenize(self, tree, reader, lookup):
        new_tree = ParseTree(name=self.name)
        for tokenizer in self.tokenizers:
            tokenizer.tokenize(new_tree, reader, lookup)
        tree.add_children(new_tree)

class LookupTokenizer:
    def __init__(self, lookup_name):
        self.lookup_name = lookup_name
    
    def __str__(self):
        return self.lookup_name
    
    def tokenize(self, tree, reader, lookup):
        lookup[self.lookup_name].tokenize(tree, reader, lookup)
    
    @property
    def name(self):
        return self.lookup_name

class RegexTokenizer:
    def __init__(self, regex, flags=[], name='RAW', discard=None):
        if discard is None:
            self.discard = name == 'RAW'
        else:
            self.discard = discard
        self.name = name
        self._raw = regex
        self.regex = re.compile(regex, flags=multi_flag(flags))
    
    def __str__(self):
        return self._raw
    
    def tokenize(self, tree, reader, lookup):
        match = reader.match(self.regex)
        if match:
            if not self.discard:
                tree.add_children(Token(self.name, match.group(0)))
            return
        raise TokenizeException(f'{self.name} {self._raw} {reader.remaining()}')

class TokenizerBuilder:
    def __init__(self, name, schema_builder=None):
        self.name = name
        self.schema_builder = schema_builder
        self.state = []

    def rule(self, rule):
        self.state.append(rule)
        return self

    def regex_rule(self, regex, flags=[], name='RAW'):
        self.state.append(RegexTokenizer(regex, flags, name))
        return self
    
    def lookup_rule(self, lookup_name):
        self.state.append(LookupTokenizer(lookup_name))
        return self
    
    def group(self, name):
        self.state = [GroupTokenizer(name, *self.state)]
        return self
    
    def next(self, first_group=False):
        self.schema_builder.rule(self.build(first_group))
        return self.schema_builder
    
    def build(self, first_group=False):
        if first_group:
            return FirstGroupTokenizer(self.name, *self.state)
        else:
            return GroupTokenizer(self.name, *self.state)

class TokenizerSchemaBuilder:
    def __init__(self):
        self.state = []
    
    def regex_rule(self, name, rule, flags=[]):
        self.state.append(RegexTokenizer(name=name, regex=rule, flags=flags))
        return self
    
    def group_rule(self, name, *tokenizers):
        self.state.append(FirstGroupTokenizer(name, *tokenizers))
        return self
    
    def rule(self, tokenizer):
        self.state.append(tokenizer)
        return self

    def complex_rule(self, name):
        return TokenizerBuilder(name, self)
    
    def build(self):
        return TokenizerSchema(*self.state)

class TokenizerSchema:
    def __init__(self, *tokenizers):
        self._production_lookup = {tokenizer.name: tokenizer for tokenizer in tokenizers}
        self._productions = tokenizers
    
    def load(self, file_name, debug=False):
        with open(file_name, 'r') as file:
            return self.parse(file.read())
    
    def parse(self, string, debug=False):
        reader = StringReader(string, exceptions=[TokenizeException])
        tree = ParseTree()
        looped = False

        while reader.has_next():
            if looped:
                if debug:
                    print(tree.as_json())
                raise TokenizeException(self._format_failed(reader))
            for production in self._productions:
                with reader.context() as temp_reader:
                    production.tokenize(tree, temp_reader, self._production_lookup)
                    if debug:
                        print('Success', production.name)
                    tree.clean()
                    continue
                if debug:
                    print('Fail', production.name)
                tree.revert()
            looped = True
        
        return tree
    
    @staticmethod
    def _format_failed(reader):
        line, line_no, offset = reader.get_line()
        return f'Failed to tokenize at line {line_no} (likely syntax error):\n{line}\n{"".join(([" "] * (offset)) + ["^"])}'
