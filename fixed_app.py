from flask import session
from admin import admin_bp
from flask import Flask, request, render_template
import os
from link_checker import check_link
from pyzbar.pyzbar import decode
from PIL import Image
from pymongo import MongoClient
import datetime

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["qr_scanner"]  # Your MongoDB DB name
collection = db["scam_reports"]  

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mysecret")
app.register_blueprint(admin_bp)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------- QR SCANNING LOGIC -----------
def scan_qr(image_path):
    try:
        image = Image.open(image_path)
        decoded = decode(image)
        if not decoded:
            return None
        first_code = decoded[0]
        if first_code.type == 'QRCODE':
            return first_code.data.decode('utf-8')
    except Exception as e:
        print("Error scanning QR:", e)
    return None

# ----------- HOME ROUTE (for render check) -----------
@app.route("/status")
def status():
    return "QR Fraud Scanner Running!"

# ----------- INDEX ROUTE: QR SCANNER -----------
@app.route('/scanner', methods=['GET', 'POST'])
def index():
    result = None
    status = None
    if request.method == 'POST':
        file = request.files.get('qr_image')
        if file and file.filename != '':
            try:
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)
                link = scan_qr(path)
                if link:
                    verdict, reason = check_link(link)
                    if verdict == "suspicious":
                        status = 'danger'
                        result = f'🚨 Suspicious Link: {link} — {reason}'
                    elif verdict == "unknown":
                        status = 'warning'
                        result = f'⚠️ Unknown Link: {link} — {reason}'
                    else:
                        status = 'success'
                        result = f'✅ Safe Link: {link}'
                else:
                    status = 'warning'
                    result = '❌ No QR code detected.'
            except Exception as e:
                print("File upload or scan error:", e)
                status = 'danger'
                result = '⚠️ An error occurred while processing the image.'
    return render_template('home.html', result=result, status=status)

# ----------- REPORT PAGE: USER LINK SUBMISSION -----------
@app.route('/report', methods=['GET', 'POST'])
def report():
    message = None
    if request.method == 'POST':
        url = request.form.get('scam_link')
        if url:
            verdict, reason = check_link(url)
            if verdict == "suspicious":
                message = f"🚨 This link is already flagged: {reason}"
            elif verdict == "unknown":
                try:
                    collection.insert_one({
                        "link": url,
                        "reported_at": datetime.datetime.now().isoformat(),
                        "status": "pending"
                    })
                    message = "✅ Thank you! Your report has been submitted for review."
                except Exception as e:
                    message = f"❌ Failed to save: {e}"
            else:
                message = "✅ This link seems safe, no action needed."
        else:
            message = "❌ No link provided."
    return render_template('report.html', message=message)

@app.route('/check', methods=['GET', 'POST'])
def check_link_page():
    result = None
    status = None
    if request.method == 'POST':
        link = request.form.get('check_link')
        if link:
            existing = collection.find_one({"link": link})
            if existing:
                status = 'danger'
                result = f'🚨 This link has been reported as suspicious!'
            else:
                status = 'success'
                result = f'✅ No reports found. Link seems clean.'
    return render_template('check.html', result=result, status=status)


    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
