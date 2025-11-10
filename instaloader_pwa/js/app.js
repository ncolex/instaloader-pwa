// instaloader_pwa/js/app.js
class InstaLoaderPWA {
    constructor() {
        this.apiBaseUrl = ''; // API endpoint is relative
        this.jobId = null;
        this.pollInterval = null;
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.targetInput = document.getElementById('targetInput');
        this.downloadProfileBtn = document.getElementById('downloadProfileBtn');
        this.downloadPostBtn = document.getElementById('downloadPostBtn');
        this.autoDownloadBtn = document.getElementById('autoDownloadBtn');
        this.statusSection = document.getElementById('statusSection');
        this.statusText = document.getElementById('statusText');
        this.progressBar = document.getElementById('progress');
        this.resultsSection = document.getElementById('resultsSection');
        this.resultsContent = document.getElementById('resultsContent');
        this.profileInfo = document.getElementById('profileInfo');
        this.profileContent = document.getElementById('profileContent');
        this.previewSection = document.getElementById('previewSection');
        this.previewContent = document.getElementById('previewContent');
        
        // Create and add cancel button
        this.cancelButton = document.createElement('button');
        this.cancelButton.id = 'cancelDownloadBtn';
        this.cancelButton.textContent = 'Cancel';
        this.cancelButton.className = 'btn';
        this.cancelButton.style.display = 'none';
        this.cancelButton.style.marginLeft = '10px';
        this.cancelButton.addEventListener('click', () => this.cancelDownload());
        
        // Add the cancel button next to the download buttons
        const buttonGroup = document.querySelector('.button-group');
        buttonGroup.appendChild(this.cancelButton);
    }

    bindEvents() {
        this.downloadProfileBtn.addEventListener('click', () => this.download('profile'));
        this.downloadPostBtn.addEventListener('click', () => this.download('post'));
        this.autoDownloadBtn.addEventListener('click', () => this.download('auto'));

        this.targetInput.addEventListener('input', (e) => {
            const value = e.target.value.trim();
            if (value && !value.startsWith('http')) {
                this.showProfileInfo(value);
            } else {
                this.profileInfo.style.display = 'none';
            }
            
            // Clear preview when input changes
            if (!value) {
                this.previewSection.style.display = 'none';
            }
        });
    }

    async download(downloadType) {
        const target = this.targetInput.value.trim();
        if (!target) {
            alert('Please enter a username or URL');
            return;
        }

        // Show download preview
        await this.showDownloadPreview(target, downloadType);

        this.setButtonsDisabled(true);
        this.statusSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.updateProgress(0);

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target, download_type: downloadType }),
                cache: 'no-cache'
            });

            if (!response.ok) throw new Error(`API error: ${response.status}`);

            const data = await response.json();
            this.jobId = data.job_id; // Store job ID for potential cancellation
            await this.pollForStatus(this.jobId);
        } catch (error) {
            this.updateStatus(`Error: ${error.message}`, 'error');
            this.setButtonsDisabled(false);
        }
    }

    async pollForStatus(jobId) {
        const maxAttempts = 120; // Increased for longer downloads
        let attempts = 0;

        this.pollInterval = setInterval(async () => {
            if (attempts >= maxAttempts) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
                this.updateStatus('Download timed out', 'error');
                this.setButtonsDisabled(false);
                this.jobId = null;
                return;
            }

            try {
                const response = await fetch(`${this.apiBaseUrl}/api/status/${jobId}`, { cache: 'no-cache' });
                if (!response.ok) throw new Error(`Status check failed: ${response.status}`);

                const statusData = await response.json();
                this.updateStatus(statusData.progress || statusData.status);
                
                // Simple progress simulation while polling
                this.updateProgress((attempts / maxAttempts) * 50); // Poll status takes 50% of progress

                if (statusData.status === 'completed') {
                    clearInterval(this.pollInterval);
                    this.pollInterval = null;
                    this.jobId = null;
                    await this.handleDownloadComplete(statusData.result);
                    this.setButtonsDisabled(false);
                } else if (statusData.status === 'failed') {
                    clearInterval(this.pollInterval);
                    this.pollInterval = null;
                    this.jobId = null;
                    this.updateStatus(`Download failed: ${statusData.result?.error || 'Unknown error'}`, 'error');
                    this.setButtonsDisabled(false);
                }
            } catch (error) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
                this.jobId = null;
                this.updateStatus(`Error checking status: ${error.message}`, 'error');
                this.setButtonsDisabled(false);
            }
            attempts++;
        }, 2000);
    }

    updateStatus(message, type = 'info') {
        this.statusText.textContent = message;
        this.statusText.className = type;
    }

    updateProgress(percentage) {
        this.progressBar.style.width = `${percentage}%`;
    }

    setButtonsDisabled(disabled) {
        this.downloadProfileBtn.disabled = disabled;
        this.downloadPostBtn.disabled = disabled;
        this.autoDownloadBtn.disabled = disabled;
        
        // Show/hide cancel button based on whether download is active
        this.cancelButton.style.display = disabled ? 'inline-block' : 'none';
    }
    
    cancelDownload() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
        
        this.updateStatus('Download cancelled by user', 'info');
        this.setButtonsDisabled(false);
        this.jobId = null;
    }

    async handleDownloadComplete(result) {
        if (result.error) {
            this.updateStatus(`Failed: ${result.error}`, 'error');
            return;
        }

        const urls = result.media_urls;
        if (!urls || urls.length === 0) {
            this.updateStatus('No media found to download.', 'info');
            return;
        }

        this.updateStatus(`Found ${urls.length} files. Preparing to download and zip...`);
        const zip = new JSZip();
        let filesDownloaded = 0;

        // Use Promise.all to fetch all files in parallel
        await Promise.all(urls.map(async (url) => {
            try {
                // Using a CORS proxy for fetching from Instagram
                const response = await fetch(`https://cors-anywhere.herokuapp.com/${url}`);
                if (!response.ok) {
                    console.error(`Failed to fetch ${url}: ${response.statusText}`);
                    return; // Skip this file
                }
                const blob = await response.blob();
                const filename = new URL(url).pathname.split('/').pop();
                zip.file(filename, blob);
                
                filesDownloaded++;
                const progress = 50 + (filesDownloaded / urls.length) * 50; // Zipping takes the other 50%
                this.updateProgress(progress);
                this.updateStatus(`Downloading & Zipping: ${filesDownloaded} / ${urls.length}`);
            } catch (error) {
                console.error(`Error fetching ${url}:`, error);
            }
        }));

        if (filesDownloaded === 0) {
            this.updateStatus('Could not download any files. This might be a CORS issue.', 'error');
            this.resultsSection.style.display = 'block';
            this.resultsContent.innerHTML = `<p>Could not fetch files from Instagram. The server hosting the files might be blocking requests. Try opening the developer console (F12) to see the errors.</p>`;
            return;
        }

        this.updateStatus('Creating zip file...');
        const zipBlob = await zip.generateAsync({ type: 'blob' });

        this.updateStatus('Download ready!');
        this.resultsSection.style.display = 'block';
        const downloadUrl = URL.createObjectURL(zipBlob);
        const targetName = this.targetInput.value.trim().replace(/[^a-zA-Z0-9]/g, '_');
        
        this.resultsContent.innerHTML = `
            <p><strong>${filesDownloaded} files zipped successfully!</strong></p>
            <a href="${downloadUrl}" class="btn btn-primary" download="${targetName}_instaloader.zip">Download .zip File</a>
        `;
    }

    async showProfileInfo(username) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/profile-info/${username}`, { cache: 'no-cache' });
            if (!response.ok) {
                if (response.status !== 404) console.error(`Profile info error: ${response.status}`);
                return;
            }
            const profileData = await response.json();
            this.profileContent.innerHTML = `
                <ul>
                    <li><strong>Username:</strong> ${profileData.username}</li>
                    <li><strong>Full Name:</strong> ${profileData.full_name}</li>
                    <li><strong>Followers:</strong> ${profileData.followers.toLocaleString()}</li>
                    <li><strong>Posts:</strong> ${profileData.posts}</li>
                    <li><strong>Private:</strong> ${profileData.is_private ? 'Yes' : 'No'}</li>
                    ${profileData.biography ? `<li><strong>Biography:</strong> ${profileData.biography.substring(0, 100)}${profileData.biography.length > 100 ? '...' : ''}</li>` : ''}
                </ul>
            `;
            this.profileInfo.style.display = 'block';
        } catch (error) {
            console.error('Profile info fetch error:', error);
        }
    }

    async showDownloadPreview(target, downloadType) {
        try {
            // Show a preview of what will be downloaded
            const isProfile = downloadType === 'profile' || 
                             (downloadType === 'auto' && !target.includes('/p/') && !target.includes('/reel/'));
            
            if (isProfile) {
                // If it's a profile, get profile info to show as preview
                const username = target.startsWith('http') ? 
                    target.split('/').filter(part => part && part !== 'www.instagram.com')[0] : 
                    target;
                
                const response = await fetch(`${this.apiBaseUrl}/api/profile-info/${username}`, { cache: 'no-cache' });
                if (!response.ok) {
                    if (response.status !== 404) console.error(`Profile info error: ${response.status}`);
                    this.previewContent.innerHTML = `<p>Preview not available. Could be a private account or invalid username.</p>`;
                    this.previewSection.style.display = 'block';
                    return;
                }
                
                const profileData = await response.json();
                this.previewContent.innerHTML = `
                    <div class="preview-content">
                        <ul>
                            <li><strong>Type:</strong> Profile (${profileData.posts} posts)</li>
                            <li><strong>Username:</strong> ${profileData.username}</li>
                            <li><strong>Full Name:</strong> ${profileData.full_name}</li>
                            <li><strong>Followers:</strong> ${profileData.followers.toLocaleString()}</li>
                            <li><strong>Private:</strong> ${profileData.is_private ? 'Yes' : 'No'}</li>
                        </ul>
                    </div>
                `;
            } else {
                // For post downloads, just show target URL
                this.previewContent.innerHTML = `
                    <div class="preview-content">
                        <ul>
                            <li><strong>Type:</strong> Single Post/Reel</li>
                            <li><strong>URL:</strong> ${target}</li>
                        </ul>
                    </div>
                `;
            }
            this.previewSection.style.display = 'block';
        } catch (error) {
            console.error('Preview fetch error:', error);
            this.previewContent.innerHTML = `<p>Unable to generate preview.</p>`;
            this.previewSection.style.display = 'block';
        }
    }
}

// Unregister any existing service workers to ensure fresh fetches
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for (let registration of registrations) {
            registration.unregister();
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    new InstaLoaderPWA();
});