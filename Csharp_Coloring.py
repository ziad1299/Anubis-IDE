import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter


def format(color, style=''):
    """
    Return a QTextCharFormat with the given attributes.
    """
    _color = QColor()
    if type(color) is not str:
        _color.setRgb(color[0], color[1], color[2])
    else:
        _color.setNamedColor(color)

    _format = QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format([200, 120, 50], 'bold'),
    'operator': format([150, 150, 150]),
    'brace': format('darkGray'),
    'defclass': format([220, 220, 255], 'bold'),
    'string': format([20, 110, 100]),
    'string2': format([30, 120, 110]),
    'comment': format([128, 128, 128]),
    'self': format([150, 85, 140], 'italic'),
    'numbers': format([100, 150, 190]),
}

class CSharpHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the C Sharp language.
    """
    # Keywords for C# language
    keywords = [
        'abstract', 'bool',	    'continue',	'decimal',	'default',
        'event',    'explicit',	'extern',	'char',	    'checked',
        'class',	'const',	'break',	'as',	    'base',
        'delegate',	'is,'	    'lock',	    'long',	    'num',
        'byte',     'case',	    'catch',	'false',	'finally',
        'fixed',	'float',	'for',	    'foreach',  'static',
        'goto',	    'if',	    'implicit',	'in',	    'int',
        'interface','internal',	'do',	    'double',	'else',
        'namespace','new',	    'null',	    'object',	'operator',
        'out',	    'override',	'params',	'private',	'protected',
        'public',	'readonly',	'sealed',	'short',	'sizeof',
        'ref',	    'return',	'sbyte',	'stackalloc','static',
        'string',	'struct',	'void',	    'volatile',	'while',
        'true',	    'try',	    'switch',	'this',	    'throw',
        'unchecked' 'unsafe',	'ushort',	'using',	'using',
        'virtual',	'typeof',	'uint',	    'ulong',	'out',
        'add',	    'alias',	'async',	'await',   	'dynamic',
        'from', 	'get',	    'orderby',	'ascending','decending',
        'group',	'into',	    'join',	    'let',	    'nameof',
        'global',	'partial',	'set',	    'remove',   'select',
        'value',	'var',	    'when',	    'Where',	'yield'
    ]

    # Operators for C# Langurage
    operators = [
        '=',
        # logical
        '!', '?', ':',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '\%', '\+\+', '--',
        # Assignment
        '\+=', '-=', '\*=', '/=', '\%=', '<<=', '>>=', '\&=', '\^=', '\|=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # C# braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in CSharpHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in CSharpHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in CSharpHighlighter.braces]

        # All other rules
        rules += [
            # String that has been double-quoted and may contain escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # Comments. from "/" to the end of a newline
            (r'//[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Format the syntax in numerous ways.
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # Actually, what we're after is the nth match's index.
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Commence multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            begin = 0
            appen = 0
        # Otherwise, look for the delimiter on this line
        else:
            begin = delimiter.indexIn(text)
            # Move past this match
            appen = delimiter.matchedLength()

        while begin >= 0:
            # Look for the ending delimiter
            finish = delimiter.indexIn(text, begin + appen)
            # Ending delimiter on this line?
            if finish >= appen:
                len = finish - begin + appen + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                len = len(text) - begin + appen
            # Apply formatting
            self.setFormat(begin, len, style)
            # Look for the next match
            begin = delimiter.indexIn(text, begin + len)

        if self.currentBlockState() == in_state:
            return True
        else:
            return False 