import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from trl_engine import (load_trl_data, compute_maturity_score,
    compute_gap_matrix, identify_gaps, compute_tech_landscape)

st.set_page_config(page_title="RLV Maintenance TRL Dashboard",
                   page_icon="\U0001f680", layout="wide")

df, trl_scale, techs = load_trl_data()

st.title("\U0001f680 Maintenance Technology Readiness Dashboard")
st.markdown("**TRL assessment of maintenance technologies for "
            "Reusable Launch Vehicles**")
st.divider()

# Sidebar
st.sidebar.header("Settings")
threshold = st.sidebar.slider("Gap threshold (TRL <)", 2, 8, 5)
gaps = identify_gaps(df, threshold)

# KPIs
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Assessments", len(df))
with c2: st.metric("Avg TRL", f"{df['trl'].mean():.1f}")
with c3: st.metric(f"Gaps (TRL<{threshold})", len(gaps))
with c4: st.metric("Critical (TRL\u22643)", len(gaps[gaps["trl"] <= 3]))

st.divider()
tab1, tab2, tab3, tab4 = st.tabs([
    "Heatmap", "Vehicle Maturity", "Technology Landscape", "Gap Analysis"])

with tab1:
    st.subheader("TRL Heatmap")
    matrix = compute_gap_matrix(df)
    fig = px.imshow(matrix, text_auto=True, aspect="auto",
        color_continuous_scale=["#E74C3C","#F39C12","#F1C40F","#2ECC71","#27AE60"],
        range_color=[1, 9], labels=dict(color="TRL"))
    fig.update_layout(height=400, xaxis_title="Technology",
                      yaxis_title="Vehicle")
    # ✅ Replaced use_container_width=True with width='stretch'
    st.plotly_chart(fig, width='stretch')

with tab2:
    st.subheader("Vehicle Maturity Scores")
    scores = compute_maturity_score(df)
    fig2 = px.bar(x=scores.values, y=scores.index, orientation="h",
        color=scores.values, color_continuous_scale="RdYlGn",
        range_color=[0, 100], labels={"x": "Maturity (%)", "y": ""})
    fig2.update_layout(height=350)
    # ✅ Replaced use_container_width=True with width='stretch'
    st.plotly_chart(fig2, width='stretch')

    st.subheader("Radar Comparison")
    sel = st.multiselect("Select vehicles", sorted(df["vehicle"].unique()),
                         default=sorted(df["vehicle"].unique())[:3])
    if sel:
        fig3 = go.Figure()
        for v in sel:
            vdata = df[df["vehicle"] == v].sort_values("technology")
            fig3.add_trace(go.Scatterpolar(
                r=vdata["trl"].tolist() + [vdata["trl"].iloc[0]],
                theta=vdata["technology"].tolist() + [vdata["technology"].iloc[0]],
                fill="toself", name=v, opacity=0.5))
        fig3.update_layout(polar=dict(radialaxis=dict(range=[0, 9])), height=500)
        # ✅ Replaced use_container_width=True with width='stretch'
        st.plotly_chart(fig3, width='stretch')

with tab3:
    st.subheader("Technology Landscape")
    landscape = compute_tech_landscape(df)
    for tech in landscape.index:
        with st.expander(f"{tech} (Avg TRL: {landscape.loc[tech, 'mean']})"):
            tech_data = df[df["technology"] == tech].sort_values("trl", ascending=False)
            fig_t = px.bar(tech_data, x="vehicle", y="trl", color="trl",
                color_continuous_scale="RdYlGn", range_color=[1, 9])
            fig_t.update_layout(height=300, yaxis_range=[0, 9])
            # ✅ Replaced use_container_width=True with width='stretch'
            st.plotly_chart(fig_t, width='stretch')

with tab4:
    st.subheader(f"Gap Analysis (TRL < {threshold})")
    if len(gaps) > 0:
        display = gaps[["vehicle","technology","trl","severity",
                       "category","justification","source"]].rename(columns={
            "vehicle":"Vehicle","technology":"Technology","trl":"TRL",
            "severity":"Severity","category":"Category",
            "justification":"Justification","source":"Source"})
        # ✅ Replaced use_container_width=True with width='stretch'
        st.dataframe(display, width='stretch', height=400)
        csv = display.to_csv(index=False)
        st.download_button("Export gaps as CSV", csv, "trl_gaps.csv")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Gaps by Vehicle**")
            st.bar_chart(gaps["vehicle"].value_counts())
        with col2:
            st.markdown("**Gaps by Category**")
            st.bar_chart(gaps["category"].value_counts())
    else:
        st.success("No gaps found at this threshold!")

st.divider()
st.caption("RLV Maintenance TRL Dashboard | Oscar Vincent Dbritto")