import pymysql
import random
import databaseconfig as CFG
import post as POST
import util as U

url = 'http://localhost:8888/tsugi/mod/map/index.php'
user1 = 'unittest:user:'+str(random.random())
user2 = 'unittest:user:'+str(random.random())
context1 = 'unittest:context:'+str(random.random())
context2 = 'unittest:context:'+str(random.random())
link1 = 'unittest:link:'+str(random.random())
link2 = 'unittest:link:'+str(random.random())
link3 = 'unittest:link:'+str(random.random())

conn = pymysql.connect(host=CFG.host,
                             port=CFG.port,
                             user=CFG.user,
                             password=CFG.password,
                             db=CFG.db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = conn.cursor()

# Clean up old unit test users and contexts
U.cleanunit(conn, cursor)

print('Sending a launch with a bad secret... ',end='')

post = {}
post.update(POST.core)
post.update(POST.inst)
post['resource_link_id'] = link1
post['context_id'] = context1
post['user_id'] = user1

CFG.oauth_secret = "bad_news"
r = U.launch(CFG,url,post)
if ( r.status_code != 302 ) :
    print('Expected a redirect to the error URL')
    U.dumpr(r)
    exit()

print('Received 302 - Success')

print('Loading secret for',CFG.oauth_consumer_key,'from the database')

sql = "SELECT secret FROM lti_key WHERE key_key = %s"
cursor.execute(sql, (CFG.oauth_consumer_key, ))
result = cursor.fetchone()
if ( result == None ) :
    print('Unable to load secret for key',CFG.oauth_consumer_key)
    exit()
conn.commit()

CFG.oauth_secret = result['secret']

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

print('Sending a launch with a good secret... ',end='')

r = U.launch(CFG,url,post)
if ( r.status_code != 200 ) :
    print('Launch failed')
    U.dumpr(r)
    exit()

print("Received 200 - Success")

u = U.getuser(conn, post)
print(u)

c = U.getcontext(conn, post)
print(c)

m = U.getmembership(conn, u, c)
print(m)

