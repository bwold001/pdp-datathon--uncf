"""Matplotlib look from Kevin Systrom's COVID-19 notebook.

Same settings as k-sys/covid-19 matplotlibrc (gray type, bold labels,
open spines, frameless legend, retina inline figures). The color cycle
is left at matplotlib's default.
"""

import matplotlib as mpl

_STYLE = {
    "font.weight": "bold",
    "font.size": 13.0,
    "font.family": "sans-serif",
    "font.sans-serif": [
        "Helvetica Neue",
        "Lucida Grande",
        "Verdana",
        "Geneva",
        "Lucid",
        "Arial",
        "Avant Garde",
        "sans-serif",
    ],
    "text.color": "#555555",
    "axes.edgecolor": "#555555",
    "axes.linewidth": 1,
    "axes.titlesize": 14,
    "axes.titleweight": "normal",
    "axes.titlepad": 10.0,
    "axes.labelcolor": "#555555",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "grid.color": "#eeeeee",
    "legend.frameon": False,
    "figure.titlesize": 16,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "figure.subplot.top": 0.91,
}


def _retina() -> None:
    try:
        from IPython import get_ipython
    except ImportError:
        return
    ip = get_ipython()
    if ip is not None:
        ip.run_line_magic("config", "InlineBackend.figure_format = 'retina'")


def use() -> None:
    """Apply the style. Called on import."""
    mpl.rcParams.update(_STYLE)
    _retina()


use()
