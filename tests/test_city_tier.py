"""Tests for the static city tier lists in `city/city_tier.py`."""

from __future__ import annotations

from city.city_tier import tier_1_cities, tier_2_cities


def test_tier_1_is_non_empty():
    assert len(tier_1_cities) >= 1


def test_tier_2_is_non_empty():
    assert len(tier_2_cities) >= 1


def test_no_overlap_between_tiers():
    assert set(tier_1_cities).isdisjoint(set(tier_2_cities))


def test_all_entries_are_strings():
    for c in tier_1_cities + tier_2_cities:
        assert isinstance(c, str)
        assert c  # no empty strings


def test_tier_1_contains_known_metro_cities():
    # Spot-check that the well-known metros are in tier 1. Locks down
    # against silent edits to the list.
    expected = {"Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"}
    assert expected.issubset(set(tier_1_cities))


def test_tier_2_contains_known_cities():
    # Spot-check
    assert "Jaipur" in tier_2_cities
    assert "Chandigarh" in tier_2_cities
    assert "Noida" in tier_2_cities