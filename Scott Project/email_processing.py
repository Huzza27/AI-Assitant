import imaplib
import email
import re
import time


def get_latest_email_id(user, password, server, sender):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, password)
    mail.select('inbox')

    status, data = mail.search(None, f'FROM "{sender}"')
    if status != 'OK':
        mail.logout()
        return None

    messages = data[0].split()
    latest_email_id = messages[-1] if messages else None
    mail.logout()
    return latest_email_id

def get_email_body(user, password, server, email_id):
    mail = imaplib.IMAP4_SSL(server)
    mail.login(user, password)
    mail.select('inbox')

    _, data = mail.fetch(email_id, '(RFC822)')
    message = email.message_from_bytes(data[0][1])
    mail.logout()

    for part in message.walk():
        if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
            return part.get_payload(decode=True).decode()
    return None

def find_2fa_code_in_body(body):
    match = re.search(r'\b\d{6}\b', body)  # Regex for 6-digit code
    if match:
        return match.group()
    return None

def wait_for_new_email(user, password, server, sender, timeout=180):  # 3 minutes timeout
    start_time = time.time()
    latest_checked_email_id = get_latest_email_id(user, password, server, sender)

    while time.time() - start_time < timeout:
        time.sleep(10)  # Wait for 10 seconds before checking again
        latest_email_id = get_latest_email_id(user, password, server, sender)

        if latest_email_id != latest_checked_email_id:
            email_body = get_email_body(user, password, server, latest_email_id)
            two_factor_code = find_2fa_code_in_body(email_body)
            if two_factor_code:
                return two_factor_code

            latest_checked_email_id = latest_email_id  # Update the last checked email ID

    return None  # Return None if no new email with 2FA code is found

# Example usage
print("Python is running")
 
