from dataclasses import dataclass

__all__ = [
    'SVGNode',
    'create_svg',
    'create_path',
    'create_use',
    'create_style',
    'create_text',
]


@dataclass
class SVGNode:
    """
    A class representing an SVG node.

    :param tag: The tag name.
    :type tag: str
    :param attributes: The SVG attributes as a dictionary.
    :type attributes: dict[str, str]
    :param body: The body of the node as a list of other SVG nodes.
                 If it is ``None``, the node will have no body.
    :type body: list[SVGNode | str] | None
    :param format: Indicates whether the node may be formatted when converting
                   the node to a string using pretty output. Setting it to
                   ``False`` does not make sense if the node body does not
                   contain text nodes.
    :type format: bool
    """

    tag: str
    attributes: dict[str, str]
    body: list[SVGNode | str] | None = None
    format: bool = True

    def to_string(self, pretty: bool = False) -> str:
        """
        Converts the SVG node to a string.

        :param pretty: Indicates whether line breaks should be used and
                       whether the string should be formatted. Pretty output
                       can be helpful during debugging, but should be avoided
                       if the SVG is exported for sharing or for serving via
                       a webserver, since a well-formatted SVG file is larger
                       than a minified SVG file.
        :type pretty: bool

        :return: The SVG node as a string.
        :rtype: str
        """

        def convert_svg_node_to_string(
            node: SVGNode,
            level: int = 0,
        ) -> str:
            str_repr = level * ('    ' if pretty else '')
            str_repr += f'<{node.tag}'
            for key, value in node.attributes.items():
                value = str(value) \
                    .replace('&', '&amp;') \
                    .replace('<', '&lt;') \
                    .replace('"', '&quot;')
                str_repr += f' {key}="{value}"'
            if node.body is None:
                if pretty:
                    str_repr += ' '
                str_repr += '/>'
                if pretty:
                    str_repr += '\n'
            else:
                str_repr += '>'
                if pretty and node.format:
                    str_repr += '\n'
                for element in node.body:
                    if not isinstance(element, type(self)):
                        element = element \
                            .replace('&', '&amp;') \
                            .replace('<', '&lt;') \
                            .replace('>', '&gt;')
                    if pretty and node.format:
                        if isinstance(element, type(self)):
                            str_repr += convert_svg_node_to_string(element, level + 1)
                        else:
                            node_str_repr = ''
                            lines = (str(element).split('\n'))
                            for line in lines:
                                node_str_repr += (level + 1) * '    '
                                node_str_repr += line
                            str_repr += node_str_repr.strip('\n') + '\n'
                    else:
                        str_repr += str(element)
                str_repr += level * ('    ' if pretty and node.format else '')
                str_repr += f'</{node.tag}>'
                if pretty:
                    str_repr += '\n'
            return str_repr

        return convert_svg_node_to_string(self)

    def __str__(self) -> str:
        return self.to_string()

def create_svg(
    body: list[SVGNode],
    *,
    root: bool = True,
    width: int | float | None = None,
    height: int | float | None = None,
    view_box: str | None = None,
    x: int | float | None = None,
    y: int | float | None = None,
) -> SVGNode:
    """
    Creates an SVG SVG element (``<svg>``).

    :param body: The SVG body.
    :type body: list[SVGNode]
    :param root: Indicates whether this is the root SVG element. If ``True``,
                 the ``xmlns`` attribute will be added.
    :type root: bool
    :param width: The width of the SVG (``width`` attribute). If ``None``, no
                  width will ne set.
    :type width: int | float | None
    :param height: The height of the SVG (``height`` attribute). If ``None``,
                   no height will be set.
    :type height: int | float | None
    :param view_box: The view box of the SVG (``viewBox`` attribute). If
                     ``None``, no view box will be set.
    :type view_box: str | None
    :param x: The x position of the SVG (``x`` attribute). If ``None``, no x
              position will be set. Specifying the position makes no sense if
              this is the root SVG element.
    :type x: int | float | None
    :param y: The y position of the SVG (``y`` attribute). If ``None``, no y
              position will be set. Specifying the position makes no sense if
              this is the root SVG element.
    :type y: int | float | None

    :return: The SVG element.
    :rtype: SVGNode
    """

    attributes = {}
    if root:
        attributes['xmlns'] = 'http://www.w3.org/2000/svg'
    if width is not None:
        attributes['width'] = str(width)
    if height is not None:
        attributes['height'] = str(height)
    if view_box is not None:
        attributes['viewBox'] = view_box
    if x is not None:
        attributes['x'] = x
    if y is not None:
        attributes['y'] = y
    return SVGNode('svg', attributes, body)


def create_path(
    path: str,
    *,
    fill: str | None = None,
    stroke_color: str | None = None,
    stroke_width: int | float | None = None,
    stroke_linejoin: str | None = None,
    stroke_linecap: str | None = None,
    class_: str | None = None,
    style: str | None = None,
    visibility_delay: int | float = 0,
    fade_in_duration: int | float | None = None,
) -> SVGNode:
    """
    Creates an SVG path element (``<path>``).

    :param path: The path definition (``d`` attribute).
    :type path: str
    :param fill: The fill color (``fill`` attribute). If it is ``None``, no
                 no fill color will be set.
    :type fill: str | None
    :param stroke_color: The stroke color (``stroke`` attribute). If it is
                         ``None``, no stroke color will be set.
    :type stroke_color: str | None
    :param stroke_width: The stroke width (``stroke-width`` attribute). If it
                         is ``None``, no stroke width will be set.
    :type stroke_width: int | float | None
    :param stroke_linejoin: The shape at the corners (``stroke-linejoin``
                            attribute). If it is ``None``, no shape will be
                            set.
    :type stroke_linejoin: str | None
    :param stroke_linecap: The shape at the end of open subpaths
                           (``stroke-linecap`` attribute). If it is ``None``,
                           no shape will be set.
    :type stroke_linecap: str | None
    :param class_: The class list (``class`` attribute). If it is ``None``, no
                   class list will be set.
    :type class_: str | None
    :param style: The inline CSS (``style`` attribute). If it is ``None``, no
                  inline CSS will be set.
    :type style: str | None
    :param visibility_delay: The delay before the path becomes visible (in
                             seconds). If ``0``, there will be no delay. This
                             is the default value.
    :type visibility_delay: int | float
    :param fade_in_duration: The duration of the fade-in animation
                                        of the visibility (in seconds). If
                                        ``None``, the path will be displayed
                                        without a fade-in animation. The
                                        animation starts when after the
                                        visibility delay. If no
                                        ``visibility_delay`` is set, the fade-
                                        in animation will start immediately.
    :type fade_in_duration: int | float | None

    :return: The SVG path.
    :rtype: SVGNode
    """

    attributes = {'d': path}
    if fill is not None:
        attributes['fill'] = fill
    if stroke_color is not None:
        attributes['stroke'] = stroke_color
    if stroke_width is not None:
        attributes['stroke-width'] = stroke_width
    if stroke_linejoin is not None:
        attributes['stroke-linejoin'] = stroke_linejoin
    if stroke_linecap is not None:
        attributes['stroke-linecap'] = stroke_linecap
    if class_ is not None:
        attributes['class'] = class_
    if style is not None:
        attributes['style'] = style

    body = []
    if fade_in_duration is not None:
        attributes['opacity'] = '0'
        # fade-in animation enabled; it does not matter whether the delay is 0
        # or not -> `<animate>` element
        body.append(
            SVGNode(
                'animate',
                {
                    'attributeName': 'opacity',
                    'from': '0',
                    'to': '1',
                    'begin': f'{visibility_delay}s',
                    'dur': f'{fade_in_duration}s',
                    'fill': 'freeze',
                },
            )
        )
    elif visibility_delay != 0:
        attributes['opacity'] = '0'
        # no fade-in animation and a delay -> `<set>` element
        body.append(
            SVGNode(
                'set',
                {
                    'attributeName': 'opacity',
                    'from': '0',
                    'to': '1',
                    'begin': f'{visibility_delay}s',
                    'fill': 'freeze',
                },
            )
        )




    return SVGNode('path', attributes, body if body else None)


def create_use(
    definition: str,
    attributes: dict[str, str] = {},
    body: list[SVGNode] | None = None,
) -> SVGNode:
    """
    Creates an SVG ``<use>`` element to reuse the definition with the
    specified ID.

    :param definition: The definition to reuse.
    :type definition: str
    :param attributes: The attributes that will be set on the ``<use>``
                       element. Attributes set here override the corresponding
                       attributes of the reused element.
    :type attributes: dict[str, str]
    :param body: The body of the element. If ``None``, the ``<use>`` element
                 not have a body.
    :type body: list[SVGNode] | None

    :return: The ``<use>`` SVG element.
    :rtype: SVGNode
    """

    attributes['href'] = definition

    return SVGNode('use', attributes, body)


def create_style(css: str) -> SVGNode:
    """
    Creates an SVG ``<style>`` element.

    :param css: The CSS for the ``<style>`` element.
    :type css: str

    :return: The ``<style>`` SVG element.
    :rtype: SVGNode
    """

    return SVGNode('style', {}, [css])


def create_text(
    text: str,
    *,
    x: int | float | None = None,
    y: int | float | None = None,
) -> SVGNode:
    """
    Creates an SVG text element (``<text>``).

    :param text: The text.
    :type text: str
    :param x: The x position of the text (``x`` attribute). If ``None``, no x
              position will be set.
    :type x: int | float | None
    :param y: The y position of the text (``y`` attribute). If ``None``, no y
              position will be set.
    :type y: int | float | None

    :return: The SVG element.
    :rtype: SVGNode
    """

    attributes = {}
    if x is not None:
        attributes['x'] = x
    if y is not None:
        attributes['y'] = y
    return SVGNode('text', attributes, [text])
