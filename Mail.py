import email
import smtplib
import time


# Login Credential
SenderEmail = "IntouchTest001@hotmail.com"
SenderPassword = "IntouchICT2021#"

# SMTP Mail Info
SMTPServer = "smtp-mail.outlook.com"
SMTPPort = 587

# Receiver Info
ReceiverEmail = "eric@intouchictsolutions.com.au"

text = 2


def SendMail(EmailSubjectContent, MailContent):
    # Email Content
    msg = email.message_from_string(MailContent)
    msg['From'] = SenderEmail
    msg['To'] = ReceiverEmail
    msg['Subject'] = EmailSubjectContent

    # Establish Connection to SMTP Server and Send Email
    s = smtplib.SMTP(SMTPServer, SMTPPort)
    s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
    s.starttls()  # Puts connection to SMTP server in TLS mode
    s.ehlo()
    s.login(SenderEmail, SenderPassword)
    s.sendmail(SenderEmail, ReceiverEmail, msg.as_string())

    # End Connection
    s.quit()


if text == 1:
    MSubject = "Server 1 Down"
    MContent = "Down" + str(time.time())
    SendMail(MSubject, MContent)
elif text == 2:
    MSubject = "Server 2 Down"
    MContent = "Down" + str(time.time())
    SendMail(MSubject, MContent)