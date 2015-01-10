#!/usr/bin/python
import requests
import json
import smtplib
# This is a simple script for using DigitalOcean's DNS as dynamic DNS.
# I use it for the VPN I have at my home. It requires a DO API key,
# takes a domain name, a subdomain, and email credentials (I'm using gmail).
# Simply have this running as a cron on a machine in your internal network, and you're good to go.
# Note: This script utilizes V2 of the DO API. https://developers.digitalocean.com

# Domain Info
domain_name = 'example.com'
subdomain_name = 'subdomain'  # Use an '@' if you aren't using a subdomain

# Email Setup
username = 'email@example.com'  # Username here
password = 'yourpassword'  # Password here (I recommend generating an app password with 2FA enabled)
FROM = 'email@example.com'  # From address here
TO = ['email@example.com']  # This must be a list

# Set your DO API key here. 'Bearer' is required by the API
# in the authorization header.
do_api_key = 'Bearer yourAPIkeyHere'
do_api_url = 'https://api.digitalocean.com/v2/domains/%s/records' % domain_name
do_request_header = {'content-type': 'application/json', 'Authorization': do_api_key}

# Determine current external IP
external_ip = requests.get('http://echoip.com').text

# Get list of domains on DO account
get_domains = requests.get(do_api_url, headers=do_request_header).json()

# Go through the list of domains and find the domain being used for dynamic DNS
for domain in get_domains['domain_records']:
    if domain['name'] == subdomain_name:
        do_ip = domain['data']
        do_id = domain['id']
        if external_ip != do_ip and domain['type'] == 'A':
            # Setup the email for a IP change
            msg = "\r\n".join([
                "From: %s",
                "To: %s",
                "Subject: External IP Change",
                "",
                "External IP changed from %s to %s"
                ]) % (FROM, TO, do_ip, external_ip)
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.sendmail(FROM, TO, msg)

            # Update the DigitalOcean DNS record
            update_url = 'https://api.digitalocean.com/v2/domains/%s/records/%s' % (domain_name, do_id)
            do_update_data = {'data': external_ip}
            requests.put(update_url, data=json.dumps(do_update_data), headers=do_request_header)
