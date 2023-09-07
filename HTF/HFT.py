def calculate_intervals(x, y, unit):
    if unit == "minutes":
        intervals = int(y / x)
    elif unit == "hours":
        intervals = int((y * 60) / x)
    elif unit == "weeks":
        intervals = int((y * 60 * 24 * 7) / x)
    elif unit == "months":
        intervals = int((y * 60 * 24 * 30) / x)  # Approximate number of days in a month
    else:
        raise ValueError("Invalid unit. Choose 'minutes', 'hours', 'weeks', or 'months'.")

    return intervals

# Example usage
x_intervals = 20
y_units = 12
unit = "hours"
intervals = calculate_intervals(x_intervals, y_units, unit)

print(f"There are {intervals} intervals of {x_intervals} minutes in {y_units} {unit}.")
