import matplotlib.pyplot as plt
import streamlit as st


_COLOURS = {
    "fixed_deposit": "#4C72B0",
    "recurring_deposit": "#55A868",
    "bonds": "#C44E52",
    "mutual_funds": "#8172B2",
    "equity": "#CCB974",
}

_LABELS = {
    "fixed_deposit": "Fixed Deposit",
    "recurring_deposit": "Recurring Deposit",
    "bonds": "Bonds",
    "mutual_funds": "Mutual Funds",
    "equity": "Equity",
}


def render_pie_chart(allocation: dict) -> None:
    """Render allocation as a pie chart, hiding zero-value categories."""
    filtered = {k: v for k, v in allocation.items() if v > 0}
    if not filtered:
        st.warning("No allocation data to display.")
        return

    labels = [_LABELS.get(k, k) for k in filtered]
    sizes = list(filtered.values())
    colours = [_COLOURS.get(k, "#999999") for k in filtered]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        sizes,
        labels=labels,
        colors=colours,
        autopct="%1.0f%%",
        startangle=140,
        pctdistance=0.82,
    )
    ax.set_title("Your Recommended Investment Allocation", fontsize=14, pad=16)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
