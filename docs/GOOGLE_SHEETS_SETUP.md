# Google Sheets Export Setup Guide

## Overview
This guide helps you set up Google Sheets export functionality for the Mortgage Analysis Tool. Once configured, you can export your analysis directly to Google Sheets with beautiful formatting and share links with friends.

## Step-by-Step Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Enter project name (e.g., "mortgage-analysis-tool")
4. Click "Create"

### 2. Enable Google Sheets API
1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

### 3. Create Service Account
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Enter service account name (e.g., "mortgage-sheets-exporter")
4. Click "Create and Continue"
5. Skip role assignment (click "Continue")
6. Click "Done"

### 4. Generate Service Account Key
1. In "Credentials" page, click on your service account email
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key"
4. Select "JSON" format
5. Click "Create"
6. Your credentials file will download automatically

### 5. Setup Credentials File
1. Rename the downloaded file to `google_credentials.json`
2. Move it to your project folder (same directory as `streamlit_app.py`)

```
know_your_mortgage/
├── google_credentials.json  ← Place here
├── streamlit_app.py
├── mortgage_analyzer.py
└── requirements.txt
```

### 6. Install Dependencies
```bash
pip install gspread google-auth
```

## How It Works

### What Happens When You Export:
1. **Creates New Sheet**: A timestamped Google Sheet in your service account's drive
2. **Makes It Public**: Anyone with the link can view (but not edit)
3. **Returns Share Link**: You get a shareable URL instantly

### Sheet Structure:
- **Summary Dashboard**: Key metrics and recommendations
- **Detailed Data**: Year-by-year breakdown for all scenarios
- **Parameters**: All input assumptions used in analysis

### Features:
✅ **Professional formatting** with colors and styling
✅ **Currency formatting** for all financial values
✅ **Shareable links** - works without Google account
✅ **Multiple sheets** for different views
✅ **Real-time updates** when you run new analyses

## Sharing Your Analysis

Once exported, you get a link like:
```
https://docs.google.com/spreadsheets/d/abc123...
```

**Share this with friends to show:**
- Your mortgage scenarios comparison
- Which option provides best financial outcome
- All the detailed calculations behind your decision

## Troubleshooting

### Common Issues:

**Error: "Authentication failed"**
- Ensure `google_credentials.json` is in the correct location
- Verify the file isn't corrupted (should be valid JSON)

**Error: "Permission denied"**
- Make sure Google Sheets API is enabled in your project
- Check that service account has proper permissions

**Error: "Module not found"**
- Install required packages: `pip install gspread google-auth`

### Alternative: Manual Import
If automatic export doesn't work, you can:
1. Use "Generate CSV Export" button
2. Download the CSV file
3. Go to Google Sheets → File → Import → Upload the CSV

## Security Notes

- Service account credentials should be kept private
- The generated sheets are public (anyone with link can view)
- No personal Google account access required
- Service account creates sheets in its own drive space

## Need Help?

If you encounter issues:
1. Check that all setup steps were followed exactly
2. Verify file permissions on `google_credentials.json`
3. Try the CSV export as a fallback option

The Google Sheets export feature makes sharing your mortgage analysis much easier - no more sending files back and forth!