import requests
import json
from oauthlib.oauth1 import Client
import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             port=8889,
                             user='ltiuser',
                             password='ltipassword',
                             db='tsugi',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
print(connection)

try:
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT * FROM `lti_user`"
        # cursor.execute(sql, ('webmaster@python.org',))
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
finally:
    connection.close()

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

