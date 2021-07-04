import os
import subprocess
import time
import re
import email
import smtplib

# Pre-define Variable
faultCounter = 0
maxFaultCount = 2
resetCounter = 0
maxResetCounter = 5
IPStatus = -1
sleepTime = 1

# IP Detail
NetworkInterface = 'eth0'
Primary_IPAddr = '192.168.0.154'
Secondary_IPAddr = '192.168.0.245'
SubnetMask = '255.255.255.0'

# Interface Detail
InterfaceDetail = str(subprocess.check_output("ifconfig"))
InterfaceStart = "eth0:"
InterfaceEnd = "collisions"

# Email
SMTPServer = "smtp-mail.outlook.com"
SMTPPort = 587
SenderEmail = "IntouchTest001@hotmail.com"
SenderPassword = "IntouchICT2021#"
ReceiverEmail = "eric@intouchictsolutions.com.au"


# Ping Host (use OS.System)
def pingHost(host):
    response = os.system("ping -c 1 " + host)
    return response


# Find the First IP address from Interface interface
def regexFindIPAddress():
    subString1 = InterfaceDetail.find(InterfaceStart)
    subString2 = InterfaceDetail.find(InterfaceEnd)
    IPAddress = re.search(r'\d+.\d+.\d+.\d+', InterfaceDetail[subString1:subString2]).group(0)
    return IPAddress


# 1 = Primary  2 = Secondary   3 = Error
def IPAddressStatus():
    if regexFindIPAddress() == Primary_IPAddr:
        return 1
    elif regexFindIPAddress() == Secondary_IPAddr:
        return 2
    else:
        return 3


def EmailToServer(EmailSubjectContent, MailContent):
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

    # Print on Console
    print()
    print("Sent Mail")
    print()


def runOSChangeIP_Addr():
    # Clean all the IP Address
    os.system("sudo ip addr flush " + NetworkInterface)
    print("Flush Down")
    time.sleep(sleepTime)

    # Force the Eth0 disable
    os.system("sudo ifconfig eth0 down")
    print("Eth0 Down")
    time.sleep(sleepTime)

    # Restart Network Interface and set IP to Primary
    os.system("sudo ifconfig " + NetworkInterface + " " + Primary_IPAddr)
    os.system("ifconfig")


# Main Program
while True:
    print("My IP Status: " + str(IPStatus))

    # IP Status = 1 -> Primary Server
    while IPStatus == 1:
        # Monitor Ping Status -> 0 = Success else Fail
        pingStatus = pingHost(Secondary_IPAddr)

        # Fault Counter reach to max -> Report Error & Reset Fault Count
        if faultCounter == maxFaultCount:
            print("Primary Server: Fault Tolerant Reach to Max, Cannot ping to Secondary Server")

            # Email Content
            ESubject = "Server 2 is Down"
            EContent = "Primary Server Cannot Ping to Secondary Server, Server maybe Disconnect or Offline"

            # Send Email
            EmailToServer(ESubject, EContent)
            faultCounter = -100
            time.sleep(sleepTime)

        # Fault Tolerant & Ping Success -> FaultCount reset
        elif (faultCounter < maxFaultCount) & (pingStatus == 0):
            # Refresh Fault Counter
            faultCounter = 0
            time.sleep(sleepTime)

        # Ping fail & Fail tolerant within limit -> ResetCount Reset, FaultCount ++
        elif (faultCounter < maxFaultCount) & (pingStatus != 0):
            # If Detect Fault (tolerant 5 fault)
            faultCounter = faultCounter + 1
            print("Primary Server - Fail tolerant: " + str(faultCounter))
            time.sleep(sleepTime)

        else:
            print("Primary Server: Error Unknown")
            time.sleep(sleepTime)

    while IPStatus == 2:
        # Monitor Ping Status -> 0 = Success else Fail
        pingStatus = pingHost(Primary_IPAddr)

        # Fault Counter reach to max -> Report Error & Reset Fault Count
        if faultCounter == maxFaultCount:
            # Email Content
            ESubject = "Server 1 is Down"
            EContent = "Secondary Server Cannot Ping to Secondary Server, Secondary Server Become Primary Server"

            # Send Email
            EmailToServer(ESubject, EContent)

            # Change IP Address
            print("Backup Server Active")
            runOSChangeIP_Addr()

            # Exit Program
            exit()

        # Fault Tolerant & Ping Success -> FaultCount reset, ResetCounter ++
        elif (faultCounter < maxFaultCount) & (pingStatus == 0):
            # Refresh Counter if No error
            faultCounter = 0
            time.sleep(sleepTime)

        # Ping fail & Fail tolerant within limit -> FaultCount ++
        elif (faultCounter < maxFaultCount) & (pingStatus != 0):
            # If Detect Fault (tolerant 5 fault)
            faultCounter = faultCounter + 1
            print("Secondary Server - Fail tolerant: " + str(faultCounter))
            time.sleep(sleepTime)

        else:
            print("Secondary Server: Error Unknown")
            time.sleep(sleepTime)

    # IP Status neither Primary nor Secondary -> Re-detect the IP Status
    while (IPStatus != 1) & (IPStatus != 2):
        if faultCounter < maxFaultCount:
            IPStatus = IPAddressStatus()
            faultCounter = faultCounter + 1
            print(IPStatus)
            print("Error")
            time.sleep(sleepTime)
        else:
            # Reset Fault Count avoid Error
            faultCounter = 0
            print("Error -> Need to Report")
            time.sleep(sleepTime)
