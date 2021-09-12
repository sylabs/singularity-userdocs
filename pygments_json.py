from pygments.lexer import include, RegexLexer
from pygments.token import Token
import re


# JSON lexer, for its use, please use ".. code-block:: json" syntax

class JSONLexer(RegexLexer):
    """
    Lexer for `JSON files`
    """

    name = 'JSON Lexer'
    aliases = ['json']
    filenames = ['*.json']
    mimetypes = ['application/json']

    flags = re.DOTALL
    tokens = {
        'whitespace': [
            (r'\s+', Token.Text),
        ],

        # represents a simple terminal value
        'simplevalue':[
            (r'(true|false|null)\b', Token.Keyword.Constant),
            (r'-?[0-9]+', Token.Number.Integer),
            (r'"(\\\\|\\"|[^"])*"', Token.String.Double),
        ],


        # the right hand side of an object, after the attribute name
        'objectattribute': [
            include('value'),
            (r':', Token.Punctuation),
            # comma terminates the attribute but expects more
            (r',', Token.Punctuation, '#pop'),
            # a closing bracket terminates the entire object, so pop twice
            (r'}', Token.Punctuation, ('#pop', '#pop')),
        ],

        # a json object - { attr, attr, ... }
        'objectvalue': [
            include('whitespace'),
            (r'"(\\\\|\\"|[^"])*"', Token.Name.Tag, 'objectattribute'),
            (r'}', Token.Punctuation, '#pop'),
        ],

        # json array - [ value, value, ... }
        'arrayvalue': [
            include('whitespace'),
            include('value'),
            (r',', Token.Punctuation),
            (r']', Token.Punctuation, '#pop'),
        ],

        # a json value - either a simple value or a complex value (object or array)
        'value': [
            include('whitespace'),
            include('simplevalue'),
            (r'{', Token.Punctuation, 'objectvalue'),
            (r'\[', Token.Punctuation, 'arrayvalue'),
        ],


        # the root of a json document would be a value
        'root': [
            include('value'),
        ],

    }
