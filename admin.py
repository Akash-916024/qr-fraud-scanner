from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os

admin_bp = Blueprint('admin', __name__)

# MongoDB setup
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["qr_scanner"]
collection = db["scam_reports"]

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
    reports = list(collection.find().sort("reported_at", -1))
    return render_template('admin_dashboard.html', reports=reports)

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/admin/delete/<id>')
def delete_report(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    collection.delete_one({'_id': id})
    flash("Report deleted", "success")
    return redirect(url_for('admin.dashboard'))
