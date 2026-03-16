# 🚗 Vehicle-s-Testing-Accuracy-Dashboard (TATA Motors Project) 


## 📌 Project Overview
This project analyzes vehicle testing data and visualizes testing accuracy trends through an interactive dashboard.  

The system is built using a **FastAPI backend**, **MySQL database**, and a **Streamlit frontend dashboard**.  
It retrieves live data from the database through API endpoints and displays insights for analysis.

This project demonstrates **real-world data analytics architecture used in industry systems.**

---

## 🛠 Tech Stack

- **Python**
- **FastAPI** (Backend API)
- **Streamlit** (Interactive Dashboard)
- **MySQL** (Database)
- **Pandas**
- **SQLAlchemy**
- **Git & GitHub**

---

## 🏗 Project Architecture

            MySQL Database
                  ↓
        FastAPI Backend (API)
                  ↓
         Streamlit Dashboard
                  ↓
    User Interaction & Visualizations
                  


The dashboard fetches live vehicle testing data through FastAPI APIs and displays insights using interactive charts and tables.

---

## 📊 Dashboard Features

- Vehicle testing accuracy analysis
- Plant-wise filtering
- Date range filtering
- Top DTC code analysis
- Vehicle model insights
- API-based live data retrieval

---

## 📡 Example API Response

The backend provides JSON responses such as:
  {
    "RECORD_ID": 41550805,
    "ENGINE_NO": "NA",
    "VC_NO": "123456789000R",
    "VIN_NO": "MAT122332342443434",
    "ECU_TYPE": "ESCL Marquardt Osprey",
    "TIME_TOFLASH": null,
    "FLASHING_REMARK": "ECU & PLM PARA RECORD COUNT MATCH. ECU:2, PLM:2   ECU TML_PART_NO - 543816211302.    ECU HW_NO - 543816212016.    ECU SW_VERNO - R.010.00.   ",
    "WRITING_REMARK": "ECU VIN:MAT122332342443434.  ",
    "PAIRING_REMARK": "NOT STARTED",
    "STATIC_REMARK": "NO ERRORS PRESENT IN ECU.  ",
    "FLASHING_STATUS": 0,
    "WRITING_STATUS": 1,
    "PAIRING_STATUS": 1,
    "STATIC_STATUS": 1,
    "DTC_CODE": "NO ERRORS|,U010008,,U160981,,",
    "STATION_ID": "172.23.27.80_TR1",
    "TCF_LINE": "TR1_HEV",
    "PLANT_CODE": "TCF2",
    "PROD_DATETIME": "2025-06-03T09:51:40",
    "TOOL_VERSION": "V 25.4.20.25",
    "CYCLE_TIME": "3_2_5_154 Second",
    "IS_TRIAL": 0,
    "FMID": 1922745,
    "BID": 282574,
    "BL_NO": "5473E4Z0100901",
    "BL_VER": "H9",
    "DTS_TRANSFER_DATE": null
  }

  ▶ How to Run the Project
1️⃣ Clone the repository
git clone https://github.com/YOUR_USERNAME/Vehicles-Testing-Accuracy-Dashboard-Project-TATA-Motors-

2️⃣ Install dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

3️⃣ Run FastAPI backend
uvicorn main:app --reload

4️⃣ Run Streamlit dashboard
streamlit run frontend/app.py

📬 Author :
**Prathamesh Umesh Mhaske**
