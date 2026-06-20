from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
from datetime import datetime, timedelta
from email import message_from_bytes
from email.header import decode_header
from email.utils import parsedate_to_datetime
import imaplib
import json
import os
import re

app = Flask(__name__)
CORS(app)

PATH = 'all excels/'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TARGET_JOBS_PATH = os.path.join(DATA_DIR, 'target_jobs.json')


def load_target_jobs():
    if not os.path.exists(TARGET_JOBS_PATH):
        return []
    with open(TARGET_JOBS_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_target_jobs(jobs):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TARGET_JOBS_PATH, 'w', encoding='utf-8') as file:
        json.dump(jobs, file, indent=2, ensure_ascii=False)


def decode_mime(value):
    if not value:
        return ''
    parts = []
    for text, charset in decode_header(value):
        if isinstance(text, bytes):
            parts.append(text.decode(charset or 'utf-8', errors='replace'))
        else:
            parts.append(text)
    return ''.join(parts)


def extract_text_from_message(message):
    chunks = []
    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            disposition = str(part.get('Content-Disposition') or '').lower()
            if 'attachment' in disposition:
                continue
            if content_type == 'text/plain':
                payload = part.get_payload(decode=True)
                if payload:
                    chunks.append(payload.decode(part.get_content_charset() or 'utf-8', errors='replace'))
    elif message.get_content_type() == 'text/plain':
        payload = message.get_payload(decode=True)
        if payload:
            chunks.append(payload.decode(message.get_content_charset() or 'utf-8', errors='replace'))
    return '\n'.join(chunks)


def company_tokens(company):
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', company.lower())
    words = [word for word in normalized.split() if len(word) > 2]
    aliases = {
        'general motors': ['gm', 'general motors'],
        'rivian and volkswagen group technologies': ['rivian', 'volkswagen', 'vw'],
        'base power': ['base power'],
    }
    return aliases.get(company.lower(), words + [company.lower()])


def classify_reply(subject, body):
    text = f'{subject}\n{body}'.lower()
    if any(word in text for word in ['interview', 'schedule', 'availability', 'next step', 'next steps']):
        return 'interview_or_next_step'
    if any(word in text for word in ['assessment', 'coding challenge', 'test', 'hackerrank', 'codility']):
        return 'assessment'
    if any(word in text for word in ['unfortunately', 'not selected', 'not moving forward', 'decided to pursue']):
        return 'rejection'
    if any(word in text for word in ['received your application', 'application received', 'thank you for applying']):
        return 'received'
    return 'unclassified'


def match_reply_to_jobs(sender, subject, body, target_jobs):
    haystack = f'{sender}\n{subject}\n{body}'.lower()
    matches = []
    for job in target_jobs:
        tokens = company_tokens(job.get('company', ''))
        role_words = [
            word for word in re.sub(r'[^a-z0-9 ]+', ' ', job.get('role', '').lower()).split()
            if len(word) > 5
        ]
        company_hit = any(token and token in haystack for token in tokens)
        role_hit = sum(1 for word in role_words if word in haystack)
        if company_hit or role_hit >= 2:
            matches.append({
                'job_id': job.get('id'),
                'company': job.get('company'),
                'role': job.get('role'),
                'confidence': 'high' if company_hit and role_hit >= 1 else 'medium',
            })
    return matches


def email_config():
    return {
        'host': os.environ.get('JOB_AGENT_IMAP_HOST', ''),
        'port': int(os.environ.get('JOB_AGENT_IMAP_PORT', '993')),
        'user': os.environ.get('JOB_AGENT_IMAP_USER', ''),
        'password': os.environ.get('JOB_AGENT_IMAP_PASSWORD', ''),
        'mailbox': os.environ.get('JOB_AGENT_IMAP_MAILBOX', 'INBOX'),
    }


def fetch_email_replies(days=30, limit=50):
    config = email_config()
    if not (config['host'] and config['user'] and config['password']):
        return {
            'configured': False,
            'messages': [],
            'error': 'Set JOB_AGENT_IMAP_HOST, JOB_AGENT_IMAP_USER, and JOB_AGENT_IMAP_PASSWORD to enable email reply tracking.',
        }

    target_jobs = load_target_jobs()
    since = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
    messages = []

    with imaplib.IMAP4_SSL(config['host'], config['port']) as mail:
        mail.login(config['user'], config['password'])
        mail.select(config['mailbox'])
        status, data = mail.search(None, f'(SINCE "{since}")')
        if status != 'OK':
            return {'configured': True, 'messages': [], 'error': 'IMAP search failed.'}

        message_ids = data[0].split()[-limit:]
        for message_id in reversed(message_ids):
            status, msg_data = mail.fetch(message_id, '(RFC822)')
            if status != 'OK' or not msg_data or not msg_data[0]:
                continue
            raw_message = msg_data[0][1]
            message = message_from_bytes(raw_message)
            sender = decode_mime(message.get('From', ''))
            subject = decode_mime(message.get('Subject', ''))
            body = extract_text_from_message(message)
            snippet = re.sub(r'\s+', ' ', body).strip()[:360]
            matches = match_reply_to_jobs(sender, subject, body, target_jobs)
            if not matches:
                continue
            date_value = message.get('Date', '')
            try:
                received_at = parsedate_to_datetime(date_value).isoformat()
            except Exception:
                received_at = date_value
            messages.append({
                'from': sender,
                'subject': subject,
                'date': received_at,
                'category': classify_reply(subject, body),
                'matched_jobs': matches,
                'snippet': snippet,
            })

    return {'configured': True, 'messages': messages, 'error': None}


##> ------ Karthik Sarode : karthik.sarode23@gmail.com - UI for excel files ------
@app.route('/')
def home():
    """Displays the home page of the application."""
    return render_template('index.html')

@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    '''
    Retrieves a list of applied jobs from the applications history CSV file.
    
    Returns a JSON response containing a list of jobs, each with details such as 
    Job ID, Title, Company, HR Name, HR Link, Job Link, External Job link, and Date Applied.
    
    If the CSV file is not found, returns a 404 error with a relevant message.
    If any other exception occurs, returns a 500 error with the exception message.
    '''

    try:
        jobs = []
        with open(PATH + 'all_applied_applications_history.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                jobs.append({
                    'Job_ID': row['Job ID'],
                    'Title': row['Title'],
                    'Company': row['Company'],
                    'HR_Name': row['HR Name'],
                    'HR_Link': row['HR Link'],
                    'Job_Link': row['Job Link'],
                    'External_Job_link': row['External Job link'],
                    'Date_Applied': row['Date Applied']
                })
        return jsonify(jobs)
    except FileNotFoundError:
        return jsonify({"error": "No applications history found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/target-jobs', methods=['GET'])
def get_target_jobs():
    """Returns locally saved target jobs from the latest search."""
    try:
        jobs = load_target_jobs()
        return jsonify(jobs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/target-jobs/<job_id>', methods=['PUT'])
def update_target_job(job_id):
    """Updates local target-job status, such as target/applied/skipped."""
    try:
        payload = request.get_json(silent=True) or {}
        allowed_status = {'target', 'applied', 'skipped', 'interview', 'rejected'}
        new_status = payload.get('status')
        if new_status not in allowed_status:
            return jsonify({"error": f"status must be one of {sorted(allowed_status)}"}), 400

        jobs = load_target_jobs()
        for job in jobs:
            if job.get('id') == job_id:
                job['status'] = new_status
                if new_status == 'applied':
                    job['date_applied'] = payload.get('date_applied') or datetime.now().strftime('%Y-%m-%d')
                save_target_jobs(jobs)
                return jsonify(job)
        return jsonify({"error": f"Target job {job_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/email-config-status', methods=['GET'])
def get_email_config_status():
    config = email_config()
    return jsonify({
        'configured': bool(config['host'] and config['user'] and config['password']),
        'host': config['host'],
        'user': config['user'],
        'mailbox': config['mailbox'],
        'missing': [
            name for name, value in [
                ('JOB_AGENT_IMAP_HOST', config['host']),
                ('JOB_AGENT_IMAP_USER', config['user']),
                ('JOB_AGENT_IMAP_PASSWORD', config['password']),
            ]
            if not value
        ],
    })


@app.route('/email-replies', methods=['GET'])
def get_email_replies():
    """Reads recent IMAP messages and returns replies matched to target jobs."""
    try:
        days = int(request.args.get('days', '30'))
        limit = int(request.args.get('limit', '50'))
        days = max(1, min(days, 120))
        limit = max(1, min(limit, 200))
        return jsonify(fetch_email_replies(days=days, limit=limit))
    except Exception as e:
        return jsonify({'configured': True, 'messages': [], 'error': str(e)}), 500

@app.route('/bot-status', methods=['GET'])
def get_bot_status():
    """Returns the current status and latest logs of the bot."""
    log_path = 'logs/logs.txt'
    try:
        if not os.path.exists(log_path):
            return jsonify({"status": "Idle", "logs": []})
        
        with open(log_path, 'r', encoding='utf-8') as f:
            # Get last 50 lines of logs
            lines = f.readlines()
            latest_logs = [line.strip() for line in lines[-50:]]
            
        # Basic heuristic for status
        current_status = "Running" if latest_logs and "Sleeping" not in latest_logs[-1] else "Idle"
        if any("failed" in line.lower() for line in latest_logs[-5:]):
            current_status = "Attention Required"
            
        return jsonify({
            "status": current_status,
            "logs": latest_logs,
            "last_update": datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/applied-jobs/<job_id>', methods=['PUT'])
def update_applied_date(job_id):
    """
    Updates the 'Date Applied' field of a job in the applications history CSV file.

    Args:
        job_id (str): The Job ID of the job to be updated.

    Returns:
        A JSON response with a message indicating success or failure of the update
        operation. If the job is not found, returns a 404 error with a relevant
        message. If any other exception occurs, returns a 500 error with the
        exception message.
    """
    try:
        data = []
        csvPath = PATH + 'all_applied_applications_history.csv'
        
        if not os.path.exists(csvPath):
            return jsonify({"error": f"CSV file not found at {csvPath}"}), 404
            
        # Read current CSV content
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldNames = reader.fieldnames
            found = False
            for row in reader:
                if row['Job ID'] == job_id:
                    row['Date Applied'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    found = True
                data.append(row)
        
        if not found:
            return jsonify({"error": f"Job ID {job_id} not found"}), 404

        with open(csvPath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(data)
        
        return jsonify({"message": "Date Applied updated successfully"}), 200
    except Exception as e:
        print(f"Error updating applied date: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('JOB_AGENT_UI_PORT', '5000'))
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

##<
