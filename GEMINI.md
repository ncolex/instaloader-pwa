# Project Overview

This project is a web application for downloading Instagram media. It consists of a Python backend API and a Progressive Web App (PWA) frontend.

- **Backend:** The backend is a REST API built with Python and the **FastAPI** framework. It uses the **`instaloader`** library to interact with Instagram's data. The API provides endpoints for initiating download jobs, checking job status, and retrieving profile information. It is designed to be deployed as a serverless function on Vercel.

- **Frontend:** The frontend is a **Progressive Web App (PWA)** built with vanilla JavaScript, HTML, and CSS. It provides a user interface to input an Instagram username or post URL, start the download process, and receive a zipped file with the media. The PWA communicates with the backend API to perform these actions.

- **Deployment:** The project is configured for deployment on **Vercel**, using `@vercel/python` for the serverless backend and `@vercel/static` for the PWA.

# Building and Running

## Prerequisites

- Python 3.8+
- Node.js and npm

## Installation

1.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Node.js dependencies (for running scripts):**
    ```bash
    npm install
    ```

## Running the Application

### Development

1.  **Run the backend API:**
    ```bash
    npm run dev
    ```
    This will start the FastAPI server in development mode with auto-reload at `http://localhost:8000`.

2.  **Run the PWA:**
    In a separate terminal, run the PWA development server:
    ```bash
    npm run pwa
    ```
    This will serve the PWA at `http://localhost:8080`.

    You can then access the application in your browser at `http://localhost:8080`. The PWA will automatically connect to the API running on port 8000.

### Production

The `npm start` command is configured to run the application in a production environment, typically on a platform like Vercel.

# Development Conventions

- **Backend:** The main backend logic is contained in `api/index.py`. It uses FastAPI for routing and handling requests. Environment variables (`INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`) are used for Instagram authentication.
- **Frontend:** The main frontend logic is in `instaloader_pwa/js/app.js`. The API base URL is dynamically resolved in the `resolveApiBaseUrl` function, which defaults to `http://localhost:8000` in a local development environment.
- **Scripts:** The `package.json` file contains scripts for running the application in development and production, as well as for serving the PWA.
- **Deployment:** The `vercel.json` file defines the build and routing configuration for deploying the application on Vercel. The backend is deployed as a serverless function, and the PWA is served as a static site.
