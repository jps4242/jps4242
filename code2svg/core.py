from decimal import Decimal
from fontTools.ttLib import TTFont

from .fonts import FontTransformer
from .svg import SVGNode, create_path, create_svg
from .tokens import ColorScheme, colors, Token

__all__ = ['SVGCode']


_DEFAULT_LINE_HEIGHT = 16
_DEFAULT_LINE_FACTOR = 1.2
_DEFAULT_ANIMATION_DURATION = Decimal(0.5)


class SVGCode:
    """
    SVG code generator.

    :param lines: A list of the code lines. Each line is a list of tokens.
    :type lines: list[list[Token]]
    :param font: The font to use.
    :type font: TTFont
    :param line_height: The height of the lines.
    :type line_height: int | float
    :param line_factor: The factor the line height is multiplied by. It
                        determines the space a line needs. The height of the
                        actual characters has nothing to do with this.
    :type line_factor: int | float
    :param color_scheme: The color scheme for the token colors.
    :type color_scheme: ColorScheme
    :param background: Indicates a background will be added to the SVG.
    :type background: bool
    :param animation: Indicates whether the code will be animated. If it is
                      animated, each character appears with a delay which is
                      increased after each character. Each character fades in
                      within 0.1 seconds.
    :type animation: bool
    :param animation_duration: The total duration of the animation (in
                               seconds). ``animation_duration`` is ignored if
                               the animation is disabled. Default is one
                               second.
    :type animation_duration: int | Decimal | None
    """

    def __init__(
        self,
        lines: list[list[Token]],
        font: TTFont,
        *,
        line_height: int | float = _DEFAULT_LINE_HEIGHT,
        line_factor: int | float = _DEFAULT_LINE_FACTOR,
        color_scheme: ColorScheme = 'light',
        background: bool = False,
        animation: bool = False,
        animation_duration: int | Decimal | None = None,
    ) -> None:
        self.lines = lines
        self.text_height = line_height
        self.line_height = line_factor
        self.font = font
        self.color_scheme = color_scheme
        self.background = background
        self.animation = animation
        self.animation_duration = (
            (
                animation_duration
                if animation_duration is not None
                else _DEFAULT_ANIMATION_DURATION
            )
            if animation
            else None
        )

    def _get_height(self) -> int | float:
        """
        Returns the height of the code canvas.

        :return: The height of the code canvas.
        :rtype: int | float
        """

        return self.line_height * self.text_height * len(self.lines)

    def _get_glyph_width(self, character: int) -> float:
        """
        Returns the width of a particular character glyph.
        
        :param character: The character.
        :type character: int

        :returns: The height of the character glyph.
        :rtype: float
        """

        glyph_name = self.font.getBestCmap()[character]

        hhea = self.font['hhea']
        natural_line_height = hhea.ascent - hhea.descent + hhea.lineGap
        scale = self.text_height / natural_line_height

        advance_width, _ = self.font['hmtx'][glyph_name]
        return advance_width * scale

    def _get_width(self) -> float:
        """
        Returns the width of the code canvas. It is the width of the longest
        line.

        :return: The width of the canvas.
        :rtype: float
        """

        longest_line = 0
        for line in self.lines:
            line_length = 0
            for token in line:
                line_length += sum(
                    [
                        self._get_glyph_width(ord(character))
                        for character in token.text
                    ]
                )
            if line_length > longest_line:
                longest_line = line_length

        return longest_line

    def __str__(self) -> int:
        return '\n'.join(
            ''.join(
                token.text
                for token in line
            )
            for line in self.lines
        )

    def render(self) -> SVGNode:
        """
        Renders the code and returns it as an SVG.

        :return: The code as an SVG.
        :rtype: SVGNode
        """

        width = self._get_width()
        height = self._get_height()

        body = []
        if self.background:
            body.append(
                create_path(
                    f'M0 0h{width}v{height}h{-width}z',
                    fill=colors.background.get_value(self.color_scheme),
                    stroke_width=0,
                )
            )

        current_x = 0
        current_y = 0
        current_delay = Decimal(0)

        if self.animation:
            delay_step = (
                self.animation_duration
                / (Decimal(len(str(self))) - 1)
            )
        else:
            delay_step = 0

        for line in self.lines:
            for token in line:
                for character in token.text:
                    body.append(
                        FontTransformer(self.font).transform_glyph_to_svg(
                            ord(character),
                            self.text_height,
                            root_svg=False,
                            x=current_x,
                            y=current_y,
                            color=(
                                token.color.get_value(self.color_scheme)
                                if token.color is not None
                                else None
                            ),
                            visibility_delay=current_delay,
                        )
                    )
                    current_x += self._get_glyph_width(ord(character))
                    current_delay += delay_step
            current_x = 0
            current_y += self.line_height * self.text_height
        return create_svg(body, width=width, height=height)
