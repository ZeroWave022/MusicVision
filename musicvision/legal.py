from flask import Blueprint, render_template

legal_bp = Blueprint("legal", __name__, url_prefix="/legal")


@legal_bp.route("/terms-of-service")
def terms():
    return render_template("legal/terms-of-service.html")


@legal_bp.route("/privacy-policy")
def privacy():
    return render_template("legal/privacy-policy.html")
