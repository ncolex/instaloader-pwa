# InstaLoaderApp - Project Context

## Project Overview
InstaLoaderApp is an Android application that serves as a bulk media downloader for Instagram. It allows users to automatically download all pictures, videos, and reels from an Instagram account in one click, based on the Python library [instaloader](https://github.com/instaloader/instaloader).

The app is built with Kotlin for the Android frontend and integrates Python code using Chaquopy for the core Instagram downloading functionality. It provides both bulk profile downloading and single post/reel downloading capabilities.

## Architecture
- **Platform**: Android (API level 21+)
- **Language**: Kotlin (Android frontend), Python (backend logic)
- **Build System**: Gradle
- **Python Integration**: Chaquopy plugin
- **Dependencies**: instaloader Python library, AndroidX libraries, Material Design components

## Key Components

### Core Functionality
- **Python Backend**: Located at `app/src/main/python/script.py`, contains the core Instagram downloading logic using the `instaloader` library
- **Android Frontend**: `app/src/main/java/com/alphacorp/instaloader/MainActivity.kt` contains the UI logic and Python integration
- **UI Layout**: `app/src/main/res/layout/activity_main.xml` provides the user interface for input and download controls

### Python Functions
- `download(profile)`: Downloads all media from an Instagram profile
- `post_count(username)`: Returns the number of posts for a given username
- `download_post_from_link(shortcode)`: Downloads a single post/reel from its URL

### Android Features
- Supports downloading all media from a profile using username
- Supports downloading single posts/reels using URL
- Handles both Instagram post links (`/p/shortcode`) and reel links (`/reel/shortcode`)
- Manages Android storage permissions for external storage access

## Build and Development

### Prerequisites
- Android Studio
- Android SDK (compileSdk 33)
- Python 3.8 (used via Chaquopy)
- Internet connection for downloading dependencies

### Build System Configuration
- Gradle plugin `com.chaquo.python` version 14.0.2
- Python dependencies installed via pip (currently only `instaloader`)
- Python source directory: `src/main/python`
- Storage permissions managed for Android 11+ (API 30+)

### Building the Project
```bash
# Navigate to InstaLoaderApp directory
cd /home/ncx/Proyectos/INS33/InstaLoaderApp

# Build the project
./gradlew build

# Or install directly to a connected device
./gradlew installDebug
```

## Development Conventions
- Kotlin follows standard Android development practices
- Python code uses the instaloader library for Instagram data extraction
- Chaquopy handles the Python-Android integration
- UI uses Material Design components and ConstraintLayout
- Coroutines are used for background processing

## File Structure
```
InstaLoaderApp/
├── app/
│   ├── build.gradle (Module-level build configuration, includes Chaquopy and Python setup)
│   ├── src/main/
│   │   ├── java/com/alphacorp/instaloader/MainActivity.kt (Android frontend logic)
│   │   ├── python/script.py (Python backend for Instagram downloads)
│   │   └── AndroidManifest.xml (App permissions and activities)
│   └── res/layout/activity_main.xml (Main UI layout)
├── build.gradle (Project-level build configuration)
├── settings.gradle (Project module configuration)
├── gradle.properties (Gradle settings)
└── README.md (Project documentation)
```

## Key Features
- Download all media from a public Instagram profile by username
- Download single Instagram posts/reels by URL
- Automatic storage management with downloads saved to `Internal Storage/InstaLoaderApp/`
- Asynchronous downloading with status updates
- Permission handling for external storage access

## Storage Locations
- Profile downloads: `/sdcard/InstaLoaderApp/{username}/`
- Single post downloads: `/sdcard/InstaLoaderApp/posts/`

## Permissions
- INTERNET: Required for accessing Instagram
- ACCESS_NETWORK_STATE: For network status checks
- WRITE_EXTERNAL_STORAGE: For saving downloaded media
- READ_EXTERNAL_STORAGE: For reading stored media
- MANAGE_EXTERNAL_STORAGE: For managing external storage access on Android 11+

## Testing
- Unit tests can be added in the test directories
- Android tests can be written in the androidTest directories
- Manual testing required for Instagram integration due to API limitations

## External Dependencies
- instaloader (Python library for Instagram data extraction)
- AndroidX libraries (core Android components)
- Material Design (UI components)
- Chaquopy (Python-Android integration)