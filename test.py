import requests
import json
from oauthlib.oauth1 import Client
import pymysql
import databaseconfig as CFG
import post as POST
import util as U

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
U.cleanunit(connection, cursor)

# sql = "SELECT * FROM `lti_user`"
# cursor.execute(sql)
# result = cursor.fetchone()
# print(result)

print('Yo')

post = {};
post.update(POST.core);
post.update(POST.inst);


client = Client(CFG.oauth_consumer_key, client_secret=CFG.oauth_secret, signature_type='BODY')

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

url = 'http://localhost:8888/tsugi/mod/map/index.php';

uri, headers, body = client.sign(url, 'POST', post, header);

print(uri)
print(headers)
print(body)

r = requests.post(url, data=body, headers=headers)
# print(r.text)

