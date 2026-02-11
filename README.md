# ⚡ Sparky: Your AI-Powered Agent

Welcome to Sparky! Sparky is a Python-based autonomous agent designed for job search. This guide will walk you through the setup, from environment configuration to API integration.

## 🛠 Prerequisites
Before you begin, ensure you have the following installed:

Python 3.10+

pip (Python package manager)

## 🚀 Getting Started

1. Clone & Set Up Virtual Environment
Isolation is key! We use venv to keep Sparky’s dependencies from clashing with your system.

2. Get the required keys

### ♊ Gemini API Key (Google AI Studio)

Go to Google AI Studio.
Sign in with your Google account.
Click the "Get API key" button on the left sidebar.
Click "Create API key" (choose a new project or an existing one).
Copy the generated key immediately.

### 🕸 Apify API Key

(Apify Console)[http://console.apify.com]

Log in to your Apify Console.
Navigate to Settings (gear icon) in the bottom-left.
Click on the Integrations tab.
Find your Personal API token and click the Copy icon.

### ⚙️ Configuration
Open the app.py file in your preferred code editor and look for the configuration section. Paste your keys directly into the variables:

```python
# --- CONFIGURATION ---
GEMINI_API_KEY = "PASTE_YOUR_GEMINI_KEY_HERE"
APIFY_API_KEY = "PASTE_YOUR_APIFY_KEY_HERE"
# ---------------------
```

[!WARNING] Security Tip: Never commit your app.py to a public repository with these keys visible. Use a .env file for production-level security.

## 🏃 Running Sparky

With your environment active and keys saved, start the agent:

```bash
source launch.sh
```
