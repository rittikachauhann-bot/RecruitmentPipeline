# 🚀 CV Web Portfolio Deployment Guide

This guide explains how to deploy your interactive CV web page to **https://ritika-cv.vercel.app** (or your preferred URL) for sharing with recruiters.

## 📝 Overview

Your recruitment pipeline now includes an **interactive web portfolio** that you can share with recruiters via email. When you send outreach emails, they'll include a link to your portfolio in the footer/signature.

**Portfolio URL**: `https://ritika-cv.vercel.app`

---

## 🎨 Step 1: Create Your CV Web Page

### Option A: Using Python Generator (Recommended)

Create a Flask app that generates your CV page dynamically:

```bash
# Generate a sample CV web page
mkdir -p portfolio
cd portfolio

# Create index.html with your CV content
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ritika Chouhan - Portfolio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }
        
        header {
            background: white;
            padding: 40px 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideDown 0.6s ease-out;
        }
        
        header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header p {
            color: #666;
            font-size: 1.1em;
            margin-bottom: 20px;
        }
        
        .contact-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .contact-links a {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        
        .contact-links a:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        main {
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        section {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: fadeIn 0.8s ease-out;
        }
        
        section h2 {
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .experience-item {
            padding: 15px 0;
            border-left: 4px solid #667eea;
            padding-left: 15px;
            margin-bottom: 15px;
        }
        
        .experience-item h3 {
            color: #333;
            font-size: 1.1em;
        }
        
        .experience-item .company {
            color: #667eea;
            font-weight: 600;
        }
        
        .skills {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .skill-tag {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            text-align: center;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .skill-tag:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        footer {
            background: #333;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @media (max-width: 768px) {
            header h1 { font-size: 1.8em; }
            section { padding: 20px; }
            .skills { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <header>
        <h1>Ritika Chouhan</h1>
        <p>AI Strategy | Digital Transformation | Enterprise Cloud</p>
        <div class="contact-links">
            <a href="mailto:riti.iiit@gmail.com">📧 Email</a>
            <a href="https://linkedin.com/in/ritikachouhan">🔗 LinkedIn</a>
            <a href="tel:+917042656887">📱 +91-7042656887</a>
        </div>
    </header>
    
    <main>
        <section>
            <h2>About</h2>
            <p>Director-level professional with 10+ years in AI Strategy, Digital Transformation, and Enterprise Cloud solutions. Experienced in leading cross-functional teams and driving business transformation for Fortune 500 organizations.</p>
        </section>
        
        <section>
            <h2>Experience</h2>
            <div class="experience-item">
                <h3>Director – AI Strategy</h3>
                <p class="company">Leading Organization (2023-Present)</p>
                <p>Spearheaded AI transformation initiatives, resulting in 40% efficiency gains. Led team of 15+ professionals across multiple verticals.</p>
            </div>
            <div class="experience-item">
                <h3>Senior Consultant – Digital Transformation</h3>
                <p class="company">Global Consulting Firm (2020-2023)</p>
                <p>Delivered enterprise cloud migration projects for BFSI clients with >$50M in value creation.</p>
            </div>
        </section>
        
        <section>
            <h2>Skills</h2>
            <div class="skills">
                <div class="skill-tag">AI Strategy</div>
                <div class="skill-tag">Cloud Architecture</div>
                <div class="skill-tag">Digital Transformation</div>
                <div class="skill-tag">Leadership</div>
                <div class="skill-tag">Enterprise Solutions</div>
                <div class="skill-tag">Data Analytics</div>
                <div class="skill-tag">Project Management</div>
                <div class="skill-tag">BFSI Domain</div>
            </div>
        </section>
        
        <section>
            <h2>Education</h2>
            <div class="experience-item">
                <h3>Advanced Certification in AI & ML</h3>
                <p class="company">Industry Leading Institute</p>
            </div>
            <div class="experience-item">
                <h3>B.Tech in Computer Science</h3>
                <p class="company">IIIT Hyderabad</p>
            </div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2026 Ritika Chouhan. All rights reserved.</p>
    </footer>
</body>
</html>
EOF
```

---

## 🚀 Step 2: Deploy to Vercel (Recommended - Free & Easy)

### Option 1: Deploy via GitHub Pages

```bash
# 1. Create a GitHub repository
# Visit github.com and create a new repo: ritika-cv

# 2. Push your portfolio folder
git init
git add .
git commit -m "Initial CV portfolio"
git branch -M main
git remote add origin https://github.com/USERNAME/ritika-cv.git
git push -u origin main

# 3. Enable GitHub Pages
# Go to Settings → Pages → Select 'main' branch → Save

# Your site will be available at: https://USERNAME.github.io/ritika-cv
```

### Option 2: Deploy via Vercel (Easiest)

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy from portfolio directory
cd portfolio
vercel

# 3. Follow prompts to link your account and deploy

# Your site will be available at: https://ritika-cv.vercel.app (or custom domain)
```

### Option 3: Deploy via Netlify

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Deploy
cd portfolio
netlify deploy --prod

# Your site will be available at a Netlify URL
```

---

## 📋 Step 3: Update Configuration

Update `config.py` with your portfolio URL:

```python
CANDIDATE = {
    "name": "Ritika Chouhan",
    "email": "riti.iiit@gmail.com",
    "phone": "+91-7042656887",
    "linkedin": "https://linkedin.com/in/ritikachouhan",
    "portfolio_url": "https://ritika-cv.vercel.app",  # ← Update this with your deployed URL
    "notice_period": "60 days",
    "cv_path": os.path.expanduser("~/Downloads/Ritika_Chouhan_CV_Global_1.docx"),
}
```

---

## ✉️ Step 4: Send Emails with Portfolio Link

The portfolio link is now automatically included in all outreach emails:

### From Python:

```python
from gmail_sender import send_email

# Send email with automatic portfolio link in footer
send_email(
    to="recruiter@company.com",
    subject="Application for Senior Director Role",
    body="""Hi Hiring Manager,

I'm interested in the Senior Director position at your organization...

Best regards""",
    attach_cv=True,
    include_signature=True,  # Automatically adds portfolio link
    use_html=False
)
```

### Using Email Templates:

```python
from email_templates import render_template, OUTREACH_TEMPLATE
from gmail_sender import send_email

body = render_template(OUTREACH_TEMPLATE,
    recruiter_name="John Smith",
    role="Director – AI Strategy",
    company="Deloitte",
    relevant_skills="AI strategy, digital transformation, enterprise cloud",
    portfolio_url="https://ritika-cv.vercel.app",
    candidate_name="Ritika Chouhan"
)

send_email(
    to="john.smith@deloitte.com",
    subject="Director – AI Strategy Position",
    body=body,
    include_signature=True
)
```

---

## 📧 Email Footer Preview

When you send emails, recruiters will see a professional footer like:

```
---
Ritika Chouhan
riti.iiit@gmail.com | +91-7042656887

💼 Portfolio: https://ritika-cv.vercel.app
🔗 LinkedIn: https://linkedin.com/in/ritikachouhan

View my web portfolio to explore my projects, skills, and experience.
```

With HTML emails, it includes an attractive button to click directly to your portfolio.

---

## 🎨 Step 5: Customize Your Portfolio

Edit `index.html` to include:
- ✅ Your actual work experience
- ✅ Real projects and case studies
- ✅ Testimonials from colleagues
- ✅ Blog posts or articles (optional)
- ✅ Custom color scheme
- ✅ Use the CV Web Designer Agent to create an even more elaborate version

---

## 🔗 Connecting with Your Pipeline

Your pipeline will automatically include the portfolio link when:

1. **Drafting outreach emails** (`python pipeline_cli.py apply <ref_id>`)
2. **Sending follow-up emails** (`python pipeline_cli.py followup`)
3. **Any manual `send_email()` call** with `include_signature=True`

---

## 📊 Analytics (Optional)

Add Google Analytics to track recruiter visits:

```html
<!-- Add to <head> in index.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=UA-XXXXXXXX-X"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'UA-XXXXXXXX-X');
</script>
```

---

## ✅ Checklist

- [ ] Created portfolio folder with `index.html`
- [ ] Deployed to Vercel/GitHub Pages/Netlify
- [ ] Updated `config.py` with portfolio URL
- [ ] Tested email signature in `gmail_sender.py`
- [ ] Added Google Analytics (optional)
- [ ] Customized content with your information
- [ ] Shared portfolio URL with recruiters
- [ ] Monitored analytics for recruiter visits

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Portfolio not showing | Check source URL in `config.py` |
| Link broken in emails | Verify URL is correct and deployed |
| Footer not appearing | Ensure `include_signature=True` in `send_email()` |
| HTML formatting issues | Use `use_html=False` for plain text emails |
| Deploy failed | Check Vercel CLI installation and GitHub token |

---

## 📚 Related Files

- `config.py` - Portfolio URL configuration
- `gmail_sender.py` - Email sending with signature
- `email_templates.py` - Email templates with footer
- `.github/agents/cv-web-designer.agent.md` - Create more elaborate CV pages

---

Happy recruiting! 🚀
