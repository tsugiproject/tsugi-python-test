import pymysql
import databaseconfig as CFG
import post as POST
import util as U

url = 'http://localhost:8888/tsugi/mod/map/index.php';

connection = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
pymysql.paramstyle = 'named'

cursor = connection.cursor()

U.cleanunit(connection, cursor)

# sql = "SELECT * FROM `lti_user`"
# cursor.execute(sql)
# result = cursor.fetchone()
# print(result)

print('Yo')

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

post = {};
post.update(POST.core);
post.update(POST.inst);

CFG.oauth_secret = "secret";
r = U.launch(url,post)
print(r.status_code)
print(r.headers)
print(r.text)


