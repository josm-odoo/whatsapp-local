 async function setWhatsAppWebhook() {
            const tokenInput = document.querySelector('#whatsapp_webhook_token');
            try {
                const response = await fetch("/set-odoo-whatsapp-webhook", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        webhook_token: tokenInput.value
                    })
                });
                const data = await response.json();
                document.getElementById('mock_whatsapp_webhook_access_token').textContent = data.webhook_token;
            } catch (error) {
                console.error('Failed to refresh traffic log:', error);
            }
        };
        document.getElementById('webhook-btn').addEventListener('click', (e) => {
            e.preventDefault();
            setWhatsAppWebhook();
        });

    async function sendManualWebhookMessage(event) {
        console.log('Sending manual webhook message...');
        const numberInput = document.getElementById('number');
        const messageInput = document.getElementById('message');
        const parentMsgIdInput = document.getElementById('parent_msg_id');
        try {
            const response = await fetch("/send-manual-webhook-message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    from_phone_number: numberInput.value,
                    message: messageInput.value,
                    type: 'text',
                    manualSend: true,
                    parent_msg_id: parentMsgIdInput.value
                })
            });
            const data = await response.json();
            alert('Message sent successfully!');
            numberInput.value = '';
            messageInput.value = '';
        } catch (error) {
            console.error('Failed to send manual webhook message:', error);
        }
    };
    document.getElementById('message-submit').addEventListener('click', (e) => {
        e.preventDefault();
        sendManualWebhookMessage(e);
    });