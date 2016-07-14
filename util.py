import requests
from oauthlib.oauth1 import Client

def cleanunit(conn, cursor) :
    sql = "DELETE FROM lti_user WHERE user_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
    cursor.execute(sql)
    conn.commit();
    print('Removed {} old unittest users'.format(cursor.rowcount))
    sql = "ALTER TABLE `lti_user` AUTO_INCREMENT = 1";
    cursor.execute(sql)
    conn.commit();

    sql = "DELETE FROM lti_context WHERE context_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
    cursor.execute(sql)
    conn.commit();
    print('Removed {} old unittest contexts'.format(cursor.rowcount))
    sql = "ALTER TABLE `lti_context` AUTO_INCREMENT = 1";
    cursor.execute(sql)
    conn.commit();

    # Links are cleaned up ON DELETE CASCADE
    sql = "ALTER TABLE `lti_link` AUTO_INCREMENT = 1";
    cursor.execute(sql)
    conn.commit();

def launch(CFG,url, post) :
    header = {'Content-Type' : 'application/x-www-form-urlencoded'}
    client = Client(CFG.oauth_consumer_key, client_secret=CFG.oauth_secret, signature_type='BODY')
    uri, headers, body = client.sign(url, 'POST', post, header)
    r = requests.post(url, data=body, headers=headers, allow_redirects=False)
    if ( r.status_code == 302 ) :
        new_url = r.headers.get('Location', False);
        # print('New Url',new_url);
        error_url = post.get('launch_presentation_return_url', False)
        # print('Error url',error_url);
        if ( new_url.startswith(error_url) ) :
            # print('Redirect to return_url')
            return r
        r = requests.get(new_url);
    return r

def dumpr(r) :
    print(r.status_code)
    print(r.headers)
    print(r.text)

def getrow(conn,post,post_key,table) :
    cursor = conn.cursor()
    key = post.get(post_key, False)
    if key is False :
        print('Could not find',post_key,'in POST data')
        exit();
    sql = "SELECT * FROM lti_"+table+" WHERE "+table+"_key = %s"
    cursor.execute(sql, (key, ))
    result = cursor.fetchone()
    conn.commit()
    cursor.close();
    return result

def getuser(conn, post) :
    return getrow(conn,post,'user_id', 'user')

def getcontext(conn, post) :
    return getrow(conn,post,'context_id', 'context')

def getmembership(conn,user,context) :
    user_id = user.get('user_id',False)
    if user_id is False :
        print('Could not find user_id')
        exit();
    context_id = context.get('context_id',False)
    if context_id is False :
        print('Could not find context_id')
        exit();
    cursor = conn.cursor()
    sql = "SELECT * FROM lti_membership WHERE user_id = %s AND context_id = %s"
    cursor.execute(sql, (user_id, context_id))
    result = cursor.fetchone()
    conn.commit()
    cursor.close();
    return result

