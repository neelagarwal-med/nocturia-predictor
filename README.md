# 🌙 Barometric Nocturia Predictor

A clinical decision-support dashboard designed to predict environmental triggers for **nocturia** and associated **fall risks** in geriatric populations. This tool bridges the gap between meteorological data and urological pathophysiology.

## 🩺 The Problem
Nocturia—waking up multiple times at night to urinate—is a leading cause of fatal falls in the elderly. In patients with minor heart failure or chronic kidney disease, this is often caused by **"third-spacing"**: fluid pooling in the legs during the day and returning to the kidneys at night when supine. Research suggests this fluid shift is highly sensitive to drops in barometric pressure, which can exacerbate urinary urgency.

## 🚀 Key Features
* **Zip Code Geocoding:** Automatically converts US Zip Codes to high-resolution coordinates.
* **Urinary Urge Score (1-10):** A translated risk index that helps caregivers understand predicted physiological intensity at a glance.
* **Automated Action Plan:** Generates dynamic, non-pharmacological intervention checklists (e.g., leg elevation, fluid restriction) based on risk levels.
* **Precision Analytics:** Uses Altair-powered time-series charting to visualize overnight barometric flux.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Frontend:** Streamlit
* **Data APIs:** Open-Meteo (Atmospheric Pressure), Nominatim (Geocoding)
* **Libraries:** Pandas, Altair, Pytz

## 📦 Installation & Usage
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/neelagarwal-med/barometric-nocturia-predictor.git](https://github.com/your-username/barometric-nocturia-predictor.git)
   cd barometric-nocturia-predictor
