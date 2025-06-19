import numpy as np
import pandas as pd
from models import MonthlyBreakdown


def calculate_forecast(
    monthly_breakdown: list[MonthlyBreakdown],
    method: str = "average",
    decay_rate: float = 0.01,
) -> int:
    """
    Calculate a steel production forecast for the next month based on
    production history using one of two methods: a standard average
    or a weighted average where more recent observations carry more weight.
    If using a weighted average, you can specify a decay rate.
    """
    supported_methods = ["average", "weighted_average"]
    if method not in supported_methods:
        msg = (
            f"Unsupported method '{method}'. Supported methods are: {supported_methods}"
        )
        raise ValueError(msg)

    rows = []
    for production in monthly_breakdown:
        rows.append({"month": production.month, "tons": production.tons})
    production_history = pd.DataFrame(rows)
    production_history.set_index("month", inplace=True)
    production_history.index = pd.to_datetime(production_history.index)
    production_history.sort_index(inplace=True)
    if method == "average":
        forecast = np.average(production_history).round()
    elif method == "weighted_average":
        decay_rate = decay_rate
        time_deltas = (production_history.index[-1] - production_history.index).days
        weights = np.exp(-decay_rate * time_deltas)
        forecast = np.average(production_history, weights=weights, axis=0).round()

    return int(forecast)
