from dataclasses import dataclass

__all__ = ['SVGNode', 'create_svg', 'create_path']


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
    :type body: list[SVGNode] | None
    """

    tag: str
    attributes: dict[str, str]
    body: list[SVGNode] | None = None

    def __str__(self) -> str:
        str_repr = f'<{self.tag}'
        for key, value in self.attributes.items():
            str_repr += f' {key}="{value}"'
        if self.body is None:
            str_repr += '/>'
        else:
            str_repr += '>'
            for node in self.body:
                str_repr += str(node)
            str_repr += f'</{self.tag}>'
        return str_repr


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
    :type x: int | float
    :param y: The y position of the SVG (``y`` attribute). If ``None``, no y
              position will be set. Specifying the position makes no sense if
              this is the root SVG element.
    :type y: int | float

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
    return SVGNode('path', attributes, None)
