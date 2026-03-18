import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, render_template, request, session, redirect, url_for, flash
import pandas as pd
from io import BytesIO, StringIO
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-dev-secret')
app.permanent_session_lifetime = 3600

ALLOWED_EXTENSIONS = ('.xlsx', '.xls', '.csv', '.txt')

SENDER_EMAIL    = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
APP_PASSWORD    = os.getenv('APP_PASSWORD')


# ── CLEAR SESSION ────────────────────────────────────────────────────────────
@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.pop('excel_data', None)
    session.pop('selected_template', None)
    flash('Session has been cleared!', 'info')
    return redirect(url_for('home'))


# ── HELPERS ──────────────────────────────────────────────────────────────────
def encode_image(image_path):
    absolute_image_path = os.path.join(app.root_path, 'static', 'images', image_path)
    if not os.path.exists(absolute_image_path):
        raise FileNotFoundError(f"Image file not found at {absolute_image_path}")
    with open(absolute_image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


def send_email(recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From']    = SENDER_EMAIL
        msg['To']      = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        image_data = base64.b64decode(encode_image('A4C_Logo.png'))
        img_attachment = MIMEImage(image_data, name="logo.png")
        msg.attach(img_attachment)

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            print("Connected to server.")
            server.starttls()
            print("Started TLS.")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("Logged in.")
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")

    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")


def load_dataframe(file):
    in_memory_file = BytesIO(file.read())
    ext = os.path.splitext(file.filename)[1].lower()

    if ext in ('.xlsx', '.xls'):
        df = pd.read_excel(in_memory_file)
    elif ext in ('.csv', '.txt'):
        df = pd.read_csv(in_memory_file, sep=',')
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    df.columns = [c.strip().lower() for c in df.columns]
    return df


def build_paragraphs(df, selected_template, image_base64):
    paragraphs = []
    for _, row in df.iterrows():
        company_name = row.get('company name', '')

        if selected_template == 'partnership':
            paragraph = (
                f"Hello <b>{company_name}</b>,<br><br>"
                f"My name is Michael Joseph Candra, and I'm reaching out on behalf of <b>ApplyforChina</b>. "
                f"I came across your company and was impressed by your online presence and the work you're doing. "
                f"We're currently expanding our collaboration network and believe there's a great opportunity for us "
                f"to support each other's search visibility. Specifically, we'd love to explore a content exchange—"
                f"your team could contribute a guest post to our site, and we'd be happy to do the same for yours. "
                f"If this sounds of interest, I'd be happy to schedule a brief call to explore how we can create "
                f"a mutually beneficial partnership. Looking forward to your thoughts.<br><br>"
                f"Best regards,<br>"
                f"<i>Michael Joseph Candra</i><br>"
                f"<i><a href='https://www.applyforchina.com'>ApplyforChina</a></i><br>"
                f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
            )
        else:
            paragraph = (
                f"Dear <b>{company_name}</b>,<br><br>"
                f"I hope this message finds you well.<br><br>"
                f"My name is Michael Joseph Candra, and I'm reaching out on behalf of <b>ApplyforChina</b>. "
                f"While reviewing your website at <a href='{row.get('page link', '')}'>{row.get('page link', '')}</a>, "
                f"we noticed a broken hyperlink that currently points to "
                f"<a href='{row.get('broken link', '')}'>{row.get('broken link', '')}</a>.<br><br>"
                f"To enhance user experience, maintain your site's credibility, and support SEO performance, "
                f"we suggest updating the link to "
                f"<a href='{row.get('fixed link', '')}'>{row.get('fixed link', '')}</a>. "
                f"This is a page we manage and regularly maintain, and it contains updated and relevant information "
                f"that aligns with the content previously hosted on the broken link.<br><br>"
                f"Ensuring all links are functional not only helps reduce bounce rates but also improves user trust "
                f"and signals content quality to search engines.<br><br>"
                f"If needed, our team at <b>ApplyforChina</b> would be happy to assist with the update. "
                f"We're also open to discussing possible collaboration opportunities that align with your digital goals.<br><br>"
                f"Please feel free to reach out if you have any questions or would like to connect further.<br><br>"
                f"Best regards,<br>"
                f"<i>Michael Joseph Candra</i><br>"
                f"<i><a href='https://www.applyforchina.com'>ApplyforChina</a></i><br>"
                f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
            )
        paragraphs.append(paragraph)
    return paragraphs


# ── ROUTES ────────────────────────────────────────────────────────────────────
@app.route('/', methods=['GET', 'POST'])
def home():
    table_html = None
    paragraphs = []
    selected_template = request.args.get('template', 'broken_link')
    session['selected_template'] = selected_template

    # Always clear session on fresh page load (not when switching templates)
    if request.method == 'GET' and 'template' not in request.args:
        session.pop('excel_data', None)
        session.pop('selected_template', None)

    if request.method == 'POST':
        # No password on upload — password only required at send time

        if 'file' not in request.files:
            flash('No file part.', 'error')
            return redirect(url_for('home'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('home'))

        if file and file.filename.lower().endswith(ALLOWED_EXTENSIONS):
            try:
                df = load_dataframe(file)

                required_columns = ['company name', 'email address']
                if selected_template == 'broken_link':
                    required_columns += ['page link', 'broken link', 'fixed link']

                missing = [col for col in required_columns if col not in df.columns]
                if missing:
                    flash(f"Missing required columns: {', '.join(missing)}", 'error')
                    return redirect(url_for('home'))

                session.permanent = True
                session['excel_data'] = df.to_json(orient='records')

            except Exception as e:
                flash(f'Error reading file: {str(e)}', 'error')
                return redirect(url_for('home'))
        else:
            flash(f'Invalid file type. Please upload: {", ".join(ALLOWED_EXTENSIONS)}', 'error')
            return redirect(url_for('home'))

    if 'excel_data' in session:
        df = pd.read_json(StringIO(session['excel_data']))
        table_html = df.to_html(classes='table table-striped', index=False)
        image_base64 = encode_image('A4C_Logo.png')
        paragraphs = build_paragraphs(df, selected_template, image_base64)

    return render_template('index.html',
                           table_html=table_html,
                           paragraphs=paragraphs,
                           selected_template=selected_template)


@app.route('/send_email', methods=['POST'])
def send_bulk_email():
    try:
        # Password check happens here, not on upload
        entered_password = request.form.get('modal_password', '')
        if entered_password != APP_PASSWORD:
            flash('Incorrect password. Emails were not sent.', 'error')
            return redirect(url_for('home'))

        if 'excel_data' not in session:
            flash('No email data available. Please upload the file again.', 'error')
            return redirect(url_for('home'))

        df = pd.read_json(StringIO(session['excel_data']))
        selected_template = session.get('selected_template', 'broken_link')
        image_base64 = encode_image('A4C_Logo.png')

        for _, row in df.iterrows():
            company_name   = row.get('company name', '')
            recipient_email = str(row.get('email address', '')).strip()

            if not recipient_email:
                print(f"Skipping row with missing email: {company_name}")
                continue

            if selected_template == 'partnership':
                subject = f"Exploring Partnership Opportunity with {company_name}"
                body = (
                    f"Hello <b>{company_name}</b>,<br><br>"
                    f"My name is Michael Joseph Candra, and I'm reaching out on behalf of <b>ApplyforChina</b>. "
                    f"I came across your company and was impressed by your online presence and the work you're doing. "
                    f"We're currently expanding our collaboration network and believe there's a great opportunity for us "
                    f"to support each other's search visibility. Specifically, we'd love to explore a content exchange—"
                    f"your team could contribute a guest post to our site, and we'd be happy to do the same for yours. "
                    f"If this sounds of interest, I'd be happy to schedule a brief call to explore how we can create "
                    f"a mutually beneficial partnership. Looking forward to your thoughts.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f'<i><a href="https://www.applyforchina.com">ApplyforChina</a></i><br>'
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )
            else:
                subject = f"Broken Link Notification for {company_name}"
                body = (
                    f"Dear <b>{company_name}</b>,<br><br>"
                    f"I hope this message finds you well.<br><br>"
                    f"My name is Michael Joseph Candra, and I'm reaching out on behalf of <b>ApplyforChina</b>. "
                    f"While reviewing your website at <a href='{row.get('page link', '')}'>{row.get('page link', '')}</a>, "
                    f"we noticed a broken hyperlink that currently points to "
                    f"<a href='{row.get('broken link', '')}'>{row.get('broken link', '')}</a>.<br><br>"
                    f"To enhance user experience, maintain your site's credibility, and support SEO performance, "
                    f"we suggest updating the link to "
                    f"<a href='{row.get('fixed link', '')}'>{row.get('fixed link', '')}</a>. "
                    f"This is a page we manage and regularly maintain, and it contains updated and relevant information "
                    f"that aligns with the content previously hosted on the broken link.<br><br>"
                    f"Ensuring all links are functional not only helps reduce bounce rates but also improves user trust "
                    f"and signals content quality to search engines.<br><br>"
                    f"If needed, our team at <b>ApplyforChina</b> would be happy to assist with the update. "
                    f"We're also open to discussing possible collaboration opportunities that align with your digital goals.<br><br>"
                    f"Please feel free to reach out if you have any questions or would like to connect further.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f"<i><a href='https://www.applyforchina.com'>ApplyforChina</a></i><br>"
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )

            send_email(recipient_email, subject, body)

        session.pop('excel_data', None)
        session.pop('selected_template', None)

        flash('Bulk emails have been sent successfully!', 'success')
        return redirect(url_for('home', template=selected_template))

    except Exception as e:
        flash(f'Error sending emails: {str(e)}', 'error')
        return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)