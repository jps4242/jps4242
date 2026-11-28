from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

class FontConverter:
    """
    An SVG converter for fonts.

    :param font: The font object.
    :type font: TTFont
    """

    def __init__(self, font: TTFont) -> None:
        self.font = font

    def convert_character_to_svg(
        self,
        character: int,
        height: int,
    ) -> str:
        """
        Converts a character to an SVG using the font.

        :param character: The character.
        :type character: int
        :param height: The height of the glyph. The width will be set according
                       to the height.
        :type height: int

        :return: The SVG path commands for the glyph.
        :rtype: str
        """

        glyph_set = self.font.getGlyphSet()
        glyph_name = self.font.getBestCmap()[character]
        glyph = glyph_set[glyph_name]

        hhea = self.font['hhea']

        ascent = hhea.ascent
        descent = hhea.descent
        line_gap = hhea.lineGap

        bounds_pen = BoundsPen(glyph_set)
        glyph.draw(bounds_pen)

        natural_line_height = ascent - descent + line_gap
        scale = height / natural_line_height

        pen = SVGPathPen(glyph_set)
        transform_pen = TransformPen(
            pen,
            (
                scale, 0,
                0, -scale,
                0, ascent * scale
            ),
        )
        glyph.draw(transform_pen)

        return pen.getCommands()
