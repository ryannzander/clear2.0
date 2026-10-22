# DST edge dates are the ones the standard names: docs/standards/naming-units-time.md
# (2025-03-09 spring forward, 2025-11-02 fall back, America/Toronto).
import pandas as pd
import pytest

from clear.timeutil import lst_zone, to_utc

TORONTO = "America/Toronto"


def naive(*stamps: str) -> pd.Series:
    return pd.Series(pd.to_datetime(list(stamps)))


def utc(*stamps: str) -> list[pd.Timestamp]:
    return [pd.Timestamp(s, tz="UTC") for s in stamps]


def test_lst_zone_inverts_sign_like_iana():
    assert lst_zone(-5) == "Etc/GMT+5"
    assert lst_zone(3) == "Etc/GMT-3"
    assert lst_zone(0) == "Etc/UTC"


def test_local_standard_time_ignores_dst():
    # Summer noon in EST (UTC-5 all year) is 17:00 UTC, not 16:00.
    out = to_utc(naive("2025-07-01 12:00"), source_tz=lst_zone(-5))
    assert list(out) == utc("2025-07-01 17:00")


def test_clock_time_follows_dst():
    out = to_utc(naive("2025-07-01 12:00", "2025-01-15 12:00"), source_tz=TORONTO)
    assert list(out) == utc("2025-07-01 16:00", "2025-01-15 17:00")


def test_spring_forward_gap_raises_by_default_and_can_become_nat():
    gap = naive("2025-03-09 02:30")  # does not exist in Toronto
    with pytest.raises(ValueError, match="nonexistent"):
        to_utc(gap, source_tz=TORONTO)
    assert to_utc(gap, source_tz=TORONTO, nonexistent="NaT").isna().all()


def test_fall_back_repeat_raises_by_default_and_infers_when_sorted():
    hours = naive("2025-11-02 00:00", "2025-11-02 01:00", "2025-11-02 01:00", "2025-11-02 02:00")
    with pytest.raises(ValueError, match="ambiguous"):
        to_utc(hours, source_tz=TORONTO)
    out = to_utc(hours, source_tz=TORONTO, ambiguous="infer")
    assert list(out) == utc(
        "2025-11-02 04:00", "2025-11-02 05:00", "2025-11-02 06:00", "2025-11-02 07:00"
    )


def test_hour_ending_labels_shift_to_hour_beginning():
    # Hour-ending 01:00 LST covers 00:00-01:00 LST = 05:00-06:00 UTC; label is the start.
    out = to_utc(naive("2025-01-01 01:00"), source_tz=lst_zone(-5), hour_ending=True)
    assert list(out) == utc("2025-01-01 05:00")


def test_hour_ending_across_spring_forward_has_no_gap():
    # Clock jumps 02:00 EST -> 03:00 EDT. The hour 01:00-02:00 EST ends at 03:00 EDT, so
    # hour-ending clock labels run 01:00, 03:00, 04:00 and the UTC hours stay contiguous.
    out = to_utc(
        naive("2025-03-09 01:00", "2025-03-09 03:00", "2025-03-09 04:00"),
        source_tz=TORONTO,
        hour_ending=True,
    )
    assert list(out) == utc("2025-03-09 05:00", "2025-03-09 06:00", "2025-03-09 07:00")


def test_hour_ending_label_inside_the_spring_gap_is_not_shifted_silently():
    # An hour-ending "02:00" on the spring-forward day is not a real clock time.
    with pytest.raises(ValueError, match="nonexistent"):
        to_utc(naive("2025-03-09 02:00"), source_tz=TORONTO, hour_ending=True)


def test_hour_ending_across_fall_back_needs_the_repeat_resolved():
    # Clock falls back 02:00 EDT -> 01:00 EST: hour-ending label 01:00 appears twice
    # (end of 00:00-01:00 EDT, then end of 01:00-02:00 EDT).
    labels = naive("2025-11-02 01:00", "2025-11-02 01:00", "2025-11-02 02:00", "2025-11-02 03:00")
    with pytest.raises(ValueError, match="ambiguous"):
        to_utc(labels, source_tz=TORONTO, hour_ending=True)
    out = to_utc(labels, source_tz=TORONTO, hour_ending=True, ambiguous="infer")
    assert list(out) == utc(
        "2025-11-02 04:00", "2025-11-02 05:00", "2025-11-02 06:00", "2025-11-02 07:00"
    )


def test_rejects_aware_and_non_datetime_input():
    aware = pd.Series(pd.to_datetime(["2025-01-01 00:00"]).tz_localize("UTC"))
    with pytest.raises(ValueError, match="tz-aware"):
        to_utc(aware, source_tz=TORONTO)
    with pytest.raises(TypeError, match="datetime64"):
        # Deliberately the wrong dtype: the runtime check is what is under test.
        to_utc(pd.Series(["2025-01-01"]), source_tz=TORONTO)  # pyright: ignore[reportArgumentType]
