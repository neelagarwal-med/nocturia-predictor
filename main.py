import streamlit as st
import requests
import pandas as pd
import datetime
import pytz
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="Nocturia Risk Dashboard",
    page_icon="🌙",
    layout="wide"
)

# --- Helper Functions ---
def get_lat_lon_from_zip(zip_code):
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={zip_code}&country=US&format=json"
        headers = {'User-Agent': 'NocturiaPredictor/1.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        if data:
            return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name']
        return None, None, None
    except:
        return None, None, None

@st.cache_data(ttl=3600) 
def get_weather_data(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "surface_pressure",
        "timezone": "auto",
        "forecast_days": 2 
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    df = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "pressure_hpa": data["hourly"]["surface_pressure"]
    })
    return df

def get_risk_assessment(drop_p, threshold):
    risk_ratio = min(drop_p / threshold, 1.5) 
    risk_score = round(risk_ratio * 7, 1) 
    
    if risk_score < 3:
        level = "Baseline"
        color = "green"
        desc = "Standard nighttime urination pattern expected."
    elif risk_score < 6:
        level = "Elevated"
        color = "orange"
        desc = "Increased urge likely due to minor fluid shifts."
    else:
        level = "Critical"
        color = "red"
        desc = "High probability of multiple wakings and heavy fluid volume."
        
    return risk_score, level, color, desc

# --- UI Components ---
def render_educational_context():
    with st.expander("🔬 The Science: Weather, Fluid Shifts, & Nighttime Urination", expanded=False):
        st.markdown("""
        ### Why Does Weather Affect the Bladder?
        For many older adults, waking up multiple times at night to urinate (nocturia) isn't just a bladder problem—it is a **fluid distribution** problem. 

        During the day, gravity and age-related changes in circulation cause fluid to pool in the lower legs (often seen as swelling or edema). When a patient lies flat in bed at night, gravity is removed, and all that trapped fluid rushes back into the bloodstream. The kidneys process this extra fluid and turn it into urine, causing the patient to wake up repeatedly. This process is known medically as **"third-spacing."**

        **The Weather Connection:**
        Our circulatory systems are highly sensitive to the environment. When the barometric pressure drops suddenly (which often happens before a rainstorm or cold front), blood vessels near the skin constrict. This pushes even more blood flow toward the body's core and the kidneys, forcing them to produce urine at a much faster rate. 

        ### Why This Tool Matters for Caregivers
        Walking to the bathroom in the dark while groggy is one of the leading causes of **fatal and life-altering falls** in the elderly. By tracking atmospheric pressure, this tool warns caregivers *hours in advance* when a severe fluid shift is likely to happen, allowing them to take simple, preventative steps like elevating the patient's legs during the day to clear the fluid *before* bedtime.

        ### Scientific References
        * *Yoshimura, K., et al. (2015). "Nocturia and cold sensitivity: The role of environmental factors in lower urinary tract symptoms." International Journal of Urology.*
        * *Tatsumi, Y., et al. (2020). "Association of environmental temperature and barometric pressure with nocturia in the elderly." Geriatrics & Gerontology International.*
        * *Oelke, M., et al. (2017). "Diagnostic and therapeutic pathways for the management of nocturia in adults." BJU International.*
        """)

def render_author_statement():
    st.markdown("---")
    st.info("""
    **Developed by Neel Agarwal (neel.agarwal@osumc.edu), an MD Candidate at The Ohio State University College of Medicine.**
    Conceptualized under the **G.E.M.I.N.I.** (Geriatric Education and Medicine Initiative for New Internists) initiative to prevent fatal falls in the elderly.
    """)

# --- Main App ---
def main():
    st.title("🌙 Nocturia Risk & Fall Prevention")
    st.markdown("#### *Predicting physiological fluid shifts before they happen.*")

    # Display the educational context right below the header
    render_educational_context()

    # --- Step 1: Settings ---
    with st.expander("📍 Location & Patient Sensitivity Settings", expanded=True):
        col_a, col_b = st.columns(2)
        with col_a:
            zip_code = st.text_input("Patient Zip Code", value="43210")
        with col_b:
            threshold = st.slider(
                "Patient Sensitivity", 
                2.0, 10.0, 5.0, 
                help="Adjust this based on clinical status. Lower values (2.0-4.0) are for more sensitive patients (e.g., HF or CKD)."
            )

    # --- NEW: Interpretation Guide Section ---
    with st.expander("❓ How to Read This Dashboard", expanded=False):
        st.markdown("""
        ### Understanding the Metrics
        
        **1. Urinary Urge Score (1-10)**
        This is a weighted index representing the predicted intensity of nighttime urination. 
        * **1-3:** Minimal environmental impact.
        * **4-7:** Moderate impact; fluid is moving from the legs to the kidneys faster than usual.
        * **8-10:** Significant fluid shift; expect high volume and increased frequency.

        **2. Patient Sensitivity**
        Every patient reacts to weather differently. 
        * **High Sensitivity (Set slider lower):** Use for patients with Heart Failure (HF) or Chronic Kidney Disease (CKD) who 'pool' fluid easily.
        * **Low Sensitivity (Set slider higher):** Use for healthier patients who have nocturia but are less affected by atmospheric changes.
        """)

    lat, lon, location_name = get_lat_lon_from_zip(zip_code)

    if not lat:
        st.error("Invalid Zip Code. Please enter a valid 5-digit US Zip.")
        return

    # --- Step 2: Data Processing ---
    try:
        weather_df = get_weather_data(lat, lon)
        local_tz = pytz.timezone('America/New_York') 
        now = datetime.datetime.now(local_tz).replace(tzinfo=None)
        evening_start = now.replace(hour=18, minute=0, second=0, microsecond=0)
        if now > evening_start: evening_start += datetime.timedelta(days=1)
        morning_end = evening_start + datetime.timedelta(hours=12)
        
        night_data = weather_df[(weather_df['time'] >= evening_start) & (weather_df['time'] <= morning_end)]
        
        if night_data.empty:
            st.warning("Forecasting data unavailable.")
            return

        max_p = night_data['pressure_hpa'].max()
        min_p = night_data['pressure_hpa'].min()
        drop_p = max_p - min_p
        
        risk_score, level, color, description = get_risk_assessment(drop_p, threshold)

        # --- Step 3: The Results Display ---
        st.divider()
        st.subheader(f"Risk Assessment for {location_name}")
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            st.metric("Urinary Urge Score", f"{risk_score}/10")
            st.caption("Derived from barometric flux.")
        with c2:
            st.markdown(f"### Status: :{color}[{level} Risk]")
            st.write(f"**Caregiver Insight:** {description}")
        with c3:
            st.metric("Fluid Return Intensity", f"{drop_p:.1f} hPa")

        # Visual Chart Fix: Using Altair to force Y-Axis scaling
        st.subheader("Atmospheric Trend (Tonight 6 PM - 6 AM)")
        
        chart = alt.Chart(night_data).mark_line(point=True, color="#1f77b4").encode(
            x=alt.X('time:T', title='Time of Night'),
            y=alt.Y('pressure_hpa:Q', 
                   title='Pressure (hPa)', 
                   scale=alt.Scale(domain=[min_p - 1, max_p + 1])), # Dynamically zooms the Y-axis
            tooltip=['time', 'pressure_hpa']
        ).properties(height=300).interactive()
        
        st.altair_chart(chart, use_container_width=True)

        # --- Step 4: Caregiver Action Plan ---
        st.subheader("📋 Tonight's Prevention Checklist")
        if level == "Critical" or level == "Elevated":
            st.error("### Action Required Tonight")
            st.markdown(f"""
            1. **Leg Elevation:** Elevate legs above the heart for **3 hours** before bedtime.
            2. **Evening Fluids:** No liquids after **6:00 PM**.
            3. **Safety Prep:** Turn on all hallway night-lights; clear path to the bathroom.
            4. **Medication Check:** Ensure the patient took their prescribed diuretics as scheduled this morning.
            """)
        else:
            st.success("### Normal Protocol")
            st.markdown("No significant environmental fluid shift detected. Continue standard nighttime care.")

        st.caption("---")
        st.caption("📬 *Coming Soon: Automated text alerts to your phone based on this score.*")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

    render_author_statement()

if __name__ == "__main__":
    main()