from flask import Flask, request, render_template
import os
from pyzbar.pyzbar import decode
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def scan_qr(image_path):
    try:
        image = Image.open(image_path)
        decoded = decode(image)
        if not decoded:
            return None
        first_code = decoded[0]
        if first_code.type == 'QRCODE':
            return first_code.data.decode('utf-8')
        else:
            return None
    except Exception as e:
        print("Error scanning QR:", e)
        return None

def is_scam(link):
    red_flags = ['bit.ly', '.tk', 'paytmm', 'freegift', 'login-verify']
    return any(flag in link.lower() for flag in red_flags)

@app.route('/', methods=['GET', 'POST'])
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
                    if is_scam(link):
                        status = 'danger'
                        result = f'🚨 Suspicious Link Detected: {link}'
                    else:
                        status = 'success'
                        result = f'✅ Link seems clean: {link}'
                else:
                    status = 'warning'
                    result = '❌ No QR code detected.'
            except Exception as e:
                print("File upload or scan error:", e)
                status = 'danger'
                result = '⚠️ An error occurred while processing the image.'
    return render_template('index.html', result=result, status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
