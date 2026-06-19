import streamlit as st

_LABELS = {
    "fixed_deposit": "Fixed Deposit",
    "recurring_deposit": "Recurring Deposit",
    "bonds": "Bonds",
    "mutual_funds": "Mutual Funds",
    "equity": "Equity",
}


def render_recommendation(explanation: str, disclaimer: str, allocation: dict | None = None) -> None:
    """Display explanation, allocation metrics, and disclaimer."""
    st.subheader("Why This Mix?")
    st.info(explanation)

    if allocation:
        st.subheader("Your Allocation")
        cols = st.columns(len([v for v in allocation.values() if v > 0]))
        col_idx = 0
        for key, pct in allocation.items():
            if pct > 0:
                cols[col_idx].metric(label=_LABELS.get(key, key), value=f"{pct}%")
                col_idx += 1

    st.warning(disclaimer)
