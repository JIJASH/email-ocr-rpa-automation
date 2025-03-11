import os
import time
from imapclient import IMAPClient
import smtplib
from email import message_from_bytes
from email.utils import parseaddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

email = "v6053724@gmail.com"
password = "tfou vyfa vhhh qskl"
imapServer = "imap.gmail.com"
attachment_dir = "./temp"
os.makedirs(attachment_dir, exist_ok=True)
service_acc_cred = "./serviceAcc/mail-watcher-47-49ce629e4ae7.json"
scopes = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(
    service_acc_cred, scopes=scopes
)
drive_service = build("drive", "v3", credentials = credentials)


folder_id = "1J7bYwFbs-5R80Xg5nWxsakMBtbefUKCs" # this is from the drive folder where i am saving

def upload_to_drive(file_path):
    """Uploads file to Google Drive"""
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    media = MediaFileUpload(file_path, resumable=True)
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    # print(f" Uploaded to Google Drive: {file.get('id')}")
    print(f"Attachment uploaded to Google Drive!")

    return file.get("id")

def extract_details(msg):
  sender_name, sender_email = parseaddr(msg['From'])
  subject = msg['Subject']
  date = msg['Date']
  body = ""
  # body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
  print(f"From: {sender_name}")
  print(f"Email address: {sender_email}")
  print(f"Recieved on: {date} \n")
  print(f"Subject: {subject} \n")

  if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
  else:
      body = msg.get_payload(decode=True).decode()
  if len(body) > 200:
     print(f"📜 Body: {body[:250]}...")
  else:
    body_preview = body if body else "No body content found"
  print(f"📜 Body: {body_preview}")
  for part in msg.walk():
          if part.get_filename():
              filename = part.get_filename()
              file_path = os.path.join(attachment_dir, filename)
              with open(file_path, "wb") as f:
                  f.write(part.get_payload(decode=True))
              # print(f"Attachment downloaded: {filename} \n")
              drive_file_id = upload_to_drive(file_path)          # upload
              os.remove(file_path)      # remove the local temp file
              time.sleep(5)
              send_reply(sender_email)
  print("-----")


  # print(f"📜 Body: {body}...")

def send_reply(to_email):
  from_email = "v6053724@gmail.com"
  password = "tfou vyfa vhhh qskl"
  subject = "Completed"
  body = "Your attachment has been processed."

  msg = MIMEMultipart()
  msg['From'] = from_email
  msg['To'] = to_email
  msg['Subject'] = subject
  msg.attach(MIMEText(body, 'plain'))

  try:
      with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
          server.login(from_email, password)
          server.sendmail(from_email, to_email, msg.as_string())
      print(f"Reply sent to {to_email}")
      print("-------------------------")
  except Exception as e:
      print(f"Error sending reply to {to_email}: {e}")
  
def check_for_attachments():
    print("Checking emails")
    client = IMAPClient(imapServer)
    client.login(email, password)
    client.select_folder('INBOX')
    while True:
          try:
              client.idle()
              # print("Entering idle mode")
              responses = client.idle_check(timeout=300)
              client.idle_done()
              # print("Exiting idle mode")
              if responses:
                messages = client.search('UNSEEN')
                if messages:
                  print("New email recieved! ")
                  for msg_id in messages:
                    raw_email = client.fetch(msg_id, ['RFC822'])[msg_id][b'RFC822']
                    processed_mail = message_from_bytes(raw_email)
                  # print(processed_mail)
                    extract_details(processed_mail)
                else:
                  print("its quiet here")
          except KeyboardInterrupt:
            print("Stopping")
            break
          except Exception as e:
                print(f"⚠️ Error: {e}")

    # client.logout()
check_for_attachments()