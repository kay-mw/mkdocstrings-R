import warnings
from collections.abc import Generator


def google_docstring_kitchen_sink(
    numbers: list[float],
    *,
    scale: float = 1.0,
    clamp: float | None = None,
    **extras: float,
) -> Generator[float, float | None, tuple[float, float]]:
    """Single-function visual reference for Google-style docstring sections.

    Args:
        numbers: Input values to process.

    Keyword Args:
        scale: Multiplier applied to each value.
        clamp: Optional maximum contribution per step after scaling and extras.

    Other Args:
        **extras: Named additive offsets applied to every step.

    Yields:
        Running total after each processed value.

    Receives:
        Optional increment added to the next step via ``send``.

    Returns:
        A tuple of ``(final_total, mean_total)`` when the generator completes.

    Raises:
        ValueError: If ``numbers`` is empty.

    Warns:
        UserWarning: If ``final_total`` is unusually large.

    Examples:
        >>> gen = google_docstring_kitchen_sink([1.0, 2.0], scale=2.0, bonus=0.5)
        >>> next(gen)
        2.5
        >>> gen.send(1.0)
        8.0
    """

    if not numbers:
        raise ValueError("numbers must not be empty")

    running_total = 0.0
    carried = 0.0
    extra_offset = sum(float(value) for value in extras.values())

    for raw in numbers:
        step = raw * scale + carried + extra_offset
        if clamp is not None:
            step = min(step, clamp)
        running_total += step
        incoming = yield running_total
        carried = 0.0 if incoming is None else float(incoming)

    if running_total > 100.0:
        warnings.warn("Large total may indicate suspicious inputs", UserWarning)

    return running_total, running_total / len(numbers)
