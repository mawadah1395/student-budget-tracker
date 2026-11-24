"""
chart.py  --  draws the pie chart.

No chart library needed. We build the SVG by hand, using the exact pie-chart
formula from your STA 1110 notes:

        angle of a slice = (amount of category / total) x 360 degrees

Then a bit of trigonometry turns each angle into a point on a circle.
"""

import math

# One colour per slice. If there are more slices than colours we wrap around
# using the modulo operator (%), so we can never run off the end of the list.
PALETTE = [
    "#2f7d45", "#14467a", "#c8762a", "#8e3b7d",
    "#b03a3a", "#1c7f8c", "#6b6f2a", "#7a4a2b",
]


def point_on_circle(cx, cy, radius, angle_degrees):
    """Where is a point on the edge of a circle, at this angle?

    We subtract 90 degrees so that 0 degrees points straight UP, which is
    where people expect a pie chart to start. SVG's y-axis grows downward,
    hence the + for y.
    """
    radians = math.radians(angle_degrees - 90)
    x = cx + radius * math.cos(radians)
    y = cy + radius * math.sin(radians)
    return x, y


def pie_chart_svg(totals, size=240):
    """Turn {category: amount} into an SVG pie chart as a string of HTML."""
    grand_total = sum(totals.values())

    # Nothing spent yet -- draw a friendly empty circle instead of crashing.
    if grand_total <= 0:
        return (
            f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{size/2}" cy="{size/2}" r="{size/2 - 10}" '
            f'fill="#eef1f4" stroke="#ccd3da" stroke-width="2"/>'
            f'<text x="{size/2}" y="{size/2 + 5}" text-anchor="middle" '
            f'font-family="Arial" font-size="13" fill="#8a8f96">No data yet</text>'
            f"</svg>"
        )

    cx = cy = size / 2
    radius = size / 2 - 10

    slices = []
    start_angle = 0.0

    for i, (category, amount) in enumerate(totals.items()):
        # THE FORMULA FROM YOUR STATS COURSE:
        angle = amount / grand_total * 360
        end_angle = start_angle + angle

        colour = PALETTE[i % len(PALETTE)]

        if angle >= 359.99:
            # One single category -- an arc cannot draw a full circle,
            # so just draw an actual circle.
            slices.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{colour}"/>'
            )
        else:
            x1, y1 = point_on_circle(cx, cy, radius, start_angle)
            x2, y2 = point_on_circle(cx, cy, radius, end_angle)

            # SVG needs to know whether to take the short way round or the
            # long way round. Anything over 180 degrees is "the long way".
            large_arc = 1 if angle > 180 else 0

            # M = move to centre, L = line to edge, A = arc along the edge,
            # Z = close the shape back to the centre.
            path = (
                f"M {cx} {cy} "
                f"L {x1:.2f} {y1:.2f} "
                f"A {radius} {radius} 0 {large_arc} 1 {x2:.2f} {y2:.2f} "
                f"Z"
            )
            slices.append(
                f'<path d="{path}" fill="{colour}" stroke="#fff" stroke-width="2"/>'
            )

        start_angle = end_angle

    body = "".join(slices)
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">{body}</svg>'


def legend_colour(index):
    """Let the web page ask for the same colour the chart used."""
    return PALETTE[index % len(PALETTE)]
