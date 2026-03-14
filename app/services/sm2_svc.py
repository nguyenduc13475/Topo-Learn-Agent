def calculate_sm2(
    quality_response: int, repetitions: int, previous_interval: int, previous_ef: float
):
    """
    Calculate SM-2 review parameters for a Concept.
    quality_response (q): 0 to 5 (0: Forget completely, 5: Remember perfectly)
    """
    if quality_response < 0 or quality_response > 5:
        raise ValueError("Quality response must be between 0 and 5.")

    # 1. Calculate the new Easiness Factor (EF)
    new_ef = previous_ef + (
        0.1 - (5 - quality_response) * (0.08 + (5 - quality_response) * 0.02)
    )

    # Press the EF to a minimum of 1.3 according to the formula
    if new_ef < 1.3:
        new_ef = 1.3

    # 2. Caculate Interval and Repetitions
    if quality_response < 3:
        # If score < 3 (forget), reset repetitions to 0
        new_repetitions = 0
        new_interval = 1
    else:
        # If rêmmber (score >= 3)
        new_repetitions = repetitions + 1

        if new_repetitions == 1:
            new_interval = 1
        elif new_repetitions == 2:
            new_interval = 6
        else:
            new_interval = round(previous_interval * new_ef)

    return {
        "repetitions": new_repetitions,
        "interval": new_interval,
        "ef": round(new_ef, 3),
    }
