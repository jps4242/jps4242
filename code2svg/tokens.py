from dataclasses import dataclass
from typing import get_args, Literal

__all__ = [
    'Token',
    'ColorScheme',
    'Color'
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


type ColorScheme = Literal['light', 'dark']


@dataclass
class Color:
    """
    A class representing a token color. Colors must be specified for at least
    one color scheme.

    :param light: The color used for the light color scheme. Can be ``None``.
    :type light: str | None
    :param dark: The color used for the dark color scheme. Can be ``None``.
    :type dark: str | None
    """

    def __init__(self, light: str | None = None, *, dark: str | None = None):
        if light is None and dark is None:
            raise ValueError(
                'Colors must be specified for at least on color scheme'
            )
        self.light = light
        self.dark = dark

    def get_value(self, color_scheme: ColorScheme = 'light') -> str:
        valid_color_schemes = get_args(ColorScheme.__value__)
        if color_scheme not in valid_color_schemes:
            raise ValueError(
                f'color_scheme must be one of {
                    ", ".join(valid_color_schemes)
                }'
            )
        return (
            (self.light if self.light is not None else self.dark)
            if color_scheme == 'light'
            else (self.dark if self.dark is not None else self.light)
        )


class colors:
    """
    Colors for common token types.
    """

    keyword = Color(light='#af00db', dark='#c586c0')
    default = Color(light='#24292f', dark='#d4d4d4')
    string = Color(light='#a31515', dark='#ce9178')
    number = Color(light='#098658', dark='#b5cea8')
    function = Color(light='#795e26', dark='#dcdcaa')
    class_or_type = Color(light='#267f99', dark='#4ec9b0')
    property = Color(light='#0451a5', dark='#9cdcfe')
    punctuation = Color(light='#24292f', dark='#d4d4d4')
    operator = Color(light='#24292f', dark='#d4d4d4')
    comment = Color(light='#008000', dark='#6a9955')
    constant = Color(light='#0000ff', dark='#569cd6')

    background = Color(light='#fafafa', dark='#1e1e1e')


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
