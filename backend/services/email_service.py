"""Resend email service."""
import os
import asyncio
import logging
import resend

logger = logging.getLogger(__name__)

resend.api_key = os.environ.get("RESEND_API_KEY")
SENDER = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")


async def send_email(to_email: str, subject: str, html: str) -> bool:
    """Send email asynchronously. Returns True on success, False on failure (logged)."""
    if not resend.api_key:
        logger.warning("Resend not configured; skipping email")
        return False
    try:
        params = {"from": SENDER, "to": [to_email], "subject": subject, "html": html}
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {result.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Email send failed to {to_email}: {e}")
        return False


def render_welcome(name: str) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1C1B1A;">
      <h1 style="color:#1E3A2F;font-size:24px;">Welcome to Golf For Good, {name}!</h1>
      <p>You're part of a community that plays for a purpose. Track your scores, support your chosen charity, and participate in our monthly draws.</p>
      <p style="margin-top:24px;"><a href="#" style="background:#D95D39;color:white;padding:12px 24px;border-radius:32px;text-decoration:none;font-weight:600;">Go to Dashboard</a></p>
    </div>
    """


def render_winner(name: str, tier: str, amount: float) -> str:
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1C1B1A;">
      <h1 style="color:#D95D39;font-size:28px;">Congratulations, {name}!</h1>
      <p>You've won in the <strong>{tier}</strong> tier of this month's draw.</p>
      <p style="font-size:20px;">Prize amount: <strong>${amount:.2f}</strong></p>
      <p>Please submit your score screenshot in the dashboard to claim your payout.</p>
    </div>
    """


def render_draw_result(name: str, month: str, numbers: list) -> str:
    nums = ", ".join(str(n) for n in numbers)
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1C1B1A;">
      <h1 style="color:#1E3A2F;">This month's numbers are in</h1>
      <p>Hi {name}, the {month} draw is complete.</p>
      <p style="font-size:20px;">Winning numbers: <strong>{nums}</strong></p>
      <p>Check your dashboard to see if you matched.</p>
    </div>
    """
