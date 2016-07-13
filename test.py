import requests
import json
from oauthlib.oauth1 import Client
import pymysql
import databaseconfig as CFG
import post as POST

connection = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
pymysql.paramstyle = 'named'

cursor = connection.cursor()

# TODO: Also do this at the end
sql = "DELETE FROM lti_user WHERE user_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
cursor.execute(sql)
connection.commit();
print('Removed {} old unittest users'.format(cursor.rowcount))
sql = "ALTER TABLE `lti_user` AUTO_INCREMENT = 1";
cursor.execute(sql)
connection.commit();

sql = "DELETE FROM lti_context WHERE context_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
cursor.execute(sql)
connection.commit();
print('Removed {} old unittest contexts'.format(cursor.rowcount))
sql = "ALTER TABLE `lti_context` AUTO_INCREMENT = 1";
cursor.execute(sql)
connection.commit();

# Links are cleaned up ON DELETE CASCADE
sql = "ALTER TABLE `lti_link` AUTO_INCREMENT = 1";
cursor.execute(sql)
connection.commit();

# sql = "SELECT * FROM `lti_user`"
# cursor.execute(sql)
# result = cursor.fetchone()
# print(result)

print('Yo')

post = {};
post.update(POST.core);
post.update(POST.inst);


client = Client('12345', client_secret='secret', signature_type='BODY')

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

url = 'http://localhost:8888/tsugi/mod/map/index.php';

uri, headers, body = client.sign(url, 'POST', post, header);

print(uri)
print(headers)
print(body)

r = requests.post(url, data=body, headers=headers)
# print(r.text)

