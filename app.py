"""Simple Flask web app entrypoint for deployment."""

import os
from flask import Flask, send_file, render_template_string

app = Flask(__name__)

PORTFOLIO_HTML = os.path.join(os.path.dirname(__file__), "portfolio.html")

@app.route("/")
def index():
    """Serve the generated portfolio page."""
    if os.path.exists(PORTFOLIO_HTML):
        return send_file(PORTFOLIO_HTML)
    return render_template_string(
        "<h1>Portfolio not found</h1><p>Generate portfolio.html using generate_cv_portfolio.py.</p>"
    ), 404

@app.route("/status")
def status():
    """Simple health check endpoint."""
    return {"status": "ok", "app": "Recruitment Pipeline Portfolio"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
