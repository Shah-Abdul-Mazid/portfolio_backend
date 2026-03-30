// EmailJS API Helper
export const sendAutoReply = async (email, name, req_phone, req_query) => {
    const publicKey = process.env.EMAILJS_PUBLIC_KEY;
    const privateKey = process.env.EMAILJS_PRIVATE_KEY;
    const serviceId = process.env.EMAILJS_SERVICE_ID;
    const templateId = process.env.EMAILJS_TEMPLATE_ID;

    if (!publicKey || !serviceId || !templateId) {
        console.log('Skipping auto-reply: EmailJS credentials not fully configured in env.');
        return;
    }

    console.log(`✉️ Sending EmailJS auto-reply to: ${name} (${email})`);

    try {
        const response = await fetch('https://api.emailjs.com/api/v1.0/email/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                service_id: serviceId,
                template_id: templateId,
                user_id: publicKey,
                accessToken: privateKey,
                template_params: {
                    to_name: name,
                    to_email: email
                }
            })
        });

        if (response.ok) {
            console.log(`✅ Auto-reply sent successfully via EmailJS to ${email}`);
        } else {
            const errText = await response.text();
            console.error('❌ EmailJS Error:', errText);
        }
    } catch (error) {
        console.error('❌ Error hitting EmailJS API:', error);
    }
};
