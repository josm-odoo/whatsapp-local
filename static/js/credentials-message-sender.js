async function setWhatsAppWebhookAccount1() {
            const tokenInput = document.querySelector('#whatsapp_webhook_token_account_1');
            try {
                const response = await fetch("/set-odoo-whatsapp-webhook-account-1", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        webhook_token: tokenInput.value
                    })
                });
                const data = await response.json();
                document.getElementById('mock_whatsapp_webhook_access_token_account_1').textContent = data.webhook_token;
            } catch (error) {
                console.error('Failed to refresh traffic log:', error);
            }
        };
        document.getElementById('webhook-account-1-btn').addEventListener('click', (e) => {
            e.preventDefault();
            setWhatsAppWebhookAccount1();
        });
async function setWhatsAppWebhookAccount2() {
            const tokenInput = document.querySelector('#whatsapp_webhook_token_account_2');
            try {
                const response = await fetch("/set-odoo-whatsapp-webhook-account-2", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        webhook_token: tokenInput.value
                    })
                });
                const data = await response.json();
                document.getElementById('mock_whatsapp_webhook_access_token_account_2').textContent = data.webhook_token;
            } catch (error) {
                console.error('Failed to refresh traffic log:', error);
            }
        };
        document.getElementById('webhook-account-2-btn').addEventListener('click', (e) => {
            e.preventDefault();
            setWhatsAppWebhookAccount2();
        });

    async function sendManualWebhookMessage(event) {
        console.log('Sending manual webhook message...');
        const numberInput = document.getElementById('number');
        const messageInput = document.getElementById('message');
        const parentMsgIdInput = document.getElementById('parent_msg_id');
        const accountTypeIdInput = document.getElementById('account_type');
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
                    parent_msg_id: parentMsgIdInput.value,
                    account_type: accountTypeIdInput.value
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