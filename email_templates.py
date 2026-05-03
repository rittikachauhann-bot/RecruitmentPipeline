"""Email templates and signature builders for recruiting communications."""

from config import CANDIDATE


def get_email_signature_html() -> str:
    """Return HTML email signature with portfolio link."""
    return f"""
<div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #555;">
  <p style="margin: 8px 0; font-size: 13px; font-weight: 600; color: #000;">
    {CANDIDATE['name']}
  </p>
  <p style="margin: 4px 0;">
    <a href="mailto:{CANDIDATE['email']}" style="color: #1a73e8; text-decoration: none;">{CANDIDATE['email']}</a> | 
    <a href="tel:{CANDIDATE['phone'].replace('-', '')}" style="color: #1a73e8; text-decoration: none;">{CANDIDATE['phone']}</a>
  </p>
  <p style="margin: 8px 0;">
    <a href="{CANDIDATE['portfolio_url']}" style="display: inline-block; padding: 8px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 4px; font-weight: 600; font-size: 12px;">
      💼 View My Portfolio
    </a>
  </p>
  <p style="margin: 8px 0;">
    <a href="https://{CANDIDATE['linkedin']}" style="color: #0077b5; text-decoration: none; margin-right: 12px;">🔗 LinkedIn</a>
    <a href="https://github.com" style="color: #333; text-decoration: none;">🐙 GitHub</a>
  </p>
  <p style="margin: 12px 0 0 0; font-size: 11px; color: #999;">
    Open <a href="{CANDIDATE['portfolio_url']}" style="color: #1a73e8; text-decoration: none;">my web portfolio</a> to explore my projects, skills, and experience.
  </p>
</div>
"""


def get_email_signature_plain() -> str:
    """Return plain text email signature."""
    return f"""
---
{CANDIDATE['name']}
{CANDIDATE['email']} | {CANDIDATE['phone']}

💼 Portfolio: {CANDIDATE['portfolio_url']}
🔗 LinkedIn: https://{CANDIDATE['linkedin']}

View my web portfolio to explore my projects, skills, and experience.
"""


def format_body_with_signature(body: str, use_html: bool = False) -> str:
    """Append signature to email body."""
    if use_html:
        return f"{body}{get_email_signature_html()}"
    else:
        return f"{body}\n{get_email_signature_plain()}"


def get_footer_banner() -> str:
    """Return HTML footer banner for bulk emails."""
    return f"""
<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 24px 0;">
<table width="100%" cellpadding="12" style="background: #f5f5f5; border-radius: 8px; font-family: Arial, sans-serif;">
  <tr>
    <td>
      <p style="margin: 8px 0; font-size: 12px; color: #666;">
        <strong>Interested in connecting?</strong> Check out my interactive portfolio:
      </p>
      <p style="margin: 12px 0;">
        <a href="{CANDIDATE['portfolio_url']}" style="display: inline-block; padding: 10px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 13px;">
          ✨ View Interactive Portfolio
        </a>
      </p>
      <p style="margin: 8px 0; font-size: 11px; color: #999;">
        Designed to showcase my projects, work experience, and skills in an interactive way.
      </p>
    </td>
  </tr>
</table>
"""


# Email templates for different scenarios

OUTREACH_TEMPLATE = """Hi {recruiter_name},

I'm reaching out regarding the {role} position at {company}. 

With my background in {relevant_skills}, I'm confident I can make a meaningful impact on your team.

I've attached my CV for your review. For a more interactive view of my projects and experience, please visit my portfolio:

{portfolio_url}

I'd love to discuss how I can contribute to your organization.

Best regards,
{candidate_name}"""


FOLLOWUP_TEMPLATE = """Hi {recruiter_name},

I wanted to follow up on my previous application for the {role} position at {company}.

I remain very interested in this opportunity and would welcome the chance to discuss my qualifications further. 

My portfolio provides an interactive view of my work and experience:
{portfolio_url}

Thank you for considering my application.

Best regards,
{candidate_name}"""


THANK_YOU_TEMPLATE = """Hi {recruiter_name},

Thank you for taking the time to meet with me today. It was great to discuss the {role} opportunity at {company}.

I'm excited about the possibility of joining your team. For your reference, here's my interactive portfolio with my full work experience:

{portfolio_url}

Please let me know if you need any additional information.

Best regards,
{candidate_name}"""


def render_template(template: str, **kwargs) -> str:
    """Render template with provided variables."""
    return template.format(**kwargs)
