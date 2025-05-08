import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import pandas as pd
from io import BytesIO
import base64
import json  # for JSON dump

app = Flask(__name__)
app.secret_key = 'hello123'  # Replace with a secure random string!
app.permanent_session_lifetime = 3600  # session lasts 1 hour


@app.route('/clear_session', methods=['POST'])
def clear_session():
    # Clear the same specific session data as in send_bulk_email
    session.pop('excel_data', None)
    session.pop('selected_template', None)

    flash('Session has been cleared!', 'info')
    return redirect(url_for('home'))


# Function to encode image to base64
def encode_image(image_path):
    absolute_image_path = os.path.join(app.root_path, 'static', 'images', image_path)
    if not os.path.exists(absolute_image_path):
        raise FileNotFoundError(f"Image file not found at {absolute_image_path}")
    with open(absolute_image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')


# Function to send the email
def send_email(recipient_email, subject, body):
    try:
        sender_email = "michaeljosephcandra@gmail.com"
        sender_password = "ndey kkel fktf vfdd"


        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        image_base64 = encode_image('A4C Logo.png')
        image_data = base64.b64decode(image_base64)
        image_attachment = MIMEImage(image_data, name="logo.png")
        msg.attach(image_attachment)

        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            print("Connected to server.")
            server.starttls()
            print("Started TLS.")
            server.login(sender_email, sender_password)
            print("Logged in.")
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Email sent to {recipient_email}")


    except Exception as e:
        print(f"Error sending email to {recipient_email}: {str(e)}")


@app.route('/', methods=['GET', 'POST'])
def home():
    table_html = None
    paragraphs = []
    password = "ApplyForChina68"
    # Get selected template from query parameter or default to 'broken_link'
    selected_template = request.args.get('template', 'broken_link')
    session['selected_template'] = selected_template  # store in session

    if request.method == 'POST':
        entered_password = request.form.get('password')

        if entered_password != password:
            flash('Incorrect password. Please try again.', 'error')
            return redirect(url_for('home'))

        flash('Password is correct!', 'success')

        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(url_for('home'))

        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('home'))

        if file and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            try:
                in_memory_file = BytesIO(file.read())
                df = pd.read_excel(in_memory_file)

                required_columns = ['company name', 'email address', 'page link', 'broken link', 'fixed link']
                if not all(col in df.columns for col in required_columns):
                    flash(f"Missing required columns: {', '.join(required_columns)}", 'error')
                    return redirect(url_for('home'))

                # Save data to session
                session.permanent = True
                session['excel_data'] = df.to_json(orient='records')
                table_html = df.to_html(classes='table table-striped', index=False)
                paragraphs = []

                image_base64 = encode_image('A4C Logo.png')

                for _, row in df.iterrows():
                    paragraph = (
                        f"Dear <b>{row['company name']}</b>,<br><br>"
                        f"I hope this message finds you well.<br><br>"
                        f"While reviewing your website at \"<a href='{row['page link']}'>{row['page link']}</a>\", we identified a broken hyperlink "
                        f"currently pointing to \"<a href='{row['broken link']}'>{row['broken link']}</a>\". To enhance user experience and "
                        f"maintain optimal website performance, we recommend replacing it with an updated resource: "
                        f"\"<a href='{row['fixed link']}'>{row['fixed link']}</a>\".<br><br>"
                        f"Should you require any assistance in addressing this issue or implementing the update, our team at "
                        f"<b>ApplyforChina</b> would be happy to support you. Please feel free to reach out to us for further guidance or collaboration.<br><br>"
                        f"Best regards,<br>"
                        f"<i>Michael Joseph Candra</i><br>"
                        f"<i>ApplyforChina</i><br><br>"
                        f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                    )
                    paragraphs.append(paragraph)

                # ✅ Store DataFrame as JSON in session
                session.permanent = True
                session['excel_data'] = df.to_json(orient='records')  # Save as JSON string

            except Exception as e:
                flash(f'Error reading Excel file: {str(e)}', 'error')
                return redirect(url_for('home'))
        else:
            flash('Invalid file type. Please upload an Excel file.', 'error')
            return redirect(url_for('home'))


    # ✅ Now: check if session['excel_data'] exists, even in GET
    if 'excel_data' in session:
        df = pd.read_json(session['excel_data'])
        table_html = df.to_html(classes='table table-striped', index=False)
        paragraphs = []

        image_base64 = encode_image('A4C Logo.png')

        for _, row in df.iterrows():
            company_name = row['company name']

            if selected_template == 'partnership':
                paragraph = (
                    f"Hello <b>{company_name}</b>,<br><br>"
                    f"My name is Michael Joseph Candra, and I represent <b>ApplyforChina</b>. "
                    f"We are currently looking to expand our collaboration network and I am reaching out to explore potential partnership opportunities with your company.<br><br>"
                    f"I would love to discuss how we can work together and create mutual benefits. Please let me know if you are interested or available for a brief call.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f"<i>ApplyforChina</i><br><br>"
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )
            else:
                paragraph = (
                    f"Dear <b>{company_name}</b>,<br><br>"
                    f"I hope this message finds you well.<br><br>"
                    f"While reviewing your website at \"<a href='{row['page link']}'>{row['page link']}</a>\", we identified a broken hyperlink "
                    f"currently pointing to \"<a href='{row['broken link']}'>{row['broken link']}</a>\". To enhance user experience and "
                    f"maintain optimal website performance, we recommend replacing it with an updated resource: "
                    f"\"<a href='{row['fixed link']}'>{row['fixed link']}</a>\".<br><br>"
                    f"Should you require any assistance in addressing this issue or implementing the update, our team at "
                    f"<b>ApplyforChina</b> would be happy to support you. Please feel free to reach out to us for further guidance or collaboration.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f"<i>ApplyforChina</i><br><br>"
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )
            paragraphs.append(paragraph)

    return render_template('index.html', table_html=table_html, paragraphs=paragraphs, selected_template=selected_template)



@app.route('/send_email', methods=['POST'])
def send_bulk_email():
    try:
        if 'excel_data' not in session:
            flash('No email data available. Please upload the Excel file again.', 'error')
            return redirect(url_for('home'))

        data_json = session['excel_data']
        df = pd.read_json(data_json)
        selected_template = session.get('selected_template', 'broken_link')

        image_base64 = encode_image('A4C Logo.png')

        for _, row in df.iterrows():
            company_name = row['company name']
            recipient_email = row['email address']

            if selected_template == 'partnership':
                subject = f"Exploring Partnership Opportunity with {company_name}"
                body = (
                    f"Hello <b>{company_name}</b>,<br><br>"
                    f"My name is Michael Joseph Candra, and I represent <b>ApplyforChina</b>. "
                    f"We are currently looking to expand our collaboration network and I am reaching out to explore potential partnership opportunities with your company.<br><br>"
                    f"I would love to discuss how we can work together and create mutual benefits. Please let me know if you are interested or available for a brief call.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f"<i>ApplyforChina</i><br><br>"
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )
            else:
                subject = f"Broken Link Notification for {company_name}"
                body = (
                    f"Dear <b>{company_name}</b>,<br><br>"
                    f"I hope this message finds you well.<br><br>"
                    f"While reviewing your website at \"<a href='{row['page link']}'>{row['page link']}</a>\", we identified a broken hyperlink "
                    f"currently pointing to \"<a href='{row['broken link']}'>{row['broken link']}</a>\". To enhance user experience and "
                    f"maintain optimal website performance, we recommend replacing it with an updated resource: "
                    f"\"<a href='{row['fixed link']}'>{row['fixed link']}</a>\".<br><br>"
                    f"Should you require any assistance in addressing this issue or implementing the update, our team at "
                    f"<b>ApplyforChina</b> would be happy to support you. Please feel free to reach out to us for further guidance or collaboration.<br><br>"
                    f"Best regards,<br>"
                    f"<i>Michael Joseph Candra</i><br>"
                    f"<i>ApplyforChina</i><br><br>"
                    f"<img src='data:image/png;base64,{image_base64}' alt='Logo' style='max-width: 200px;'><br><br>"
                )

            send_email(recipient_email, subject, body)

        # Clear the session data after sending emails
        session.pop('excel_data', None)
        session.pop('selected_template', None)

        flash('Bulk emails have been sent successfully!', 'success')
        return redirect(url_for('home', template=selected_template))

    except Exception as e:
        flash(f'Error sending emails: {str(e)}', 'error')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
