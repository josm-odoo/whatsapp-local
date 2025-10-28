// Main JavaScript for WhatsApp Dashboard

// Handle form submission
// Uncomment when ready to use
/*
document.addEventListener('DOMContentLoaded', function() {
    const sendMessageForm = document.getElementById('sendMessageForm');

    if (sendMessageForm) {
        sendMessageForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const statusDiv = document.getElementById('sendStatus');
            const submitBtn = e.target.querySelector('button[type="submit"]');

            // Disable button and show loading
            submitBtn.disabled = true;
            submitBtn.textContent = '⏳ Sending...';

            const formData = {
                webhook_url: document.getElementById('webhookUrl').value,
                from_number: document.getElementById('fromNumber').value,
                message_text: document.getElementById('messageText').value,
            };

            try {
                const response = await fetch('/api/send-manual-message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    statusDiv.style.display = 'block';
                    statusDiv.style.background = '#C8E6C9';
                    statusDiv.style.color = '#2E7D32';
                    statusDiv.textContent = '✅ Message sent successfully!';
                } else {
                    statusDiv.style.display = 'block';
                    statusDiv.style.background = '#FFCDD2';
                    statusDiv.style.color = '#C62828';
                    statusDiv.textContent = '❌ Failed to send: ' + (result.error || 'Unknown error');
                }
            } catch (error) {
                statusDiv.style.display = 'block';
                statusDiv.style.background = '#FFCDD2';
                statusDiv.style.color = '#C62828';
                statusDiv.textContent = '❌ Error: ' + error.message;
            }

            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = '📤 Send Message to Webhook';

            // Hide status after 5 seconds
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        });
    }

    // Save form values to localStorage (only message details, not credentials)
    const formInputs = ['webhookUrl', 'fromNumber', 'messageText'];

    // Restore saved values on page load
    formInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            const savedValue = localStorage.getItem(id);
            if (savedValue) {
                element.value = savedValue;
            }

            // Save values as user types
            element.addEventListener('input', (e) => {
                localStorage.setItem(id, e.target.value);
            });
        }
    });
});

// Auto-refresh traffic log
async function refreshTrafficLog() {
    try {
        const response = await fetch('/');
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Update only the stats and request cards
        const newStats = doc.querySelector('.stats');
        if (newStats) {
            const currentStats = document.querySelector('.stats');
            if (currentStats) {
                currentStats.innerHTML = newStats.innerHTML;
            }
        }
    } catch (error) {
        console.error('Failed to refresh traffic log:', error);
    }

    setTimeout(refreshTrafficLog, 10000);
}

// Start auto-refresh after 10 seconds
// Uncomment when ready to use
// setTimeout(refreshTrafficLog, 10000);
*/
