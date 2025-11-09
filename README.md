# chennai-crime-route-alert-system
🚨 A smart Streamlit-based web app that maps Chennai crime data, predicts hotspots using clustering, and finds the safest driving routes between locations using OpenRouteService API. Includes real-time alternate route suggestions and dynamic crime reporting.


An intelligent web application that visualizes crime hotspots across Chennai, predicts danger zones using clustering, and helps users find the **safest travel routes**.  
Built with Streamlit, Folium, OpenRouteService API, and Machine Learning (K-Means), it dynamically updates routes and identifies alternate safe paths.

🧭 Overview

This project aims to improve **public safety and navigation** by integrating real-time geospatial crime data and route analysis.  
Users can:
- View Chennai’s crime map 🗺️  
- Report new crimes 📢  
- Analyze clusters of criminal activities 📊  
- Find safe driving routes between two areas 🚗  
- Get automatic **alternate routes** when the primary path crosses a danger zone ⚠️

---

🏗️ Features

🔴 Crime Data Visualization
- Displays crime incidents on an interactive map (Folium)
- Plots clusters of high-risk zones using **K-Means** algorithm
- Supports live updates — newly reported crimes appear instantly

📢 Crime Reporting
- Users can log new crimes with date, time, type, and coordinates
- Automatically saves data to `crime.csv`
- Updates map and hotspot clusters immediately

🧭 Safe Route Finder
- Uses **OpenRouteService (ORS)** API to fetch accurate road routes
- Detects crimes near route paths (~2km threshold)
- If danger detected, computes **alternate safe route** in green
- Displays both main (blue) and alternate (green) routes with markers

 Location Intelligence
- Integrated with **GeoPy + Nominatim** for area-to-coordinate conversion
- Predefined fallback for popular Chennai localities (Guindy, Tambaram, Avadi, etc.)
- Works even if some locations fail to geocode

💾 Data Handling
- All reported data stored in a local `crime.csv` file
- Auto-refresh and persistent state with Streamlit session

---

🧠 Technologies Used

| Category | Technologies |
|-----------|---------------|
| **Frontend** | Streamlit |
| **Mapping** | Folium, Leaflet.js |
| **Backend / Logic** | Python, Pandas, GeoPandas, NumPy |
| **APIs** | OpenRouteService API, GeoPy (Nominatim) |
| **Machine Learning** | Scikit-learn (K-Means clustering) |
| **Visualization** | Folium + Streamlit-Folium |
| **Data Storage** | Local CSV (`crime.csv`) |

---

🗂️ Project Structure

📦 chennai-crime-route-alert-system
├── main.py # Streamlit app file
├── crime.csv # Crime dataset (auto-updated)
├── requirements.txt # Python dependencies
├── README.md # Documentation



⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/<your-username>/chennai-crime-route-alert-system.git
cd chennai-crime-route-alert-system
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Run the Streamlit App
streamlit run main.py
4️⃣ Access the App
Open your browser at:
http://localhost:8501

🔑 API Key Setup (ORS)
Create a free account at https://openrouteservice.org.

Generate an API key.

Replace it in your main.py:
ORS_API_KEY = "your_openrouteservice_api_key"
