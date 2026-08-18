# Aau Ya Nahi — AI Attendance Risk Predictor 🎓
> **“Know your attendance. Know your risk.”**

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/backend-Flask%203.1-green.svg)](https://palletsprojects.com/p/flask/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%201.4%2B-orange.svg)](https://scikit-learn.org/)
[![Test Suite](https://img.shields.io/badge/tests-22%20passed%20%28100%25%29-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-purple.svg)]()

---

## 📌 Project Overview
**“Aau Ya Nahi”** is an academic productivity and risk prediction web application designed for college students. It helps students understand their attendance health, simulate future scenarios, determine exact safe bunk boundaries or recovery requirements, and obtain **Machine Learning-based risk assessments** for semester-end debarment prevention.

---

## 🌟 Core Features

### 1. Attendance Predictor (What-If Simulation)
* Input total classes conducted, attended classes, and planned upcoming classes.
* Compares two future trajectories side-by-side:
  * 🟢 **If you Attend all upcoming classes** (Gain percentage + new total)
  * 🔴 **If you Miss (Bunk) all upcoming classes** (Drop percentage + warning alert)
* Interactive **Chart.js** trajectory curve showing future progression.
* Step-by-step class-by-class progression matrix.

### 2. “Aau Ya Nahi?” Dual Decision Calculator
* **A. “Kitni Classes Chhod Sakta Hoon?” (Max Safe Leaves)**:
  * Computes the maximum number of upcoming classes a student can safely skip while strictly maintaining at least 75% attendance.
* **B. “Kitni Classes Attend Karni Hogi?” (Consecutive Recovery Needed)**:
  * If attendance has dropped below 75%, calculates the exact minimum number of consecutive classes required to restore eligibility.
* **Expandable Mathematical Proofs**: Displays the exact algebraic derivation for transparency.

### 3. AI / ML Attendance Risk Prediction Module
* Multi-class classification using **Scikit-Learn** into:
  * 🟢 **Low Risk**: Healthy buffer, positive momentum, low probability of shortage.
  * 🟡 **Medium Risk**: Fragile boundary, high sensitivity to missed classes.
  * 🔴 **High Risk**: Active shortage, urgent recovery required.
* Outputs **Confidence Score**, **Class Probabilities** (Low %, Medium %, High %), and **Explainable AI (XAI)** factor contributions.
* Generates contextual, responsible academic advice.

### 4. Subject-Wise Semester Tracker
* Track individual courses (e.g. Data Structures, OS, DBMS, AI) with dedicated percentage bars and safe leave counts.
* Quick **+1 Attend** and **+1 Miss** action buttons.
* Real-time **Semester Aggregate Health** score with persistent `localStorage` storage.

### 5. AIML Mini-Project & Viva Demonstration Hub
* Displays full training metadata, 5-Fold cross-validation scores, out-of-sample test accuracy (95.3%), and feature importance weights.
* Includes a complete **Viva Q&A Defense Guide** for college examiners.

---

## 📐 Mathematical Foundations

### 1. Current Attendance
$$\text{Current \%} = \left( \frac{\text{Classes Attended}}{\text{Total Classes Conducted}} \right) \times 100$$

### 2. Maximum Safe Skippable Classes ($X_{\text{bunk}}$)
To maintain at least $R\%$ attendance (where $R = 75\%$ or custom fraction $r = R / 100$):
$$\frac{\text{Attended}}{\text{Total} + X} \ge r \implies \text{Attended} \ge r \cdot (\text{Total} + X)$$
$$X \le \frac{\text{Attended}}{r} - \text{Total}$$
$$X_{\text{max}} = \left\lfloor \frac{\text{Attended} \times 100}{R} - \text{Total} \right\rfloor$$
*(If current attendance is already $< R\%$, $X_{\text{max}} = 0$)*

### 3. Minimum Consecutive Recovery Classes ($X_{\text{attend}}$)
To restore attendance to at least $R\%$ (where $r = R / 100$):
$$\frac{\text{Attended} + X}{\text{Total} + X} \ge r \implies \text{Attended} + X \ge r \cdot \text{Total} + r \cdot X$$
$$X(1 - r) \ge r \cdot \text{Total} - \text{Attended}$$
$$X_{\text{min}} = \left\lceil \frac{R \cdot \text{Total} - 100 \cdot \text{Attended}}{100 - R} \right\rceil$$
*(If current attendance is already $\ge R\%$, $X_{\text{min}} = 0$)*

---

## 🤖 Machine Learning Pipeline & Architecture

### Engineered Feature Vector (11 Features):
1. `current_attendance_pct`: Instantaneous percentage
2. `classes_attended`: Total attended count
3. `classes_missed`: Total missed count
4. `total_conducted`: Semester elapsed volume
5. `recent_trend_pct`: Recent 2-week attendance rate
6. `momentum_score`: `recent_trend_pct - current_attendance_pct`
7. `upcoming_classes`: Horizon simulation size
8. `required_pct`: Institution threshold (e.g. 75%)
9. `margin_pct`: Buffer above/below threshold (`current_pct - required_pct`)
10. `bunk_capacity`: Safe leaves capacity
11. `recovery_needed`: Recovery burden

### Model Benchmark Comparison (Trained on 3,500 Profiles):
| Model Algorithm | 5-Fold CV Accuracy | Test Accuracy | Macro F1 Score |
| :--- | :---: | :---: | :---: |
| **Decision Tree Classifier (Selected)** | **95.68% (±0.69%)** | **95.29%** | **94.12%** |
| **Random Forest Classifier** | 94.71% (±0.79%) | 94.86% | 93.73% |
| **Logistic Regression (Standardized)** | 92.71% (±0.77%) | 92.71% | 91.61% |

---

## 📂 Project Structure

```
AI Attendance risk predictor/
├── app.py                     # Flask REST API & Web Server
├── requirements.txt           # Python package dependencies
├── README.md                  # Complete Project Documentation & Viva Guide
├── services/
│   ├── __init__.py
│   ├── calculator.py          # Deterministic Mathematical Logic & Proofs
│   └── ml_service.py          # ML Inference, Explainability & Recommendations
├── ml/
│   ├── __init__.py
│   ├── train_model.py         # ML Training, Cross-Validation & Model Exporter
│   ├── model.joblib           # Trained Scikit-Learn Model
│   └── model_meta.json        # Evaluation Metrics & Feature Importances
├── dataset/
│   ├── generate_dataset.py    # Realistic College Attendance Dataset Generator
│   └── attendance_dataset.csv # 3,500 Student Profiles Dataset
├── static/
│   ├── css/
│   │   └── style.css          # Design System, CSS Variables, Light/Dark Modes
│   └── js/
│       ├── app.js             # REST API Controller & UI State Engine
│       ├── charts.js          # Chart.js Visualizations (Trajectory & Probabilities)
│       ├── subjects.js        # Subject-Wise Semester Tracker & LocalStorage
│       └── ui.js              # Theme Toggle, SVG Gauge & Notifications
├── templates/
│   └── index.html             # Semantic HTML5 Single-Page Web App
└── tests/
    ├── test_calculations.py   # Unit Tests for Math Formulas & Edge Cases
    └── test_api_endpoints.py  # Integration Tests for Flask REST Endpoints
```

---

## 🚀 Quick Start Guide

### 1. Clone or Open Project Directory
```bash
cd "AI Attendance risk  predictor"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Retrain ML Model & Regenerate Dataset
```bash
python dataset/generate_dataset.py
python ml/train_model.py
```

### 4. Run Unit & Integration Tests (22 Tests)
```bash
python -m unittest discover tests
```

### 5. Launch the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🎓 Viva & Mini-Project Defense Q&A

**Q1: Why use Machine Learning when exact algebraic formulas exist?**  
*Answer:* Mathematical formulas calculate only instantaneous static boundaries (e.g. "Missing 4 classes drops you to 75%"). In contrast, Machine Learning assesses **multi-dimensional risk** by analyzing behavioral momentum (recent 2-week trends), buffer fragility, semester progress ratio, and predicting the likelihood of debarment before final exams.

**Q2: How do you prevent data leakage in your ML pipeline?**  
*Answer:* We use stratified train/test splitting (80/20) and 5-Fold Stratified Cross-Validation on training data only. Preprocessing transformations and scaling are fitted exclusively on the training fold.

**Q3: Which feature has the highest importance in risk prediction?**  
*Answer:* `margin_pct` (the difference between current attendance and the required threshold) followed by `momentum_score` (recent attendance trajectory) and `recovery_needed`.

**Q4: How does the application encourage responsible behavior?**  
*Answer:* The application explicitly frames all outputs as planning and risk awareness indicators, warning students against unnecessary absences and providing clear recovery roadmaps when attendance drops.

---

## 📄 License
This project is licensed under the MIT License — free for academic and educational use.
