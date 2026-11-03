import logging
from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from ..models import Business, Email

logger = logging.getLogger('autobiz')


class OutreachAgent:
    """Sends personalized outreach emails with demo links to business owners."""

    def send_outreach(self, business_id: int, demo_urls: list[str]) -> bool:
        business = Business.objects.filter(pk=business_id).first()
        if not business or not business.email:
            logger.warning('[OutreachAgent] No email for business #%s', business_id)
            if business:
                self._log_email(business, '', '', demo_urls, Email.SentStatus.FAILED, 'No recipient email address')
            return False

        subject = f'We built a FREE website for {business.name} 🚀'
        body = self._build_email_body(business, demo_urls)

        error = None
        try:
            msg = EmailMultiAlternatives(subject, '', settings.DEFAULT_FROM_EMAIL, [business.email])
            msg.attach_alternative(body, 'text/html')
            sent = msg.send() > 0
        except Exception as e:  # SMTP errors surface as many exception types
            sent, error = False, str(e)

        self._log_email(
            business, business.email, body, demo_urls,
            Email.SentStatus.SENT if sent else Email.SentStatus.FAILED, error,
        )

        if sent:
            business.status = Business.Status.CONTACTED
            business.save(update_fields=['status', 'updated_at'])
            logger.info('[OutreachAgent] Email sent to %s', business.email)
        else:
            logger.error('[OutreachAgent] Email to %s failed: %s', business.email, error)

        return sent

    @staticmethod
    def _build_email_body(business: Business, demo_urls: list[str]) -> str:
        name = escape(business.name)
        links = ''.join(
            f'<li><a href="{escape(url)}">Design #{i} — View Demo</a></li>\n'
            for i, url in enumerate(demo_urls, start=1)
        )
        reply_to = escape(settings.OUTREACH_FROM_EMAIL or '')

        return f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
  <h2 style="color: #e44d26;">Hi {name} Team! 👋</h2>

  <p>We noticed that <strong>{name}</strong> doesn't have a website yet — so we built <strong>{len(demo_urls)} FREE website designs</strong> for you to check out!</p>

  <p>Here are your demo links:</p>
  <ul>
    {links}
  </ul>

  <p>These are fully responsive, professionally designed pages — ready to go live within 24 hours if you're interested.</p>

  <p>
    <strong>Why does this matter?</strong><br>
    80% of customers search online before visiting a business. A website can increase your bookings and visibility significantly.
  </p>

  <p>
    <a href="mailto:{reply_to}" style="background:#e44d26;color:#fff;padding:12px 24px;text-decoration:none;border-radius:5px;display:inline-block;margin-top:10px;">
      Yes, I'm Interested! →
    </a>
  </p>

  <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
  <p style="font-size:12px;color:#999;">
    AutoBiz AI · Automated Business Websites<br>
    To unsubscribe, reply with "unsubscribe".
  </p>
</body>
</html>"""

    @staticmethod
    def _log_email(business, to_email, body, demo_urls, status, error):
        Email.objects.create(
            business=business,
            to_email=to_email,
            subject=f'We built a FREE website for {business.name}',
            body=body,
            demo_links='\n'.join(demo_urls),
            sent_status=status,
            error_msg=error,
            sent_at=timezone.now() if status == Email.SentStatus.SENT else None,
        )
