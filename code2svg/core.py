from fontTools.ttLib import TTFont

from .fonts import FontTransformer
from .svg import SVGNode, create_svg
from .tokens import Token

__all__ = ['SVGCode']


_DEFAULT_LINE_HEIGHT = 16
_DEFAULT_LINE_FACTOR = 1.2


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
    """

    def __init__(
        self,
        lines: list[list[Token]],
        font: TTFont,
        *,
        line_height: int | float = _DEFAULT_LINE_HEIGHT,
        line_factor: int | float = _DEFAULT_LINE_FACTOR,
    ) -> None:
        self.lines = lines
        self.text_height = line_height
        self.line_height = line_factor
        self.font = font

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

    def render(self) -> SVGNode:
        """
        Renders the code and returns it as an SVG.

        :return: The code as an SVG.
        :rtype: SVGNode
        """

        body = []
        current_x = 0
        current_y = 0
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
                            color=token.color,
                        )
                    )
                    current_x += self._get_glyph_width(ord(character))
            current_x = 0
            current_y += self.line_height * self.text_height
        return create_svg(body, width=self._get_width(), height=self._get_height())
