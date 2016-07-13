import requests
import json
from oauthlib.oauth1 import Client
import pymysql
import databaseconfig as CFG

connection = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
pymysql.paramstyle = 'named'

cursor = connection.cursor()

sql = "DELETE FROM lti_user WHERE user_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
cursor.execute(sql)
connection.commit();
print('Removed {} old unittest users'.format(cursor.rowcount))

exit();
# sql = "SELECT * FROM `lti_user`"
# cursor.execute(sql)
# result = cursor.fetchone()
# print(result)

print('Yo')

json_data=open('json/postcore.json').read()
core = json.loads(json_data)
json_data=open('json/post1.json').read()
post1 = json.loads(json_data)
json_data=open('json/post2.json').read()
post2 = json.loads(json_data)
json_data=open('json/post1s.json').read()
post1s = json.loads(json_data)

post = {};
post.update(core);
post.update(post1);


client = Client('12345', client_secret='secret', signature_type='BODY')

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

url = 'http://localhost:8888/tsugi/mod/map/index.php';

uri, headers, body = client.sign(url, 'POST', post, header);

print(uri)
print(headers)
print(body)

r = requests.post(url, data=body, headers=headers)
print(r.text)

