# analytics.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datamod_sql import get_all_patients, get_sessions_for_patient
import json

def analytics_dashboard():
    st.title("📊 Physiotherapy Analytics Dashboard (Week 5)")

    patients = get_all_patients()
    if not patients:
        st.warning("No patient data found.")
        return

    df = pd.DataFrame(patients)

    # ------------------------------
    # SECTION 1 — OVERVIEW STATS
    # ------------------------------
    st.subheader("📌 Overview Statistics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Patients", len(df))
    col2.metric("Avg Pain Level", round(df["pain_level"].mean(), 2))
    col3.metric("Avg Age", round(df["age"].mean(), 1))
    col4.metric("Avg Follow-up Pain", round(df["followup_pain_level"].mean(), 2))

    st.markdown("---")

    # ------------------------------
    # SECTION 2 — PAIN LEVEL TREND
    # ------------------------------
    st.subheader("📈 Pain Level Distribution")

    fig = px.histogram(df, x="pain_level", nbins=10,
                       title="Pain Levels Across All Patients",
                       color_discrete_sequence=["#66b3ff"])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ------------------------------
    # SECTION 3 — SWELLING PATTERN
    # ------------------------------
    st.subheader("🧊 Swelling Frequency")

    swelling_counts = df["swelling"].value_counts()
    fig2 = px.pie(
        names=swelling_counts.index,
        values=swelling_counts.values,
        title="Swelling Presence",
        color=swelling_counts.index
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ------------------------------
    # SECTION 4 — STRENGTH IMPROVEMENTS
    # ------------------------------
    st.subheader("💪 Strength Change Summary")

    strength_data = []
    for p in patients:
        try:
            entries = json.loads(p["strength_entries"]) if p["strength_entries"] else []
            for e in entries:
                strength_data.append({
                    "patient": p["name"],
                    "muscle": e.get("muscle_group"),
                    "grade": e.get("grade")
                })
        except:
            pass

    if strength_data:
        df_strength = pd.DataFrame(strength_data)
        fig3 = px.box(df_strength, x="muscle", y="grade",
                      title="Strength Grades Across Patients")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No strength entries available.")

    st.markdown("---")

    # ------------------------------
    # SECTION 5 — ROM PROGRESS
    # ------------------------------
    st.subheader("🦵 Range of Motion — Global Trends")

    rom_data = []
    for p in patients:
        try:
            roms = json.loads(p["rom_entries"]) if p["rom_entries"] else []
            for e in roms:
                rom_data.append({
                    "patient": p["name"],
                    "joint": e.get("joint"),
                    "active": e.get("active", None),
                    "passive": e.get("passive", None)
                })
        except:
            pass

    if rom_data:
        df_rom = pd.DataFrame(rom_data)

        fig4 = px.line(df_rom, x="joint", y="active",
                       title="Active ROM Comparison by Joint",
                       markers=True)
        st.plotly_chart(fig4, use_container_width=True)

        fig5 = px.bar(df_rom, x="joint", y="passive",
                      title="Passive ROM Comparison Across Joints")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("No ROM entries available.")

    st.markdown("---")

    # ------------------------------
    # SECTION 6 — INDIVIDUAL PATIENT ANALYTICS
    # ------------------------------
    st.subheader("Patient-Level Analytics")

    patient_list = {p["id"]: p["name"] for p in patients}
    selected_pid = st.selectbox("Select Patient", list(patient_list.keys()),
                                format_func=lambda x: patient_list[x])

    p = [item for item in patients if item["id"] == selected_pid][0]

    # Pain
    st.markdown("### Pain Change")
    st.write(f"**Initial Pain:** {p['pain_level']} → **Follow-up:** {p['followup_pain_level']}")

    # Session trends (voice-notes)
    sessions = get_sessions_for_patient(selected_pid)

    if sessions:
        sess_df = pd.DataFrame(sessions)
        sess_df["created_at"] = pd.to_datetime(sess_df["created_at"])
        fig6 = px.line(sess_df, x="created_at", y="pain_level",
                       title="Session-by-Session Pain Trend",
                       markers=True)
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No voice-note sessions recorded.")

    st.success("✔ Week-5 visualisation module loaded successfully!")
