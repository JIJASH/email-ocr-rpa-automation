import os
import time
from imapclient import IMAPClient
from email import message_from_bytes
from email.utils import parseaddr

email = "v6053724@gmail.com"
password = "tfou vyfa vhhh qskl"
imapServer = "imap.gmail.com"
attachment_dir = "./attachments"
os.makedirs(attachment_dir, exist_ok=True)

def extract_details(msg):
  sender_name, sender_email = parseaddr(msg['From'])
  subject = msg['Subject']
  date = msg['Date']
  # body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
  print(f"From: {sender_name}")
  print(f"Email address: {sender_email}")
  print(f"Recieved on: {date}")
  print(f"Subject: {subject}")
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
  elif body:
    print(f"📜 Body: {body}")
  else:
    print(f'No body content found')
  for part in msg.walk():
          if part.get_filename():  
              filename = part.get_filename()
              file_path = os.path.join(attachment_dir, filename)
              with open(file_path, "wb") as f:
                  f.write(part.get_payload(decode=True))
              print(f"📥 Attachment downloaded: {filename}")
  print("-----")

  # print(f"📜 Body: {body}...")

def check_for_attachments():
    print("Checking emails")
    client = IMAPClient(imapServer)
    client.login(email, password)
    client.select_folder('INBOX')
    while True:
          try:
              client.idle()  # Start IDLE mode
              responses = client.idle_check(timeout=300)  
              client.idle_done()
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
                time.sleep(5)

check_for_attachments()