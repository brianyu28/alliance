import sys
import os
import re
import secrets
from smtplib import SMTP_SSL as SMTP  # this invokes the secure SMTP protocol (port 465, uses SSL)
# from smtplib import SMTP         # use this for standard SMTP protocol   (port 25, no encryption)

def send(destination, subject, content):

    SMTPserver = 'mail.sciencealliancenetwork.com'
    sender =     'no-reply@sciencealliancenetwork.com'
    destination = destination

    USERNAME = secrets.mailusername
    PASSWORD = secrets.mailpassword

    # typical values for text_subtype are plain, html, xml
    text_subtype = 'html'
    content=content
    subject=subject

    from email.mime.text import MIMEText
    try:
        msg = MIMEText(content, text_subtype)
        msg['Subject']=       subject
        msg['From']   = sender # some SMTP servers will do this automatically, not all
        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False)
        conn.login(USERNAME, PASSWORD)
        try:
            conn.sendmail(sender, destination, msg.as_string())
        finally:
            conn.quit()
    except Exception, exc:
        sys.exit( "mail failed; %s" % str(exc) ) # give a error message
