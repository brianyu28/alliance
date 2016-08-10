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

def send_new_message_mail(recipients, sender, message):
    print "Sender: " + sender['first']
    for recipient in recipients:
        print recipient['first']
        msg = "Dear " + recipient['first'] + ",<br/><br/>"
        msg += "You have a new message on Science Alliance Network from " + sender['first'] + " " + sender['last'] + ":<br/><br/>"
        msg += message
        msg += '<br/><br/><br/>To respond to this message, use <a href="http://sciencealliancenetwork.com/">Science Alliance Network</a>'
        if recipient['settings']['notifications']:
            emails = list(recipient['contact_emails'])
            emails.append(recipient['email'])
            print emails
            send(emails, "Science Alliance Network: New Message", msg)