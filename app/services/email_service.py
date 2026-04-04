import httpx
import logging
import os
from ..config import settings

logger = logging.getLogger("portfolio-email")

async def send_auto_reply(email: str, name: str, phone: str = "", query: str = ""):
    """
    Sends an automated "Thank You" email via EmailJS API.
    Replicates the logic from Node's utils/emailjs.js.
    """
    public_key = os.getenv("EMAILJS_PUBLIC_KEY")
    private_key = os.getenv("EMAILJS_PRIVATE_KEY")
    service_id = os.getenv("EMAILJS_SERVICE_ID")
    template_id = os.getenv("EMAILJS_TEMPLATE_ID")

    if not all([public_key, private_key, service_id, template_id]):
        logger.info("Skipping auto-reply: EmailJS credentials not fully configured in env.")
        return

    logger.info(f"✉️ Sending EmailJS auto-reply to: {name} ({email})")

    payload = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": public_key,
        "accessToken": private_key,
        "template_params": {
            "to_name": name,
            "to_email": email
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.emailjs.com/api/v1.0/email/send",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Auto-reply sent successfully via EmailJS to {email}")
            else:
                logger.error(f"❌ EmailJS Error: {response.text}")
                
    except Exception as e:
        logger.error(f"❌ Error hitting EmailJS API: {str(e)}")
