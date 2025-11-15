# 📞 Voicestack Call Analytics Dashboard

A comprehensive AI-powered call analytics dashboard designed for dental practices to analyze front desk operations, call patterns, and patient engagement metrics. The dashboard leverages Google's Gemini API for intelligent call classification, sentiment analysis, and quality assessments.

## 📋 Project Overview

This project analyzes call logs from dental practices to provide actionable insights on:
- **Call Operations**: Answer rates, voicemail rates, abandonment rates
- **Call Patterns**: Peak hours, duration analysis, inbound vs outbound distribution
- **Patient Engagement**: Contact type breakdown, call type classification
- **Booking Conversion**: Appointment scheduling success rates and patterns
- **Call Quality**: AI-generated sentiment analysis and quality observations
- **Temporal Trends**: Daily and hourly call volume analysis

The dashboard is built with Streamlit for interactive exploration and uses the Gemini API for intelligent transcript analysis.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **Streamlit** | Interactive web dashboard and UI framework |
| **Pandas** | Data manipulation and analysis |
| **Plotly** | Advanced data visualizations and interactive charts |
| **Google Gemini API** | AI-powered transcript classification and analysis |
| **Python 3.8+** | Core programming language |
| **python-dotenv** | Environment variable management |

---

## 📁 Project File Structure

```
voicestack-call-analytics/
│
├── main.py                          # Main Streamlit app & dashboard UI
├── quant_metrics.py                 # Quantitative metrics calculation
├── qual_metrics.py                  # Qualitative metrics (AI analysis)
│
├── call_logs.csv                    # Call dataset (not included in repo)
├── qualitative_cache.json           # AI analysis cache (generated on first run)
│
├── .env                             # Environment variables (not in repo)
├── .gitignore                       # Git ignore file
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## ⚙️ Setup Instructions

### **1. Prerequisites**
- Python 3.8 or higher
- Google Gemini API key (free tier available)
- Git (for cloning from GitHub)

### **2. Clone the Repository**

**Option A: From GitHub**
```bash
git clone https://github.com/yourusername/voicestack-call-analytics.git
cd voicestack-call-analytics
```

**Option B: Download from Google Drive**
1. Download the project folder from Google Drive
2. Extract the ZIP file
3. Open terminal/command prompt in the extracted folder
4. Navigate to the project directory:
```bash
cd path/to/voicestack-call-analytics
```

### **3. Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
source venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### **4. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **5. Set Up Environment Variables**

Create a `.env` file in the project root directory with the following content:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### **6. Prepare Data**

Place your `call_logs.csv` file in the project root directory. The CSV should contain the following columns:

```
Call Time, transcript, From, To, Virtual Number, Call Direction, Call Status, 
Contact Type, Hangup Leg, Ring Duration, Conversation Duration, 
Voicemail Duration, Total Duration
```
**Note:** All PHI/PII data should be redacted or replaced with dummy values for privacy compliance.

### **7. Run the Application**

```bash
streamlit run main.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 🎯 Dashboard Features

### **Tab 1: 📊 Overview**
- Total calls, answer rate, voicemail rate, abandon rate KPI cards
- Summary metrics table

### **Tab 2: ⏱️ Duration & Direction**
- Average call durations (conversation, ring, total)
- Inbound vs outbound split with pie chart visualization

### **Tab 3: 👥 Contact Types**
- Contact type distribution (Existing Patient, New Patient, etc.)
- Call type classification breakdown

### **Tab 4: 📈 Trends**
- Daily call volume and answered calls over time
- Hourly call distribution to identify peak hours
- Call volume by hour analytics

### **Tab 5: 📞 Call Status**
- Call status distribution by hour (stacked histogram)
- Overall call status summary

### **🤖 Qualitative Analysis Section**
- AI-generated call type classifications (bar chart)
- Sentiment distribution (Positive/Neutral/Negative)
- All call details with classifications, sentiment, and quality observations

### **📅 Booking Conversion Metrics Section**
- Booking confirmation rate, attempted bookings, and total scheduling calls
- Booking status distribution (pie chart)
- Booking status trends by hour
- Summary table for scheduling calls only

---

### **Caching System:**

The `qualitative_cache.json` file stores all AI-generated insights. Structure:

```json
{
  "transcript_text_here": {
    "call_type": "Appointment Scheduling / Rescheduling",
    "sentiment": "Positive",
    "quality_observation": "Staff was professional and helpful.",
    "booking_status": "Booking Confirmed"
  }
}
```

**Benefits:**
- First run processes all transcripts (~2-5 minutes for 1000 calls)
- Subsequent runs load from cache (instant)
- Adding new calls only processes new transcripts

---

## 🚀 Running the Dashboard

### **Local Development**
```bash
streamlit run main.py
```
---

## 📊 Key Metrics Explained

| Metric | Definition | Business Impact |
|--------|-----------|-----------------|
| **Answer Rate** | % of calls answered by staff | Operational efficiency |
| **Booking Confirmation Rate** | % of scheduling calls that resulted in confirmed bookings | Patient acquisition |
| **Sentiment Distribution** | % of calls with Positive/Neutral/Negative sentiment | Patient satisfaction & front desk quality |
| **Peak Hours** | Hours with highest call volume | Staffing optimization |
| **Call Duration Patterns** | Average conversation, ring, and total time | Service efficiency |
| **Contact Type Mix** | % of Existing vs New Patient calls | Patient retention vs acquisition |

## 📊 Use Cases & Metric Importance

### **For Front Desk Team (Day-to-Day Operations & Efficiency)**

| Metric | Why It Matters | Daily Impact |
|--------|---------------|--------------|
| **Answer Rate & Call Status** | Shows staff performance and efficiency handling calls | Monitor real-time performance, identify coaching needs |
| **Call Duration Patterns** | Long ring times indicate understaffing; excessive times suggest inefficiency | Optimize call speed without sacrificing quality |
| **Sentiment & Quality** | Feedback on how staff conducts calls (verbiage, professionalism, resolution) | Learn from top-rated calls, improve patient interactions |
| **Peak Hours Analysis** | Optimize staffing allocation by call volume patterns | Schedule breaks strategically, prepare for busy periods |
| **Booking Status** | Track successful bookings vs obstacles encountered | Troubleshoot barriers, improve booking conversion |

**Sources**: 
- [Progressive Dental Marketing - The 3 Major Front Desk KPIs](https://www.progressivedentalmarketing.com)
- [WelcomeWare - Keys To Front Desk Success: KPIs, Data, And Best Practices](https://www.welcomeware.com)

---

### **For Practice Owner (Business Performance, Acquisition, Retention & Revenue)**

| Metric | Business Impact | Strategic Value |
|--------|-----------------|-----------------|
| **Booking Conversion Rate** | Each missed booking = revenue loss. 10% improvement = significant annual increase | Set targets, incentivize staff, measure training ROI |
| **Patient Contact Mix** | Balance new patient acquisition vs existing patient retention (retention = 25-30% of production) | Optimize marketing spend, refine recall systems |
| **Answer & Abandon Rates** | High abandonment = lost patients + negative reviews + reputation damage | Justify staffing investments, track ROI |
| **Sentiment Analysis** | Predicts patient satisfaction, churn risk, and online review impact | Monitor trends, identify improvement areas |
| **Staffing Efficiency** | Overstaffing wastes payroll; understaffing loses bookings | Model scenarios, project annual labor cost savings |
| **Call Type Distribution** | High cancellations/no-shows reveal process issues; 5-10% reduction = significant revenue gain | Implement automated reminders, adjust policies |
| **Call Quality & Performance** | Front desk quality directly impacts case acceptance rates and patient lifetime value | Set standards, identify top performers, create training programs |

**Sources**:
- [Databox - Dental KPI Dashboard: 12 Metrics and KPIs](https://databox.com/kpi/dental-kpi-dashboard)
- [MGE Online - 12 Key Performance Indicators for Dental Practice](https://www.mgeonline.com)
- [Dandy - Dental Practice KPIs: What to Track and How](https://www.dandy.com)
- [Dental Economics - The 6 Critical KPIs for Dentists (Levin Group)](https://www.dentaleconomics.com)
- [Progressive Dental Marketing - Converting Phone Inquiries into Scheduled Appointments](https://www.progressivedentalmarketing.com)

---

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Google Gemini API Docs](https://ai.google.dev)
- [Plotly Documentation](https://plotly.com/python)
- [Pandas Documentation](https://pandas.pydata.org)

---

---

## 🔐 Security & Privacy

- **PHI/PII Compliance**: All sensitive data is redacted from transcripts before processing
- **API Key Security**: Never commit `.env` file to version control
- **Data Storage**: Cache is stored locally; no data sent to third parties except Gemini API
- **.gitignore includes**: `.env`, `qualitative_cache.json`, `call_logs.csv` (optional)

---

## ⚠️ Important Notes

### **First Run**
- Delete `qualitative_cache.json` before first run to ensure fresh AI analysis
- Processing 1000 calls takes ~2-5 minutes depending on API rate limits
- Watch the progress bar and status messages

### **API Rate Limits**
- Gemini API free tier: 60 requests per minute
- Batch size: 30 transcripts per request
- Adjust `BATCH_SIZE` in `qual_metrics.py` if experiencing rate limit errors

### **Data Privacy**
- Ensure all call transcripts have PHI/PII redacted
- Store sensitive data securely
- Follow HIPAA guidelines if handling real dental practice data

---