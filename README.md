# Kenya Smart Credit Verification System - Streamlit App

## 🚀 Built With
[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-red?logo=streamlit)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-black?logo=pandas)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Computing-blue?logo=numpy)](https://numpy.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualization-darkblue?logo=plotly)](https://plotly.com/python/)
[![OpenPyXL](https://img.shields.io/badge/OpenPyXL-Excel-green)](https://openpyxl.readthedocs.io/)
[![pip](https://img.shields.io/badge/pip-Package%20Manager-orange?logo=pypi)](https://pip.pypa.io/en/stable/)

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Navigate to your project directory:**
```bash
cd C:\smart-credit-verify
```

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install streamlit pandas numpy plotly openpyxl
```
## 📱 Features

### 🏠 Dashboard
- Overview of cost savings and performance metrics
- Real-time comparison: Current vs Smart approach
- Decision breakdown and score distributions

### 💰 Cost Analysis
- Monthly and annual cost projections
- ROI calculations
- CRB usage breakdown by reason

### 🔍 Application Simulator
- Test individual loan applications
- See real-time tier-by-tier evaluation
- Understand why CRB checks are needed or avoided

### 📊 Analytics
- Advanced visualizations
- Score distributions by decision
- CRB usage patterns by loan amount
- Export data to CSV

### ℹ️ About
- Solution overview
- Problem statement
- Technology stack
- Impact projections

## 🎛️ Controls

- **Sidebar Navigation:** Switch between pages
- **Application Count Slider:** Adjust the number of applications to simulate (100-5000)
- **Interactive Charts:** Hover for detailed information
- **Live Simulator:** Input custom application data and see instant results

## 📊 Demo Data

The app generates realistic demo data including:
- Loan amounts (KES 3,000 - 30,000)
- SIM card age and device characteristics
- Application behavior patterns
- CRB records and scores
- KRA PIN and NSSF verification status

## 💡 Key Metrics Displayed

1. **Total Applications Processed**
2. **CRB Checks Avoided** (with percentage)
3. **Cost Savings** (amount and percentage)
4. **Approval Rate**
5. **Monthly/Annual Projections**

## 🎯 Use Cases
- Adjust application volume to match client's scale
- Export data for further analysis
- Simulate individual applications with custom parameters
- Understand decision logic
- Test edge cases
- Visualize cost savings at different scales
- Understand CRB usage patterns
- Export results for business cases

## 🔧 Customization

### Adjust Cost Parameters
In the code, you can modify:
- `self.crb_cost = 50` - Change CRB cost per check
- Tier 2 costs (currently simulated)
- Score thresholds for decisions

### Modify Scoring Logic
- Edit `Tier1RiskScorer` class for different scoring rules
- Adjust weights in `should_check_crb()` method
- Change approval thresholds in `final_decision()` method

### Change Styling
- Modify CSS in the `st.markdown()` section at the top
- Adjust Plotly chart colors and themes
- Change layout columns and spacing

## 📈 Performance

- Handles 1000 applications in < 2 seconds
- Tested up to 5000 applications
- Responsive UI with cached data processing

## 🎓 Next Steps

1. **Connect Real Data:**
2. **Add Authentication:** 
3. **API Integration:** 
4. **Machine Learning:** 
5. **Database:** 

**Author**
Peterson Muriuki
Email: pitmuriuki@gmail.com
GitHub: https://github.com/Peterson-Muriuki
LinkedIn: https://www.linkedin.com/in/peterson-muriuki-5857aaa9/

**License**
This project is licensed under the MIT License.

---

**Made with ❤️ for Kenya's lending ecosystem**
