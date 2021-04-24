import pymysql
import random
from urllib.parse import urlparse
import urllib
import databaseconfig as CFG
import post as POST
import util as U

inp = input('Test Java, Node, PHP, pGphp, or pYthon? ')

if inp.lower().startswith('j') :
    url = 'http://localhost:8080/tsugi-servlet/hello'
elif inp.lower().startswith('n') :
    url = 'http://localhost:3000/lti'
elif inp.lower().startswith('y') :
    url = 'http://localhost:8000/tsugi/default/launch'
elif inp.lower().startswith('g') :
    url = 'http://localhost:8888/pg-tsugi/mod/attend/index.php'
else :
    # This does not work with all tools - use map.
    url = 'http://localhost:8888/tsugi/mod/attend/index.php'

print('Test URL:',url)

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

post = {}
post.update(POST.core)
post.update(POST.inst)
post['resource_link_id'] = link1
post['context_id'] = context1
post['user_id'] = user1

print('Sending a launch with a bad secret... ',end='')
CFG.oauth_secret = 'bad_news'
r = U.launch(CFG,url,post, 302)

redirect = r.headers['Location']
up = urlparse(redirect)
qu = urllib.parse.parse_qs(up.query)
print (qu['lti_errormsg'][0])
# print (qu['detail'][0])


print('Loading secret for',CFG.oauth_consumer_key,'from the database')

sql = 'SELECT secret FROM lti_key WHERE key_key = %s'
cursor.execute(sql, (CFG.oauth_consumer_key, ))
result = cursor.fetchone()
if ( result == None ) :
    print('Unable to load secret for key',CFG.oauth_consumer_key)
    U.abort()
conn.commit()

CFG.oauth_secret = result['secret']

header = {'Content-Type' : 'application/x-www-form-urlencoded'}

print('Sending a launch with a good secret... ',end='')
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Sending minimal launch to check DB persistence... ',end='')
post = {}
post.update(POST.core)
post['resource_link_id'] = link1
post['context_id'] = context1
post['user_id'] = user1
post['roles'] = 'Instructor'

r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing context_title... ',end='')
post['context_title'] = 'Now for something completely dfferent';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing lis_person_contact_email_primary... ',end='')
post['lis_person_contact_email_primary'] = 'p@p.com';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing user_image... ',end='')
post['user_image'] = 'http://www.dr-chuck.com/csev.jpg';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing user_image again... ',end='')
post['user_image'] = 'http://www.dr-chuck.com/csev_old.jpg';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing user_locale... ',end='')
post['launch_presentation_locale'] = 'pt-BR';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

print('Changing user_locale (Again)... ',end='')
post['launch_presentation_locale'] = 'pt-PT';
r = U.launch(CFG,url,post)
U.verifyDb(conn,post)

services = ['ext_memberships_id', 'ext_memberships_url', 'lineitems_url', 'memberships_url']
for service in services:
    for i in range(2):
        x = 'http://example.com/' + service + '#' + str(i)
        print('Changing',service,'to',x,'...',end='')
        if service in post : del post[service]
        if 'custom_'+service in post : del post['custom_'+service]
        if i == 1 and not service.startswith('ext_') : 
            post['custom_'+service] = x
        else:
            post[service] = x
        r = U.launch(CFG,url,post)
        U.verifyDb(conn,post)

