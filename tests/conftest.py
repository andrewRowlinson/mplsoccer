""" Pytest configuration for the mplsoccer tests.

Force the non-interactive Agg backend so the tests run headless and are not
affected by backend behavior, e.g. the macosx backend rounds the figure size
to whole pixels, which breaks exact figure-size comparisons.
"""

import matplotlib

matplotlib.use('Agg')
