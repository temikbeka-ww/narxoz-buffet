"""Deterministic probability calculations for Narxoz Buffet Rush.

All starter waiting-time values are *illustrative assumptions*, not measured campus data.
The core math intentionally uses only course Weeks 1–5.
"""
from dataclasses import dataclass
from math import isfinite

DEFAULT_OBSERVATIONS = {
    # Illustrated classroom scenarios, NOT actual measured waiting times.
    # Spread has been widened to avoid treating a small, overly neat table
    # as if queues had exactly the same length every day.
    "1": [1, 1.5, 2, 2, 2.5, 3, 3, 3.5, 4, 4, 4.5, 5, 5, 5.5, 6, 6.5, 7, 8, 9, 10],
    "2": [1, 1.5, 2, 2, 2, 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 5, 5.5, 6, 7, 8, 9],
    # The student is already on floor 3. Queue 4–6 min and payment 1 min
    # leave 8–10 min for eating during a 15-minute break: 3 -> 3 -> 3.
    "3_same": [4, 4, 4.5, 4.5, 5, 5, 5, 5.5, 5.5, 5.5, 6, 6],
    # Later arrivals from other floors: a longer but not automatically
    # 15–20-minute wait. Walking time is calculated separately.
    "3_other": [6, 6.5, 7, 7.5, 8, 8, 8.5, 9, 9.5, 10, 10, 10.5, 11, 11.5, 12, 13],
    "4": [3, 3.5, 4, 4.5, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10],
    "5": [2, 2, 2.5, 2.5, 3, 3, 3.5, 3.5, 4, 4, 4.5, 5, 5, 5.5, 6, 7],
}

CHOICE_WEIGHTS = {
    "equal": [0.20, 0.20, 0.20, 0.20, 0.20],
    "popular_third": [0.12, 0.13, 0.50, 0.12, 0.13],
}


def group_for(buffet: int, origin: int) -> str:
    if buffet == 3:
        return "3_same" if origin == 3 else "3_other"
    return str(buffet)


def move_minutes(source: int, target: int, pace: float = 1.0) -> float:
    if not 1 <= source <= 5 or not 1 <= target <= 5:
        raise ValueError("Floors must be between 1 and 5")
    if pace <= 0:
        raise ValueError("Pace must be positive")
    return (max(0, source - target) * 1.5 + max(0, target - source) * 2.25) * pace


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


def evaluate(settings: Settings, observations: dict[str, list[float]]) -> Result:
    if settings.break_minutes <= 0 or settings.buy_minutes < 0 or settings.eat_minutes < 0:
        raise ValueError("Invalid durations")
    if settings.crowd_factor <= 0:
        raise ValueError("Crowd factor must be positive")
    group = group_for(settings.buffet, settings.origin)
    raw = observations[group]
    if not raw or any(not isfinite(v) or v < 0 for v in raw):
        raise ValueError("Waiting times must be nonempty finite nonnegative numbers")
    walk = move_minutes(settings.origin, settings.buffet, settings.pace_factor) + move_minutes(
        settings.buffet, settings.destination, settings.pace_factor
    )
    waits = tuple(v * settings.crowd_factor for v in raw)
    full_times = tuple(walk + wait + settings.buy_minutes + settings.eat_minutes for wait in waits)
    windows = tuple(settings.break_minutes - walk - wait - settings.buy_minutes for wait in waits)
    success = sum(t <= settings.break_minutes + 1e-9 for t in full_times)
    average_wait = sum(waits) / len(waits)
    avg_total = sum(full_times) / len(full_times)
    return Result(
        floor=settings.buffet,
        group=group,
        travel=walk,
        sample_count=len(raw),
        success_count=success,
        probability=success / len(raw),
        average_wait=average_wait,
        average_total=avg_total,
        average_eating_window=sum(windows) / len(windows),
        min_eating_window=min(windows),
        max_eating_window=max(windows),
        average_margin=settings.break_minutes - avg_total,
        observed_waits=waits,
        total_times=full_times,
    )


def all_buffets(settings: Settings, observations: dict[str, list[float]]) -> list[Result]:
    return [evaluate(Settings(**{**vars(settings), "buffet": f}), observations) for f in range(1, 6)]


def law_of_total_probability(results: list[Result], weights: list[float]) -> float:
    if len(results) != 5 or len(weights) != 5 or abs(sum(weights) - 1) > 1e-8:
        raise ValueError("Five buffet probabilities summing to 1 are required")
    return sum(r.probability * w for r, w in zip(results, weights))


def independence_check(results: list[Result], weights: list[float]):
    """Tests mathematical independence *inside* the stated choice-weight model."""
    p_a = law_of_total_probability(results, weights)
    p_b = weights[2]
    p_joint = results[2].probability * p_b
    p_product = p_a * p_b
    return p_a, p_b, p_joint, p_product


def best_buffet(settings: Settings, observations: dict[str, list[float]]) -> int:
    results = all_buffets(settings, observations)
    return sorted(results, key=lambda r: (-r.probability, r.average_total, r.floor))[0].floor


def parse_waits(raw: str) -> list[float]:
    parts = [p.strip() for p in raw.replace(";", ",").split(",")]
    if not parts or any(not p for p in parts):
        raise ValueError("Provide comma-separated values")
    try:
        values = [float(p) for p in parts]
    except ValueError as exc:
        raise ValueError("All waiting times must be numeric") from exc
    if any(not isfinite(v) or v < 0 or v > 120 for v in values):
        raise ValueError("Waiting times must be from 0 to 120 minutes")
    return values
