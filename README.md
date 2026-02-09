# Google Docs Typewriter

A stealthy, human-like typing simulation tool for Google Docs. It "types" your content into a document character-by-character to create a natural version history, evading detection mechanisms that look for copy-pasted or AI-generated text.

![UI Screenshot](https://via.placeholder.com/800x400?text=Web+Interface+Preview)

## Features

*   **Humanized Typing**: Variable typing speed, random pauses, and simulated typos with corrections.
*   **Stealth Mode**: Hides automation flags (`navigator.webdriver`) to avoid detection.
*   **Web Interface**: Modern, dark-mode UI for easy control.
*   **Secure**: Runs locally. Your Google session and data never leave your machine.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

## Usage

### 1. Start the App
Run the local server:
```bash
uvicorn backend.server:app --reload
```
Open your browser to: **http://127.0.0.1:8000**

### 2. Connect Google Account
*   Click **"Login to Google"** in the UI.
*   A Chrome window will open. Log in to your account.
*   **Close the Chrome window** once logged in.

### 3. Start Typing
*   **Google Doc URL**: Paste the link to your target document.
*   **Source Content**: Paste the text you want typed.
*   **Settings**: Adjust WPM (Words Per Minute) and cleanup options.
*   Click **"Start Typing"**.

## Sharing on GitHub

This project is ready to be shared.

**Important Security Note**:
A `.gitignore` file is included to ensure your **login session (`chrome_profile/`)** is NEVER uploaded to GitHub.

### How to push:

1.  Initialize Git (if not done):
    ```bash
    git init
    ```
2.  Add files:
    ```bash
    git add .
    ```
3.  Commit:
    ```bash
    git commit -m "Initial commit of Google Docs Typewriter"
    ```
4.  Push to your repository:
    ```bash
    git branch -M main
    git remote add origin <your-github-repo-url>
    git push -u origin main
    ```
