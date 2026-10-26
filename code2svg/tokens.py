from dataclasses import dataclass

__all__ = [
    'Token',
    'colors',
    'js',
    'punctuation',
    'space',
]


@dataclass
class Token:
    """
    A class representing a token.

    :param text: The token text.
    :type text: str
    :param color: The token color.
    :type color: Color | None
    """

    text: str
    color: Color | None = None


@dataclass
class Color:
    """
    A class representing a token color.

    :param value: The color value.
    :type value: str
    """
    value: str


class colors:
    """
    Colors for common token types.
    """

    keyword = Color('#c586c0')
    default = Color('#d4d4d4')
    string = Color('#ce9178')
    number = Color('#b5cea8')
    function = Color('#dcdcaa')
    class_or_type = Color('#4ec9b0')
    property = Color('#9cdcfe')
    punctuation = Color('#d4d4d4')
    operator = Color('#d4d4d4')
    comment = Color('#6a9955')
    constant = Color('#569cd6')


class js:
    """
    JavaScript tokens.
    """

    class_ = Token('class', colors.keyword)
    this = Token('this', colors.keyword)
    const = Token('const', colors.keyword)
    new = Token('new', colors.keyword)
    ternary_colon = Token(':', colors.operator)
    ternary_question_mark = Token('?', colors.operator)


class punctuation:
    """
    Punctuation tokens.
    """

    curly_parenthesis_open = Token('{', colors.punctuation)
    curly_parenthesis_close = Token('}', colors.punctuation)
    parenthesis_open = Token('(', colors.punctuation)
    parenthesis_close = Token(')', colors.punctuation)
    square_bracket_open = Token('[', colors.punctuation)
    square_bracket_close = Token(']', colors.punctuation)
    comma = Token(',', colors.punctuation)
    dot = Token('.', colors.punctuation)
    semicolon = Token(';', colors.punctuation)
    backtick = Token('`', colors.punctuation)
    single_quote = Token("'", colors.string)
    double_quote = Token('"', colors.string)
    colon = Token(':', colors.punctuation)
    dollar = Token('$', colors.punctuation)

    eq = Token('=', colors.operator)
    lt = Token('<', colors.operator)
    le = Token('<=', colors.operator)
    gt = Token('>', colors.operator)
    ge = Token('>=', colors.operator)

space = Token(' ')
