# InstaLoader API and PWA

This project contains both a REST API and a Progressive Web App (PWA) for downloading Instagram media.

## API Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Navigate to the API directory:
```bash
cd instaloader_api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional but recommended) Login to Instagram to avoid rate limits and access private content:
```bash
python login.py
```
This will prompt for your Instagram username and password and save the session for future use.

5. Run the API:
```bash
python api.py
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Root endpoint
- `POST /api/download` - Start a download job
- `GET /api/status/{job_id}` - Get download job status
- `GET /api/profile-info/{username}` - Get Instagram profile information

## PWA Setup

### Prerequisites
- A web server to serve the files
- The API server running

### Usage

1. Serve the PWA files using a web server (e.g., Python's http.server, nginx, Apache)
2. Ensure the API URL in `js/app.js` is correctly set to your API endpoint
3. Access the PWA through your web browser

### Features
- Download Instagram profiles or individual posts
- Real-time download status updates
- Profile information lookup
- PWA functionality (installable on devices)

## Configuration

In the PWA's `js/app.js`, make sure to update the `apiBaseUrl` to match your API server's address.

## Important Notes

- Instagram requires authentication for accessing content. Use the login.py script to authenticate.
- Be respectful of Instagram's terms of service and rate limits.
- Consider using proxy services if facing rate limiting issues.

## Security Note

This application is designed for educational purposes. In production, you should:
- Add authentication and authorization
- Implement rate limiting
- Add proper error handling
- Respect Instagram's terms of service
- Add input validation