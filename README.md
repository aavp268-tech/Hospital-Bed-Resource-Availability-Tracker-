# 🏥 CareMap – Hospital Beds & Resources Tracker

**Find nearby hospitals. Check resource availability. Make informed healthcare decisions.**

CareMap is a web-based hospital resource tracking application that helps patients find nearby hospitals with available general beds, ICU beds, ventilators, and oxygen facilities. It also enables hospital administrators to update resource availability and display average treatment costs per day.

Developed as a **Mini Project (Phase 1 & 2)** by the Department of Data Science, Usha Mittal Institute of Technology, SNDT Women's University.

---
## 🌐 Live Demo

🚀 **Explore CareMap:** [Visit Website](YOUR_DEPLOYED_WEBSITE_URL)

Try the application and explore hospital search, resource availability, interactive maps, and the hospital admin portal.
## 📌 Project Information

| Detail | Description |
|---|---|
| Project Name | CareMap – Hospital Beds & Resources Tracker |
| Domain | Healthcare Technology / Data Science |
| Institution | Usha Mittal Institute of Technology |
| University | SNDT Women's University |
| Project Guide | Prof. Mohan Bonde |
| Team Members | Anuja Pisal, Apurva More, Mrunmayi Surve |
| Project Type | Mini Project – Phase 1 & 2 |

---

## 🚨 Problem Statement

During medical emergencies, finding a hospital with available beds, ICU facilities, ventilators, and oxygen support can be challenging.

Hospital availability information is often scattered across different sources, manually maintained, and quickly outdated. This creates difficulties for patients and their families, resulting in wasted travel time and potential delays in medical admission.

Additionally, patients often lack information about the approximate treatment costs before visiting a hospital.

**CareMap addresses these challenges by providing a centralized platform for hospital resource discovery and availability management.**

---

## ✨ Key Features

### 👨‍⚕️ Patient Portal

- **Hospital Search:** Search hospitals across 32 predefined areas of Mumbai.
- **Resource Filtering:** Search for:
  - General Beds
  - ICU Beds
  - Ventilators
  - Any Available Resource
- **Radius-Based Search:** Find hospitals within a selected radius of up to 50 km.
- **Distance-Based Sorting:** Automatically displays the nearest hospitals first.
- **Resource Information:** View available beds, ICU beds, ventilators, and oxygen availability.
- **Cost Transparency:** View the average hospital cost and its billing period.
- **Direct Contact:** Call hospitals using their displayed contact numbers.
- **Interactive Map:** View search results on a colour-coded map based on resource availability.
- **Live Dashboard:** View overall hospital and resource availability statistics.

### 🏥 Hospital Admin Portal

- Hospital administrator registration and login.
- Each administrator account is associated with a hospital.
- Update available general beds, ICU beds, and ventilators.
- Update oxygen availability.
- Update average hospital cost and billing period.
- Input validation to prevent invalid resource counts.
- Maintain a history of resource updates.

### 🔐 Security & Data Management

- Password hashing using **bcrypt**.
- Passwords are never stored in plain text.
- Patient searches are recorded in a MongoDB collection.
- Search logs include location, resource type, result count, and timestamp.
- Resource update history supports tracking previous changes.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Frontend / User Interface | Streamlit |
| Database | MongoDB Atlas |
| Database Connectivity | PyMongo |
| Distance Calculation | Geopy |
| Interactive Maps | Folium |
| Streamlit Map Integration | streamlit-folium |
| Authentication & Security | bcrypt |
| Environment Configuration | python-dotenv |

---

## ⚙️ System Workflow

1. **Hospital Registration:** Hospital administrators register and create their login credentials.
2. **Resource Management:** Administrators update the current availability of beds, ICU beds, ventilators, oxygen, and average costs.
3. **Patient Search:** Patients select their preferred Mumbai area, required medical resource, and search radius.
4. **Distance Calculation:** The application calculates geographical distances between the selected area and registered hospitals using Geopy.
5. **Hospital Ranking:** Hospitals with the requested resources are filtered and sorted by nearest distance.
6. **Results Display:** Patients receive hospital details, resource availability, approximate costs, contact numbers, and map locations.
7. **Database Logging:** Patient searches and hospital resource updates are recorded in MongoDB.

---

## 📂 Project Structure

```text
CareMap/
│
├── Home.py
│
├── pages/
│   ├── 1_Search.py
│   ├── 2_Map.py
│   └── 3_Hospital_Admin.py
│
├── config/
│   └── db.py
│
├── models/
│   └── search_log.py
│
├── utils/
│   ├── distance.py
│   ├── geo.py
│   └── ui.py
│
├── scripts/
│   ├── setup_db.py
│   └── Migrate_schema.py
│
├── auth.py
├── crud.py
├── measure_performance.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

Follow these instructions to run CareMap locally.

### 1. Prerequisites

Make sure you have installed:

- Python 3.10 or above
- MongoDB Atlas account
- Git
- Code editor (VS Code recommended)

### 2. Clone the Repository

```bash
git clone https://github.com/aavp268-tech/Hospital-Bed-Resource-Availability-Tracker-.git
```

Navigate to the project directory:

```bash
cd Hospital-Bed-Resource-Availability-Tracker-
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory.

Add your MongoDB Atlas connection details:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGODB_DATABASE=hospital_tracker
```

**Note:** Replace the placeholders with your actual MongoDB credentials. Never upload your `.env` file or expose database credentials on GitHub.

### 6. Initialize the Database

Check your MongoDB connection:

```bash
python -m config.db
```

Create the required collections and indexes:

```bash
python -m scripts.setup_db
```

Add hospital records to the `hospitals` collection in MongoDB Atlas.

### 7. Run the Application

Start the Streamlit application:

```bash
streamlit run Home.py
```

Open the local URL displayed in your terminal:

```text
http://localhost:8501
```

---

## 🧪 Testing & Performance Evaluation

CareMap was evaluated through manual functional testing and performance measurements.

### Functional Testing

Nine manual functional test cases were performed successfully.

| Test Case | Result |
|---|---|
| Hospital search | ✅ Passed |
| Resource filtering | ✅ Passed |
| Map display | ✅ Passed |
| Admin login – valid credentials | ✅ Passed |
| Admin login – invalid credentials | ✅ Passed |
| Hospital resource updates | ✅ Passed |
| Search after resource update | ✅ Passed |
| Input validation | ✅ Passed |
| No-availability scenario | ✅ Passed |

### Performance Results

Performance evaluation was conducted using 17 hospitals connected to MongoDB Atlas.

| Performance Metric | Result |
|---|---|
| Average Search Response Time (25 searches) | 0.289 seconds |
| Maximum Search Response Time | 0.642 seconds |
| Search Accuracy | 25/25 correct results |
| Average Admin Update Visibility | 1.25 seconds |
| Maximum Admin Update Visibility | 1.56 seconds |
| Distance Calculation Accuracy | Mean difference: 0.04 km |
| Maximum Distance Difference | 0.16 km |

**Note:** These results are based on small-sample testing from a single machine. Response times include network latency to the hosted MongoDB database and should not be interpreted as production-scale benchmarks.

---

## ⚠️ Current Limitations

- Search locations are restricted to 32 predefined areas in Mumbai.
- GPS-based automatic location detection is not implemented.
- Hospital availability depends on the latest manual administrator update.
- Hospital administrator registration does not currently require approval or invitation.
- Average hospital costs are manually entered and not independently verified.
- Search history is maintained, but a dedicated analytics dashboard is not yet available.

---

## 🔮 Future Enhancements

The following improvements can make CareMap more scalable and useful:

- 📍 GPS-based patient location detection.
- 📱 Dedicated mobile application.
- 💰 Separate cost estimates for general and ICU beds.
- 🔍 Advanced filtering and sorting based on hospital costs.
- ✅ Hospital verification and administrator approval.
- 🔗 Integration with hospital management systems for automated updates.
- 🏥 Expansion to hospitals across multiple cities.
- 📊 Analytics dashboard for hospital resource utilization.
- 🤖 Predictive analysis for hospital bed demand and resource planning.

---

## 📚 Research References

1. S. Langi et al., "Bridging the gap in critical care: A data-driven approach to hospital bed management in Pune," *International Journal of Research Culture Society*, vol. 9, no. 1, 2025.
2. J. Jacob, "The Intelligent BedTracker: Enhancing inpatient ward efficiency and emergency department flow in low-resource health systems," 2025.
3. S. Hiremath et al., "Dynamic bed availability tracker for healthcare using queuing model," *IJIRT*, vol. 11, no. 12, 2025.
4. B. Graham, R. Bond, M. Quinn and M. Mulvenna, "Using data mining to predict hospital admissions from the emergency department," *IEEE Access*, vol. 6, 2018.
5. V. S. Chitrak, "MedGrid: A real-time hospital bed tracking and patient management system using MERN stack," *IJEDR*, vol. 14, no. 2, 2026.
6. V. K. Prasad et al., "ABV-CoVID: An ensemble forecasting model to predict availability of beds and ventilators for COVID-19 like pandemics," *IEEE Access*, vol. 10, 2022.

---

## 👩‍💻 Project Team

**Developed by:**

- Anuja Pisal
- Apurva More
- Mrunmayi Surve

**Project Guide:** Prof. Mohan Bonde

**Department of Data Science**

Usha Mittal Institute of Technology, SNDT Women's University, Mumbai.

---

## ⚖️ Disclaimer

CareMap is an academic student project developed for educational and research purposes.

Hospital availability and cost information may change without notice. Patients and their families should always contact the hospital directly to confirm bed availability, facilities, and costs before travelling.

**CareMap is not a substitute for professional medical advice or emergency medical services.**

---

⭐ If you find this project interesting, consider giving the repository a star!

**CareMap – Making Hospital Resource Discovery Simpler and More Accessible.**
