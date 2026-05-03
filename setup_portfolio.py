#!/usr/bin/env python3
"""
Quick setup script to deploy CV portfolio and integrate with pipeline.
Run this to quickly set up the portfolio link in your emails.
"""

import os
import subprocess
import sys
from config import CANDIDATE

print("=" * 60)
print("🚀 CV PORTFOLIO SETUP - Recruitment Pipeline Integration")
print("=" * 60)

# Step 1: Generate portfolio
print("\n1️⃣  Generating your interactive CV portfolio...")
result = subprocess.run(
    [sys.executable, "generate_cv_portfolio.py", "--output", "portfolio.html"],
    capture_output=True,
    text=True
)
print(result.stdout)

if os.path.exists("portfolio.html"):
    size = os.path.getsize("portfolio.html")
    print(f"✅ Portfolio generated: portfolio.html ({size:,} bytes)")
else:
    print("❌ Failed to generate portfolio")
    sys.exit(1)

# Step 2: Check config
print("\n2️⃣  Checking your configuration...")
print(f"   Name: {CANDIDATE.get('name')}")
print(f"   Email: {CANDIDATE.get('email')}")
print(f"   Phone: {CANDIDATE.get('phone')}")
print(f"   LinkedIn: {CANDIDATE.get('linkedin')}")
print(f"   Portfolio URL: {CANDIDATE.get('portfolio_url', '❌ Not set')}")

if not CANDIDATE.get('portfolio_url'):
    print("\n   ⚠️  Portfolio URL not configured!")
    print("   Update config.py with your deployed portfolio URL:")
    print('   CANDIDATE["portfolio_url"] = "https://your-portfolio-url.com"')

# Step 3: Test email integration
print("\n3️⃣  Testing email integration...")
try:
    from email_templates import get_email_signature_html, get_footer_banner
    print("✅ Email templates module loaded successfully")
    print("\n   Email signature preview (HTML):")
    print("   " + "─" * 50)
    sig_preview = get_email_signature_html()[:200]
    print(f"   {sig_preview}...")
except ImportError as e:
    print(f"❌ Error loading email templates: {e}")
    sys.exit(1)

# Step 4: Deployment instructions
print("\n4️⃣  Deployment instructions:")
print("   " + "─" * 50)
print("""
   Option A: Deploy to Vercel (Recommended - FREE & EASY)
   ────────────────────────────────────────────────────────
   1. Install Vercel CLI:
      $ npm install -g vercel
   
   2. Deploy:
      $ vercel
   
   3. Update config.py with the generated URL
   
   Option B: Deploy to GitHub Pages
   ───────────────────────────────────
   1. Create repository: github.com/new
   2. Push files:
      $ git init && git add . && git commit -m "Initial"
      $ git remote add origin https://github.com/YOU/cv.git
      $ git push -u origin main
   3. Enable Pages in Settings
   
   Option C: Use Netlify
   ─────────────────────
   1. Install: $ npm install -g netlify-cli
   2. Deploy: $ netlify deploy --prod portfolio.html
""")

# Step 5: Integration test
print("\n5️⃣  Integration with pipeline:")
print("   " + "─" * 50)
print("""
   When you send emails, the portfolio link is automatically added:
   
   From Python:
   ───────────
   from gmail_sender import send_email
   
   send_email(
       to="recruiter@company.com",
       subject="Application for Director Role",
       body="Hi, I'm interested in joining your team...",
       attach_cv=True,
       include_signature=True  # ← Portfolio link auto-added!
   )
   
   Using Pipeline CLI:
   ───────────────────
   $ python pipeline_cli.py apply <ref_id>
   # Portfolio link in footer automatically!
""")

# Step 6: Final checklist
print("\n6️⃣  Next steps checklist:")
print("   " + "─" * 50)
checklist = [
    ("Deploy portfolio.html to a hosting service", False),
    ("Update config.py with your portfolio URL", CANDIDATE.get('portfolio_url') is not None),
    ("Test email with include_signature=True", False),
    ("Share portfolio URL with recruiters", False),
    ("Monitor analytics for recruiter visits", False),
]

for i, (task, done) in enumerate(checklist, 1):
    status = "✅" if done else "⬜"
    print(f"   {status} {task}")

print("\n" + "=" * 60)
print("💡 Tip: Edit portfolio.html to customize it with your details!")
print("📚 Read CV_PORTFOLIO_DEPLOYMENT.md for detailed instructions")
print("=" * 60)
