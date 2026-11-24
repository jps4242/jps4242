from dataclasses import dataclass
from decimal import Decimal
from fontTools.ttLib import TTFont

from .animations import (
    BezierCurve,
    time_for_progress,
    validate_timing_function,
)
from .fonts import FontConverter
from .svg import (
    SVGNode,
    create_path,
    create_style,
    create_svg,
    create_text,
    create_use,
)
from .tokens import Color, ColorScheme, colors, Token

__all__ = ['SVGCode']


_DEFAULT_LINE_HEIGHT = 16
_DEFAULT_LINE_FACTOR = 1.2
_DEFAULT_ANIMATION_DURATION = Decimal(0.5)
_DEFAULT_ANIMATION_TIMING_FUNCTION = (BezierCurve([(0, 0), (1, 1)]),)
_DEFAULT_ANIMATION_FADE_IN_DURATION = Decimal('0.1')


class SVGCodeArea:
    """
    A code area of an SVG code generator.

    :param lines: A list of the code lines. Each line is a list of tokens.
    :type lines: list[list[Token]]
    :param background: The background that will be added to the SVG. If
                       ``True``, the default background color will be used. If
                       ``False``, no background will be added. This is the
                       default value. It can also be a custom color.
    :type background: bool | Color
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
    :param animation_timing_function: The Bézier curve or connected Bézier
                                      curves which define the timing function
                                      of the animation. The domain for the
                                      curve(s) is the set from the point (0,
                                      0) to the point (1, 1). The coordinate
                                      of each point consists of the relative
                                      time and the relative animation
                                      progress. Both the animation progress
                                      and the time must be monotonic. If the
                                      animation is disabled,
                                      ``animation_timing_function`` is
                                      ignored. The default timing function is
                                      linear.
    :type animation_timing_function: BezierCurve | list[BezierCurve] |
                                     tuple[BezierCurve, ...] | None
    :type animation_fade_in_duration: The time it takes for a character to
                                      fade in. If the animation is disabled,
                                      ``animation_fade_in_duration`` is
                                      ignored. The default duration is 0.1
                                      seconds.
    :param animation_fade_in_duration: int | Decimal | None
    :param padding_top: The padding which will be inserted at the bottom.
    :type padding_top: int | float
    :param padding_bottom: The padding which will be inserted at the bottom.
    :type padding_bottom: int | float
    """

    def __init__(
        self,
        lines: list[list[Token]],
        *,
        background: bool | Color = False,
        animation: bool = False,
        animation_duration: int | Decimal | None = None,
        line_numbers: bool = True,
        animate_line_numers: bool = False,
        animation_delay: Decimal | None = None,
        animation_timing_function: (
            BezierCurve | list[BezierCurve] | tuple[BezierCurve, ...] | None
        ) = None,
        animation_fade_in_duration: int | Decimal | None = None,
        padding_top: int | float = 0,
        padding_bottom: int | float = 0,
    ) -> None:
        self.lines = lines
        self.background = (
            colors.background
            if background == True
            else (
                background
                if isinstance(background, Color)
                else None
            )
        )
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
        self.animation_timing_function = (
            (
                validate_timing_function(animation_timing_function)
                if animation_timing_function is not None
                else _DEFAULT_ANIMATION_TIMING_FUNCTION
            )
            if animation else None
        )
        self.animation_fade_in_duration = (
            (
                animation_fade_in_duration
                if animation_fade_in_duration is not None
                else _DEFAULT_ANIMATION_FADE_IN_DURATION
            )
            if animation
            else None
        )
        self.padding_top = padding_top
        self.padding_bottom = padding_bottom

    def is_animated(self) -> bool:
        """
        Checks whether there is an animation in the code area. An area is
        animated if it contains characters and/or animated line numbers.

        :return: Whether the code area is animated.
        :rtype: bool
        """

        if not self.animation:
            return False

        if self.line_numbers and self.lines and self.animate_line_numers:
            # line numbers are enabled and there is at least one line (even if
            # it is empty)
            return True

        for line in self.lines:
            for token in line:
                if token.text:
                    # a token contains text
                    return True

        # there are no animated line numbers and no token contains text
        return False

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
    :param accessibility: Indicates whether machine-readable SVG text elements
                          should be added to improve the accessibility of the
                          SVG, for example, for screen readers. These elements
                          are invisible. By default, no text elements are
                          added.
    :type accessibility: bool
    """

    def __init__(
        self,
        areas: list[SVGCodeArea],
        font: TTFont,
        *,
        line_height: int | float = _DEFAULT_LINE_HEIGHT,
        line_factor: int | float = _DEFAULT_LINE_FACTOR,
        color_scheme: ColorScheme = 'light',
        accessibility: bool = False,
    ) -> None:
        self.areas = areas
        self.font = font
        self.line_height = line_height
        self.line_factor = line_factor
        self.color_scheme = color_scheme
        self.accessibility = accessibility

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
            animation_fade_in_durations = list(set(
                area.animation_fade_in_duration
                for area in self.areas
                if area.animation and area.is_animated()
            ))
            if animation_fade_in_durations:
                css = '@keyframes f{from{opacity:0}to{opacity:1}}'
                animation_fade_in_durations.sort()
                unique_animation_fade_in_duration = len(
                    animation_fade_in_durations
                ) == 1
                if unique_animation_fade_in_duration:
                    css += (
                        f'.c{{animation:f {animation_fade_in_durations[0]}s forwa'
                        'rds;opacity:0}'
                    )
                    classes = None
                else:
                    css += '.c{animation:f var(--d) forwards;opacity:0}'
                    available_class_characters_first = (
                        'abdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    )
                    available_class_characters = (
                        available_class_characters_first + '0123456789c'
                    )

                    def get_class_name(value: int) -> str:
                        if value < 0:
                            raise ValueError('value must not be negative')

                        if value == 0:
                            return available_class_characters[0]

                        result = ''

                        shift = 0
                        available_characters = available_class_characters_first

                        while value:
                            result += available_characters[
                                value % len(available_characters) - shift
                            ]
                            value //= len(available_characters)
                            if not shift:
                                shift = 1
                                available_characters = available_class_characters

                        return result

                    classes = {}

                    duration_index = 0
                    for duration in animation_fade_in_durations:
                        class_name = get_class_name(duration_index)
                        classes[duration] = class_name
                        css += f'.{class_name}{{--d:{duration}s}}'
                        duration_index += 1

                # add CSS for animations
                body.append(create_style(css))

                def get_class_name_for_fade_in_duration(
                    duration: Decimal
                ) -> str:
                    if classes is not None:
                        if not unique_animation_fade_in_duration:
                            return f' {classes[duration]}'
                    return ''
        else:
            get_class_name_for_fade_in_duration = None

        current_x = 0
        current_y = 0

        widths = []

        for area in self.areas:
            current_y += area.padding_top

            line_index_digits = len(str(len(area.lines)))
            widest_line_number = 0

            # Count only characters which actually receive an animation. In
            # particular, ``str(area)`` also contains line-separator characters
            # which are not rendered as glyphs.
            characters_count = sum(
                len(token.text)
                for line in area.lines
                for token in line
            )
            if area.line_numbers and area.animate_line_numers:
                characters_count += line_index_digits * len(area.lines)
            if area.animation:
                animation_delays = []
                for animation_index in range(characters_count):
                    if characters_count <= 1:
                        relative_time = Decimal(0)
                    else:
                        relative_progress = Decimal(animation_index) / Decimal(
                            characters_count - 1
                        )
                        relative_time = time_for_progress(
                            area.animation_timing_function,
                            relative_progress,
                        )
                    animation_delays.append(
                        area.animation_delay
                        + area.animation_duration * relative_time
                    )
                animation_index = 0

                def get_animation_delay(index: int) -> Decimal:
                    return animation_delays[index]
            else:
                get_animation_delay = None

            for line_index, line in enumerate(area.lines):
                if area.line_numbers:
                    line_number = str(line_index + 1).rjust(line_index_digits)
                    for line_digit in line_number:
                        character_ord = ord(line_digit)
                        glyph_width = self._get_glyph_width(character_ord)

                        use_attributes = {}
                        if area.animate_line_numers and area.animation:
                            # set attributes for line number animation
                            use_attributes['class'] = (
                                'c'
                                + get_class_name_for_fade_in_duration(
                                    area.animation_fade_in_duration
                                )
                            )
                            use_attributes['style'] = (
                                'animation-delay:'
                                + str(get_animation_delay(animation_index))
                                + 's'
                            )
                            animation_index += 1
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
                            use_attributes['class'] = (
                                'c'
                                + get_class_name_for_fade_in_duration(
                                    area.animation_fade_in_duration
                                )
                            )
                            use_attributes['style'] = (
                                f'animation-delay:'
                                + str(get_animation_delay(animation_index))
                                + 's'
                            )
                            animation_index += 1
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
                current_x = 0
                if self.accessibility:
                    text = ''.join(token.text for token in line) + '\n'
                    text_element = create_text(
                        text,
                        x=current_x + widest_line_number,
                        y=current_y + (self.line_height * self.line_factor) / 2,
                    )
                    text_element.attributes['xml:space'] = 'preserve'
                    text_element.format = False
                    text_element.attributes['opacity'] = 0
                    # compatibility with renderers which do not support fill
                    # to ensure invisibility of the text element
                    text_element.attributes['fill-opacity'] = 0
                    body.append(text_element)
                current_y += self.line_factor * self.line_height

            widths.append(self._get_width() + widest_line_number)
            height = (
                self.line_height
                * self.line_factor
                * len(area.lines)
                + area.padding_bottom
            )
            current_y += area.padding_bottom

        width = max(widths, default=0)

        current_y = 0
        for area in self.areas:
            height = (
                self.line_height
                * self.line_factor
                * len(area.lines)
                + area.padding_top
                + area.padding_bottom
            )
            if area.background is not None:
                body.insert(
                    0,
                    create_path(
                        f'M0 {current_y}h{width}v{height}h{-width}z',
                        fill=area.background.get_value(self.color_scheme),
                        stroke_width=0,
                    )
                )
            current_y += height

        return create_svg(
            body,
            width=width,
            height=(
                self._get_height()
                + sum(area.padding_top for area in self.areas)
                + sum(area.padding_bottom for area in self.areas)
            ),
        )
