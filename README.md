# Bulk Email Sender for Broken Link & Partnership Outreach

This project is a **web-based tool** to send bulk emails for two main purposes:

* 🚨 **Broken Link Outreach:** Notify websites about broken links and suggest your alternative link.
* 🤝 **Partnership Outreach:** Send partnership proposals to targeted companies.

Built with a clean UI for uploading Excel files and customizable email templates (including embedded logos/images).

---

## 🚀 Features

* **Secure Access:** Password-protected file upload to prevent unauthorized use.
* **Excel Upload:** Accepts Excel files for batch processing of recipients.
* **Dynamic Templates:**

  * *Broken Link Email:* Highlights broken URLs and offers a replacement link.
  * *Partnership Email:* Simple proposal to become a business partner.
* **Live Email Previews:** See the formatted email before sending.
* **Session Management:** Supports resetting forms and clearing data with a single button.
* **Inline Logo:** Supports embedded images (base64) in email signatures.

---

## 🗂 Excel Format Requirements

Your Excel file **must include these columns:**

| Column Name  | Description                                                                     |
| ------------ | ------------------------------------------------------------------------------- |
| company name | The recipient's company name (this is required).                                |
| email        | The recipient's email address (this is required).                               |
| page link    | The URL of the page containing the broken link (*can be null for partnership*). |
| broken link  | The broken URL to be reported (*can be null for partnership*).                  |
| fixed link   | The suggested replacement link (*can be null for partnership*).                 |

⚠ **Note: All columns must exist in the Excel file header even if you're only using the partnership template.** For the partnership emails, `page link`, `broken link`, and `fixed link` can be left empty.

---

## 🔒 How to Use

1. **Open the app.**
2. **Enter the password:**
   (default: `ApplyForChina68`).
3. **Upload your Excel file.**
4. **Choose your email template:**

   * Broken Link
   * Partnership
5. **Preview and send your emails in bulk.**
6. **Reset:** You can reset all fields and session data using the "Reset" button.

---

## 🛠 Tech Stack

* **Frontend:** HTML, Bootstrap, JavaScript
* **Backend:** Flask (or your framework)
* **Email Service:** SMTP (tested with Gmail)

---

## ⚠ Troubleshooting

* ✅ **Email fails to send?**
  Make sure:

  * Your SMTP server is accessible (check firewall/VPN)--> somethimes do not work with GHelper, if must use VPN, use hotspot shield.
  * You’re using the correct sender email & app password.
* ✅ **Reset doesn’t fully clear?**
  The reset button clears:

  * Form fields
  * Preview sections
  * Session data (via `/clear_session` POST request)


## 🙌 Credits

Made with ❤️ by Michael Joseph Candra – \[ApplyforChina].

