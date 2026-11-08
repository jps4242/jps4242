from dataclasses import dataclass
from decimal import Decimal
from fontTools.ttLib import TTFont

from .fonts import FontConverter
from .svg import SVGNode, create_path, create_style, create_svg, create_use
from .tokens import ColorScheme, colors, Token

__all__ = ['SVGCode']


_DEFAULT_LINE_HEIGHT = 16
_DEFAULT_LINE_FACTOR = 1.2
_DEFAULT_ANIMATION_DURATION = Decimal(0.5)


class SVGCodeArea:
    """
    A code area of an SVG code generator.

    :param lines: A list of the code lines. Each line is a list of tokens.
    :type lines: list[list[Token]]
    :param background: Indicates a background will be added to the SVG.
    :type background: bool
    :param animation: Indicates whether the code will be animated. If it is
                      animated, each character appears with a delay which is
                      increased after each character. Each character fades in
                      within 0.1 seconds.
    :type animation: bool
    :param animation_duration: The total duration of the animation (in
                               seconds). ``animation_duration`` is ignored if
                               the animation is disabled. Default is 0.5
                               seconds.
    :type animation_duration: int | Decimal | None
    :param line_numbers: Indicates whether line numbers will be displayed.
    :type line_numbers: bool
    :param animate_line_numbers: Indicates whether the line numbers will be
                                 part of the animation.
                                 ``animate_line_numbers`` is ignored if the
                                 animation and/or line numbers are disabled.
    :type animate_line_numbers: bool
    :param animation_delay: The delay before the animation starts.
                            ``animation_delay`` is ignored if the animation is
                            disabled.
    :type animation_delay: Decimal | None
    """

    def __init__(
        self,
        lines: list[list[Token]],
        *,
        background: bool = False,
        animation: bool = False,
        animation_duration: int | Decimal | None = None,
        line_numbers: bool = True,
        animate_line_numers: bool = False,
        animation_delay: Decimal | None = None,
    ) -> None:
        self.lines = lines
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
        self.line_numbers = line_numbers
        self.animate_line_numers = animate_line_numers
        self.animation_delay = (
            (
                animation_delay
                if animation_delay is not None
                else Decimal(0)
            )
            if animation
            else None
        )

    def __str__(self) -> int:
        return '\n'.join(
            ''.join(
                token.text
                for token in line
            )
            for line in self.lines
        )


@dataclass
class SVGCode:
    """
    An SVG code generator.

    :param areas: The code areas.
    :type areas: list[SVGCodeArea]
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
    """

    def __init__(
        self,
        areas: list[SVGCodeArea],
        font: TTFont,
        *,
        line_height: int | float = _DEFAULT_LINE_HEIGHT,
        line_factor: int | float = _DEFAULT_LINE_FACTOR,
        color_scheme: ColorScheme = 'light',
    ) -> None:
        self.areas = areas
        self.font = font
        self.line_height = line_height
        self.line_factor = line_factor
        self.color_scheme = color_scheme

    def _get_glyph_width(self, character: int) -> float:
        """
        Returns the width of a particular character glyph.

        :param character: The character.
        :type character: int

        :return: The height of the character glyph.
        :rtype: float
        """

        glyph_name = self.font.getBestCmap()[character]

        hhea = self.font['hhea']
        natural_line_height = hhea.ascent - hhea.descent + hhea.lineGap
        scale = self.line_height / natural_line_height

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
        for area in self.areas:
            for line in area.lines:
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

    def _get_height(self) -> int | float:
        """
        Returns the height of the code canvas.

        :return: The height of the code canvas.
        :rtype: int | float
        """

        return (
            self.line_factor
            * self.line_height
            * sum(len(area.lines) for area in self.areas)
        )

    def create_character_map(self) -> tuple[dict[str, SVGNode], list[str]]:
        """
        Creates a mapping of the characters of all code and their glyphs as
        SVG paths.

        :return: The mapping of the characters (keys) and their glyphs as SVG
                 paths (values) and the list of characters with only one
                 color.
        :rtype: tuple[dict[str, SVGNode], list[str]]
        """

        # list instead of set to preserve order
        characters_raw = []
        for area in self.areas:
            for line in area.lines:
                for token in line:
                    for character in token.text:
                        character_with_color = (
                            character,
                            (
                                token.color.get_value(self.color_scheme)
                                if token.color is not None else None
                            )
                        )
                        if character_with_color not in characters_raw:
                            characters_raw.append(character_with_color)

        # find all line number digits that are used
        digits = '1234567890'[
            :max(
                (
                    min(10, len(area.lines))
                    for area in self.areas
                    if area.line_numbers
                ),
                default=0,
            )
        ]
        line_numbers_color = colors.line_numbers.get_value(
            self.color_scheme
        )
        # find combinations of characters and colors also for line numbers
        for digit in digits:
            digit_with_color = (digit, line_numbers_color)
            if digit_with_color not in characters_raw:
                characters_raw.append(digit_with_color)

        # all characters
        characters = set(character for character, _ in characters_raw)
        converter = FontConverter(self.font)
        defs = {}
        # list instead of set to preserve order
        characters_with_unique_color = []

        # generate the SVG paths and collect the characters with a unique
        # color
        for character in characters:
            # find all colors this character has
            character_colors = set(
                color for char, color in characters_raw if char == character
            )
            color = None
            # check whether the character has only one color
            if len(character_colors) == 1:
                if character not in characters_with_unique_color:
                    characters_with_unique_color.append(character)
                color = character_colors.pop()
            character_ord = ord(character)
            node = create_path(
                converter.convert_character_to_svg(
                    character_ord, self.line_height
                ),
                fill=color, # fill path with the color if the color is unique
                stroke_color='none',
            )
            node.attributes['id'] = f'c{character_ord}'
            defs[character] = node

        return dict(sorted(defs.items())), characters_with_unique_color

    def render(self) -> SVGNode:
        """
        Renders the code and returns it as an SVG.

        :return: The code as an SVG.
        :rtype: SVGNode
        """

        character_map, characters_with_unique_color = (
            self.create_character_map()
        )

        body = [
            SVGNode('defs', {}, character_map.values()),
        ]
        if any(area.animation for area in self.areas):
            # add CSS for animations
            body.append(
                create_style(
                    '@keyframes f{from{opacity:0}to{opacity:1}}.c{animation:f'
                    ' 0.1s forwards;opacity:0}'
                )
            )

        current_x = 0
        current_y = 0

        max_width = 0

        for area in self.areas:
            line_index_digits = len(str(len(area.lines)))
            widest_line_number = 0

            characters_count = len(str(area))
            if area.line_numbers:
                characters_count += line_index_digits * len(area.lines)
            if area.animation:
                delay_step = (
                    area.animation_duration
                    / (Decimal(characters_count) - 1)
                )
            else:
                delay_step = 0
            current_delay = area.animation_delay

            for line_index, line in enumerate(area.lines):
                if area.line_numbers:
                    line_number = str(line_index + 1).rjust(line_index_digits)
                    for line_digit in line_number:
                        character_ord = ord(line_digit)
                        glyph_width = self._get_glyph_width(character_ord)

                        use_attributes = {}
                        if area.animate_line_numers and area.animation:
                            # set attributes for line number animation
                            use_attributes['class'] = 'c'
                            use_attributes['style'] = (
                                f'animation-delay:{current_delay}s'
                            )
                        if line_digit not in characters_with_unique_color:
                            # set character color if it is not None
                            color = colors.line_numbers.get_value(
                                self.color_scheme
                            )
                            if color is not None:
                                use_attributes['fill'] = (
                                    colors.line_numbers.get_value(
                                        self.color_scheme
                                    )
                                )

                        body.append(
                            create_svg(
                                [
                                    # reference to the character path definition
                                    create_use(
                                        f'#c{character_ord}',
                                        use_attributes,
                                    )
                                ],
                                root=False,
                                width=glyph_width,
                                height=self.line_height,
                                view_box=f'0 0 {glyph_width} {self.line_height}',
                                x=current_x,
                                y=current_y,
                            )
                        )
                        current_x += self._get_glyph_width(character_ord)
                        if area.animate_line_numers:
                            current_delay += delay_step
                    space = 2 * self._get_glyph_width(32)
                    current_x += space
                    line_number_width = sum(
                        self._get_glyph_width(ord(character))
                        for character in line_number
                    ) + space
                    if line_number_width > widest_line_number:
                        widest_line_number = line_number_width

                for token in line:
                    for character in token.text:
                        character_ord = ord(character)
                        glyph_width = self._get_glyph_width(character_ord)

                        use_attributes = {}
                        if area.animation:
                            # set attributes for animation
                            use_attributes['class'] = 'c'
                            use_attributes['style'] = (
                                f'animation-delay:{current_delay}s'
                            )
                        if character not in characters_with_unique_color:
                            # set character color if it is not None
                            color = (
                                token.color.get_value(self.color_scheme)
                                if token.color is not None else None
                            )
                            if color is not None:
                                use_attributes['fill'] = (
                                    token.color.get_value(self.color_scheme)
                                    if token.color is not None else None
                                )

                        body.append(
                            create_svg(
                                [
                                    # reference to the character path definition
                                    create_use(
                                        f'#c{character_ord}',
                                        use_attributes,
                                    )
                                ],
                                root=False,
                                width=glyph_width,
                                height=self.line_height,
                                view_box=f'0 0 {glyph_width} {self.line_height}',
                                x=current_x,
                                y=current_y,
                            )
                        )
                        current_x += self._get_glyph_width(ord(character))
                        current_delay += delay_step
                current_x = 0
                current_y += self.line_factor * self.line_height

            width = self._get_width() + widest_line_number
            if width > max_width:
                max_width = width
            height = self.line_height * self.line_factor * len(area.lines)

        current_y = 0
        for area in self.areas:
            height = self.line_height * self.line_factor * len(area.lines)
            if area.background:
                body.insert(
                    0,
                    create_path(
                        f'M0 {current_y}h{max_width}v{height}h{-max_width}z',
                        fill=colors.background.get_value(self.color_scheme),
                        stroke_width=0,
                    )
                )
            current_y += height

        return create_svg(body, width=width, height=self._get_height())
