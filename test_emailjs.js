import dotenv from 'dotenv';
dotenv.config();

async function testEmailJS() {
    const publicKey = process.env.EMAILJS_PUBLIC_KEY;
    const privateKey = process.env.EMAILJS_PRIVATE_KEY;
    const serviceId = process.env.EMAILJS_SERVICE_ID;
    const templateId = process.env.EMAILJS_TEMPLATE_ID;

    console.log(`Testing EmailJS with Service ID: ${serviceId}, Template ID: ${templateId}`);

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
                    to_name: "Test User",
                    to_email: "test@example.com"
                }
            })
        });

        if (response.ok) {
            console.log(`✅ Success! Auto-reply email was accepted by EmailJS API.`);
        } else {
            const errText = await response.text();
            console.error(`❌ EmailJS API Error (${response.status}):`, errText);
        }
    } catch (error) {
        console.error('❌ Network Error hitting EmailJS API:', error);
    }
}

testEmailJS();
