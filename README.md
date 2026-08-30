# Empyrean DGM Margin & Project Tracker

Simple Streamlit dashboard to track account/project margins from an Excel SOW.

## Quick Start

1. Create a Python virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. **Configure API Key (Recommended)**
   - Copy `.streamlit/secrets.toml` file in the project
   - Add your Gemini API Key:
     ```toml
     gemini_api_key = "your-actual-api-key-here"
     ```
   - Get a free API key from: https://aistudio.google.com/apikey

4. Run the app:

```bash
streamlit run app.py
```

5. Upload your SOW Excel/CSV file in the sidebar to load the dashboard.

## Features

✅ **Data Validation**: Automatic cleaning and validation of numeric columns  
✅ **Error Handling**: Comprehensive error messages and recovery  
✅ **Security**: API key management via `.streamlit/secrets.toml` (no hardcoding)  
✅ **Formatting**: Consistent currency and percentage formatting across tables  
✅ **AI Diagnostics**: Gemini-powered root cause analysis with fallback model selection  
✅ **Dual Views**: Overall account view or single project (SOW) deep dive  
✅ **Simulations**: What-if rate increase scenarios  

## Data Format Requirements

Your Excel/CSV file should include these columns (auto-detected):
- **SOW** (Statement of Work / Project Name)
- **Rate $/hr** (Bill Rate)
- **Hrs/month** (Hours per month) - defaults to 164.3 if missing
- **Cost** (Cost per hour) - optional

Additional columns like Name, Role, Candidate, etc. are auto-detected for display.

## Troubleshooting

- **"Could not locate required SOW or Rate $/hr columns"**: Ensure your file has SOW and Rate columns
- **"Uploaded file is empty"**: Check that your data file contains rows
- **AI Diagnostic errors**: Verify your Gemini API key is valid and active
- **Excel read errors**: Install openpyxl: `pip install openpyxl`
