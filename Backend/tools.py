def calculate_import_duty(total_base_cost: float) -> float:
    """
    Calculates a 5% import duty based on the pre-verified base cost.
    This should only be called after the Auditor has approved the base cost.
    """
    return total_base_cost * 1.05