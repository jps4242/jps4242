from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

from .svg import (
    create_svg,
    create_path,
    SVGNode,
)

class FontTransformer:
    """
    A SVG transformer for fonts.

    :param font: The font object.
    :type font: TTFont
    """

    def __init__(self, font: TTFont) -> None:
        self.font = font

    def transform_glyph_to_svg(
        self,
        character: int,
        height: int,
        *,
        root_svg: bool = True,
        x: int | float | None = None,
        y: int | float | None = None,
        color: str | None = None,
        visibility_delay: int | float = 0,
    ) -> SVGNode:
        """
        Transforms a glyph to an SVG using the font.

        :character: The character.
        :type character: int
        :height: The height of the glyph. The width will be set according to
                 the height.
        :type height: int
        :param root_svg: Indicates whether it is the root SVG. If ``True``, a
                         root SVG node will be created.
        :type root_svg: bool
        :param x: The x position of the SVG. It makes no sense to set a
                  position on a root SVG.
        :type x: int | float | None
        :param y: The y position of the SVG. It makes no sense to set a
                  position on a root SVG.
        :type y: int | float | None
        :param color: The color of the glyph.
        :type color: str | None
        :param visibility_delay: The delay before the path becomes visible (in
                                 seconds).
        :type visibility_delay: int | float

        :returns: The glyph as an SVG.
        :rtype: SVGNode
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

        advance_width, _ = self.font['hmtx'][glyph_name]
        width = advance_width * scale

        return create_svg(
            [
                create_path(
                    pen.getCommands(),
                    stroke_color='none',
                    fill=color if color is not None else None,
                    visibility_delay=visibility_delay,
                    fade_in_duration=0.1 if visibility_delay else None,
                )
            ],
            root=root_svg,
            width=width,
            height=height,
            view_box=f'0 0 {width} {height}',
            x=x,
            y=y,
        )
