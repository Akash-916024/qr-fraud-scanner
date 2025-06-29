from bson.objectid import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.json_util import dumps
import os

admin_bp = Blueprint('admin', __name__)

# MongoDB setup
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["qr_scanner"]
collection = db["scam_reports"]

def get_db_usage_mb():
    try:
        stats = db.command("dbstats")
        used_bytes = stats.get("dataSize", 0)
        return used_bytes / (1024 * 1024)  # Convert to MB
    except Exception as e:
        print("DB stats error:", e)
        return 0

# Secure credentials from environment
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('admin_login.html')

@admin_bp.route('/admin/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    reports = list(collection.find().sort([("reported_at", -1)]))
    db_usage = get_db_usage_mb()
    limit = 512
    percent = (db_usage / limit) * 100

    alert = None
    if percent >= 80:
        alert = f"🚨 Warning: Database usage is at {percent:.1f}% of the free 512MB limit."

    return render_template('admin_dashboard.html', reports=reports, alert=alert)

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


@admin_bp.route('/admin/delete/<id>')
def delete_report(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    try:
        collection.delete_one({'_id': ObjectId(id)})  
        flash("✅ Report deleted", "success")
    except Exception as e:
        flash(f"❌ Deletion failed: {e}", "danger")

    return redirect(url_for('admin.dashboard'))
    
from datetime import datetime

@admin_bp.route('/admin/delete_all')
def delete_all_reports():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    collection.delete_many({})
    flash("🗑️ All reports deleted!", "success")
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/delete_oldest')
def delete_oldest_reports():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    oldest = collection.find().sort("reported_at", 1).limit(10)
    ids = [r["_id"] for r in oldest]
    collection.delete_many({"_id": {"$in": ids}})
    flash("🧓 Oldest 10 reports deleted.", "success")
    return redirect(url_for('admin.dashboard'))
