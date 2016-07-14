import pymysql
import databaseconfig as CFG
import post as POST
import util as U

url = 'http://localhost:8888/tsugi/mod/map/index.php'

connection = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

# Clean up old unit test users and contexts
U.cleanunit(connection, cursor)

print('Sending a launch with a bad secret... ',end='')

post = {}
post.update(POST.core)
post.update(POST.inst)

r = U.launch(url,post)
if ( r.status_code != 302 ) :
    print('Expected a redirect to the error URL')
    U.dumpr(r)
    exit();

print('Received 302 - Success')

print('Loading secret for',CFG.oauth_consumer_key,'from the database')

sql = "SELECT secret FROM lti_key WHERE key_key = %s"
cursor.execute(sql, (CFG.oauth_consumer_key, ))
result = cursor.fetchone()
if ( result == None ) :
    print('Unable to load secret for key',CFG.oauth_consumer_key)
    exit()

CFG.oauth_secret = result['secret'];

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

print('Sending a launch with a good secret... ',end='');

r = U.launch(url,post)
if ( r.status_code != 200 ) :
    print('Launch failed')
    U.dumpr(r);
    exit();

print("Received 200 - Success");


