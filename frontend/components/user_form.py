import streamlit as st


def render_form() -> dict | None:
    """Render the user input form. Returns raw dict on submit, None otherwise."""
    with st.form("investment_form"):
        age = st.slider("Your Age", min_value=18, max_value=80, value=30)
        monthly_income = st.number_input(
            "Monthly Income (₹)", min_value=0.0, value=50000.0, step=1000.0
        )
        monthly_savings = st.number_input(
            "Monthly Savings (₹)", min_value=0.0, value=10000.0, step=500.0
        )
        risk = st.selectbox("Risk Preference", ["Low", "Medium", "High"])
        goal = st.selectbox(
            "Investment Goal",
            ["Short-term (< 3 years)", "Medium-term (3-7 years)", "Long-term (> 7 years)"],
        )
        submitted = st.form_submit_button("Get My Investment Plan")

    if submitted:
        risk_map = {"Low": "LOW", "Medium": "MEDIUM", "High": "HIGH"}
        goal_map = {
            "Short-term (< 3 years)": "SHORT",
            "Medium-term (3-7 years)": "MEDIUM",
            "Long-term (> 7 years)": "LONG",
        }
        return {
            "age": int(age),
            "monthly_income": float(monthly_income),
            "monthly_savings": float(monthly_savings),
            "risk": risk_map[risk],
            "goal": goal_map[goal],
        }
    return None
