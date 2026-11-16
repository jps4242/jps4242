from decimal import Decimal, InvalidOperation, getcontext
from math import comb

__all__ = ['BezierCurve', 'validate_timing_function', 'time_for_progress']


class BezierCurve:
    """
    Represents a Bézier curve.

    :param control_points: The control points of the curve. Each point is
                           represented by a tuple of two coordinates.
    :type control_points: list[tuple[int | float | Decimal, ...]]
    """

    def __init__(self, control_points: list[tuple[float, ...]]) -> None:
        if len(control_points) < 2:
            raise ValueError(
                'a Bézier curve needs at least two control points'
            )
        if len(set(map(len, control_points))) != 1:
            raise ValueError(
                'each control point must have the same number of dimensions'
            )
        if len(control_points[0]) != 2:
            raise ValueError(
                'animation control points must be two-dimensional'
            )

        try:
            points = tuple(
                tuple(Decimal(str(value)) for value in point)
                for point in control_points
            )
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError(
                'control point coordinates must be numbers'
            ) from error
        if any(not value.is_finite() for point in points for value in point):
            raise ValueError('control point coordinates must be finite')

        self.control_points = points

    @property
    def start(self) -> tuple[Decimal, Decimal]:
        return self.control_points[0]

    @property
    def end(self) -> tuple[Decimal, Decimal]:
        return self.control_points[-1]

    def evaluate(
        self,
        parameter: Decimal | int | float,
    ) -> tuple[Decimal, Decimal]:
        """
        Evaluates the curve at a parameter.

        :param parameter: The parameter at which the curve will be evaluated.
                          It must be in the interval ``[0, 1]``.
        :type parameter: Decimal | int | float

        :return: The point on the curve at ``parameter``.
        :rtype: tuple[Decimal, Decimal]
        """

        try:
            parameter = Decimal(str(parameter))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError('the Bézier parameter must be numeric') from error
        if not 0 <= parameter <= 1:
            raise ValueError('the Bézier parameter must be between 0 and 1')
        degree = len(self.control_points) - 1

        def power(base: Decimal, exponent: int) -> Decimal:
            # Decimal raises InvalidOperation for 0 ** 0, while the
            # Bernstein basis defines that factor as 1.
            return Decimal(1) if exponent == 0 else base ** exponent

        return tuple(
            sum(
                comb(degree, index)
                * power(Decimal(1) - parameter, degree - index)
                * power(parameter, index)
                * point[dimension]
                for index, point in enumerate(self.control_points)
            )
            for dimension in range(2)
        )

    def validate_monotonic(self) -> None:
        """
        Validates the monotonicity constraints of the curve. Non-negative
        differences of consecutive control points are a sufficient condition
        for a coordinate to be non-decreasing. For the time coordinate, at
        least one positive difference is required so that time is strictly
        increasing. A zero derivative at an endpoint is valid.

        :raises ValueError: If the time coordinate is not strictly increasing
                            or the progress coordinate is decreasing.
        """

        x_differences = [
            right[0] - left[0]
            for left, right
            in zip(self.control_points, self.control_points[1:])
        ]
        y_differences = [
            right[1] - left[1]
            for left, right
            in zip(self.control_points, self.control_points[1:])
        ]
        if any(difference < 0 for difference in x_differences):
            raise ValueError(
                'the time coordinate of a timing curve must not decrease'
            )
        if not any(difference > 0 for difference in x_differences):
            raise ValueError(
                'the time coordinate of a timing curve must increase'
            )
        if any(difference < 0 for difference in y_differences):
            raise ValueError(
                'the progress coordinate of a timing curve must not decrease'
            )

    def parameter_for_progress(
        self, progress: Decimal | int | float
    ) -> Decimal:
        """
        Returns a parameter whose curve value has the requested progress.

        :param progress: The progress value for which the curve parameter is
                         searched. It must be within the progress interval of
                         this curve.
        :type progress: Decimal | int | float

        :return: The curve parameter for the requested progress.
        :rtype: Decimal

        :raises ValueError: If ``progress`` is outside this curve's progress
                            interval.
        """

        progress = Decimal(str(progress))
        start_progress, end_progress = self.start[1], self.end[1]
        if not start_progress <= progress <= end_progress:
            raise ValueError('progress is outside this timing curve')

        # y is monotonic, so bisection is deterministic and does not need a
        # polynomial root solver. The endpoint checks also handle plateaus.
        if progress == start_progress:
            return Decimal(0)
        if progress == end_progress:
            return Decimal(1)
        lower, upper = Decimal(0), Decimal(1)
        for _ in range(max(16, getcontext().prec * 4)):
            middle = (lower + upper) / Decimal(2)
            if middle == lower or middle == upper:
                return middle
            curve_progress = self.evaluate(middle)[1]
            if curve_progress == progress:
                return middle
            if curve_progress < progress:
                lower = middle
            else:
                upper = middle
        return (lower + upper) / Decimal(2)


def validate_timing_function(
    curves: BezierCurve | list[BezierCurve] | tuple[BezierCurve, ...],
) -> tuple[BezierCurve, ...]:
    """
    Normalizes and validates a possibly piecewise timing function.

    :param curves: The Bézier curve or connected Bézier curves which define
                   the timing function. The complete timing function must
                   start at ``(0, 0)`` and end at ``(1, 1)``.
    :type curves: BezierCurve | list[BezierCurve] | tuple[BezierCurve, ...]

    :return: The timing function as a tuple of Bézier curves.
    :rtype: tuple[BezierCurve, ...]

    :raises TypeError: If an element of ``curves`` is not a Bézier curve.
    :raises ValueError: If the timing function is empty, disconnected, out of
                        range, or violates the monotonicity constraints.
    """

    normalized = (
        curves,
    ) if isinstance(curves, BezierCurve) else tuple(curves)
    if not normalized:
        raise ValueError('the animation timing function must not be empty')
    for curve in normalized:
        if not isinstance(curve, BezierCurve):
            raise TypeError(
                'timing functions must contain BezierCurve objects'
            )
        if any(not 0 <= value <= 1
               for point in curve.control_points for value in point):
            raise ValueError(
                'timing curve coordinates must be between 0 and 1'
            )
        curve.validate_monotonic()

    if normalized[0].start != (Decimal(0), Decimal(0)):
        raise ValueError('the timing function must start at (0, 0)')
    for previous, current in zip(normalized, normalized[1:]):
        if previous.end != current.start:
            raise ValueError('timing curve segments must connect exactly')
    if normalized[-1].end != (Decimal(1), Decimal(1)):
        raise ValueError('the timing function must end at (1, 1)')
    return normalized


def time_for_progress(
    curves: BezierCurve | list[BezierCurve] | tuple[BezierCurve, ...],
    progress: Decimal | int | float,
) -> Decimal:
    """
    Returns the normalized time for a normalized animation progress.

    :param curves: The Bézier curve or connected Bézier curves which define
                   the timing function.
    :type curves: BezierCurve | list[BezierCurve] | tuple[BezierCurve, ...]
    :param progress: The normalized animation progress. It must be in the
                     interval ``[0, 1]``.
    :type progress: Decimal | int | float

    :return: The normalized time at which ``progress`` is reached.
    :rtype: Decimal

    :raises ValueError: If ``progress`` is outside ``[0, 1]`` or outside the
                        timing function.
    """

    progress = Decimal(str(progress))
    if not 0 <= progress <= 1:
        raise ValueError('progress must be between 0 and 1')
    for curve in validate_timing_function(curves):
        if progress <= curve.end[1]:
            parameter = curve.parameter_for_progress(progress)
            return Decimal(str(curve.evaluate(parameter)[0]))
    raise ValueError('progress is outside the timing function')
