
"""Probability calculations for Narxoz Buffet Rush.

Waiting times are illustrative examples, not measured campus data.
The project uses probability concepts from Weeks 1–5.
"""

from dataclasses import dataclass
from math import isfinite

DEFAULT_OBSERVATIONS = {
    "1": [
        1, 1.5, 2, 2, 2.5, 3, 3, 3.5, 4, 4,
        4.5, 5, 5, 5.5, 6, 6.5, 7, 8, 9, 10
    ],
    "2": [
        1, 1.5, 2, 2, 2, 2.5, 2.5, 3, 3,
        3.5, 3.5, 4, 4, 4.5, 5, 5.5, 6, 7, 8, 9
    ],
    "3_same": [
        4, 4, 4.5, 4.5, 5, 5,
        5, 5.5, 5.5, 5.5, 6, 6
    ],
    "3_other": [
        6, 6.5, 7, 7.5, 8, 8, 8.5, 9,
        9.5, 10, 10, 10.5, 11, 11.5, 12, 13
    ],
    "4": [
        3, 3.5, 4, 4.5, 4.5, 5, 5.5, 6,
        6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10
    ],
    "5": [
        2, 2, 2.5, 2.5, 3, 3, 3.5, 3.5,
        4, 4, 4.5, 5, 5, 5.5, 6, 7
    ],
}

CHOICE_WEIGHTS = {
    "equal": [0.20] * 5,
    "popular_third": [0.12, 0.13, 0.50, 0.12, 0.13],
}


def group_for(buffet: int, origin: int) -> str:
    if buffet == 3:
        return "3_same" if origin == 3 else "3_other"
    return str(buffet)


def move_minutes(
    source: int,
    target: int,
    pace: float = 1.0
) -> float:
    if not (1 <= source <= 5 and 1 <= target <= 5):
        raise ValueError("Floor must be between 1 and 5")
    if pace <= 0:
        raise ValueError("Invalid walking speed")

    down = max(0, source - target) * 1.5
    up = max(0, target - source) * 2.25

    return (down + up) * pace


@dataclass(frozen=True)
class Settings:
    origin: int = 3
    buffet: int = 3
    destination: int = 3
    break_minutes: float = 15
    buy_minutes: float = 1
    eat_minutes: float = 5
    crowd_factor: float = 1
    pace_factor: float = 1


@dataclass(frozen=True)
class Result:
    floor: int
    group: str
    travel: float
    sample_count: int
    success_count: int
    probability: float
    average_wait: float
    average_total: float
    average_eating_window: float
    min_eating_window: float
    max_eating_window: float
    average_margin: float
    observed_waits: tuple[float, ...]
    total_times: tuple[float, ...]


def evaluate(
    settings: Settings,
    observations: dict[str, list[float]]
) -> Result:
    if (
        settings.break_minutes <= 0
        or settings.buy_minutes < 0
        or settings.eat_minutes < 0
    ):
        raise ValueError("Invalid time settings")

    if settings.crowd_factor <= 0:
        raise ValueError("Invalid crowd factor")

    group = group_for(settings.buffet, settings.origin)
    raw = observations[group]

    if not raw or any(
        not isfinite(value) or value < 0 for value in raw
    ):
        raise ValueError("Invalid waiting times")

    travel = (
        move_minutes(
            settings.origin,
            settings.buffet,
            settings.pace_factor
        )
        + move_minutes(
            settings.buffet,
            settings.destination,
            settings.pace_factor
        )
    )

    waits = tuple(
        value * settings.crowd_factor for value in raw
    )

    totals = tuple(
        travel
        + wait
        + settings.buy_minutes
        + settings.eat_minutes
        for wait in waits
    )

    eating_windows = tuple(
        settings.break_minutes
        - travel
        - wait
        - settings.buy_minutes
        for wait in waits
    )

    success_count = sum(
        total <= settings.break_minutes + 1e-9
        for total in totals
    )

    average_wait = sum(waits) / len(waits)
    average_total = sum(totals) / len(totals)

    return Result(
        floor=settings.buffet,
        group=group,
        travel=travel,
        sample_count=len(waits),
        success_count=success_count,
        probability=success_count / len(waits),
        average_wait=average_wait,
        average_total=average_total,
        average_eating_window=(
            sum(eating_windows) / len(eating_windows)
        ),
        min_eating_window=min(eating_windows),
        max_eating_window=max(eating_windows),
        average_margin=settings.break_minutes - average_total,
        observed_waits=waits,
        total_times=totals,
    )


def all_buffets(
    settings: Settings,
    observations: dict[str, list[float]]
) -> list[Result]:
    results = []

    for floor in range(1, 6):
        new_settings = Settings(
            **{**vars(settings), "buffet": floor}
        )
        results.append(evaluate(new_settings, observations))

    return results


def law_of_total_probability(
    results: list[Result],
    weights: list[float]
) -> float:
    if len(results) != 5 or len(weights) != 5:
        raise ValueError("Five buffets are required")

    if abs(sum(weights) - 1) > 1e-8:
        raise ValueError("Weights must sum to 1")

    return sum(
        result.probability * weight
        for result, weight in zip(results, weights)
    )


def independence_check(
    results: list[Result],
    weights: list[float]
):
    p_a = law_of_total_probability(results, weights)
    p_b = weights[2]
    p_joint = results[2].probability * p_b
    p_product = p_a * p_b

    return p_a, p_b, p_joint, p_product


def best_buffet(
    settings: Settings,
    observations: dict[str, list[float]]
) -> int:
    results = all_buffets(settings, observations)

    best = sorted(
        results,
        key=lambda result: (
            -result.probability,
            result.average_total,
            result.floor
        )
    )

    return best[0].floor
