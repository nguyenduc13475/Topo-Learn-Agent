import pytest
from app.services.sm2_svc import calculate_sm2


def test_calculate_sm2_perfect_recall():
    """Test SM-2 with a perfect score (5). User remembers everything."""
    result = calculate_sm2(
        quality_response=5, repetitions=0, previous_interval=1, previous_ef=2.5
    )

    assert result["repetitions"] == 1
    assert result["interval"] == 1
    assert result["ef"] == 2.6  # 2.5 + (0.1 - (5-5)*...)


def test_calculate_sm2_forget_completely():
    """Test SM-2 when the user forgets the concept entirely (score < 3)."""
    result = calculate_sm2(
        quality_response=2, repetitions=3, previous_interval=14, previous_ef=2.5
    )

    assert result["repetitions"] == 0
    assert result["interval"] == 1
    assert result["ef"] < 2.5


def test_calculate_sm2_min_ef_boundary():
    """Test that Easiness Factor (EF) never drops below the 1.3 threshold."""
    result = calculate_sm2(
        quality_response=0, repetitions=5, previous_interval=20, previous_ef=1.3
    )

    assert result["ef"] == 1.3
    assert result["repetitions"] == 0
    assert result["interval"] == 1


def test_calculate_sm2_invalid_quality():
    """Test SM-2 raises ValueError for out-of-bounds quality scores."""
    with pytest.raises(ValueError, match="Quality response must be between 0 and 5."):
        calculate_sm2(
            quality_response=6, repetitions=1, previous_interval=1, previous_ef=2.5
        )

    with pytest.raises(ValueError):
        calculate_sm2(
            quality_response=-1, repetitions=1, previous_interval=1, previous_ef=2.5
        )
