async function loadTemplate(url) {
    const response = await fetch(url);
    return await response.text();
}
async function loadTemplatesJsonFile() {
        try {
            const response = await fetch("/message-templates");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error("Error loading JSON file:", error);
        }
    }
async function refreshTrafficLog() {

    const template = await loadTemplate("templates/message-card.html");
    try {
        const response = await fetch("/traffic-logs");
        const data = await response.json();


        const container = document.getElementById('traffic-logs');
        container.innerHTML = "";
        for (const log of data) {
            const div = document.createElement('div');
            div.className = 'request-card';
            const methodClass = `method-${log.method}`;
            let messageHTML = '';
            const body = JSON.parse(log.body) || {};
            if (body.type === 'template') {
                const template_message = await loadTemplate("templates/template-message.html");
                const template_json = await loadTemplatesJsonFile();
                const current_templates = {};
                for (const template of template_json) {
                    if (template.name === body.template.name) {
                        current_templates[template.name] = template;
                    }
                }
                const current_template = current_templates?.[body.template.name];
                messageHTML = template_message
                .replace("{{body_type}}", body.type)
                .replace("{{body_template_name}}", body.template.name)
                .replace("{{body_language}}", body.template.language.code)
                .replace("{{body_template_body}}", current_template?.components[0]?.text || 'N/A')
                .replace("{{body_template_values}}", JSON.stringify(body.template.components[0]?.parameters || {}, null, 2));
                if (current_template?.components[0]?.example) {
                    let text_body = current_template.components[0].text;
                    const placeholders = current_template.components[0].example.body_text || [];

                   for (let i = 0; i < placeholders.length+1; i++) {
                    text_body = text_body.replace(`{{${i+1}}}`, body.template.components[0].parameters[i]?.text || `{{nothing to replace index ${i} with}}`);
            
                   }
                    messageHTML = messageHTML.replace("{{body_text_body}}", text_body);
                } else {
                    messageHTML = messageHTML.replace("{{body_text_body}}", current_template?.components[0]?.text || 'N/A');
                }
            } else if (body.type === 'text' && !body.manualSend) {
                const recieved_message = await loadTemplate("templates/recieved-message.html");       
                messageHTML = recieved_message
                .replace("{{body_type}}", "text -(Sent From Odoo)")
                .replace("{{body_to}}", body.to)
                .replace("{{body_text_body}}", body.text.body);
            } else if (body.manualSend) {           
                const manual_send_message = await loadTemplate("templates/manual-send-message.html");
                messageHTML = manual_send_message
                .replace("{{body_type}}", "text -(Manual Send from Whatsapp test tool)")
                .replace("{{body_message}}", body.message);
            }
            else {
                messageHTML = `<div class="message-unknown">Unknown message format</div>`;
            }



            div.innerHTML = template
                .replace("{{timestamp}}", log.timestamp)
                .replace("{{host}}", log.host)
                .replace("{{path}}", log.path)
                .replace("{{methodClass}}", methodClass)
                .replace("{{method}}", log.method)
                .replace("{{messageHTML}}", messageHTML);

            container.appendChild(div);
        }


    } catch (error) {
        console.error('Failed to refresh traffic log:', error);
    }

    setTimeout(refreshTrafficLog, 1000);
}

    // Start auto-refresh after 1 second
setTimeout(refreshTrafficLog, 1000);