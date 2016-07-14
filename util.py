import databaseconfig as CFG
import requests
from oauthlib.oauth1 import Client

def cleanunit(connection, cursor) :
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

def launch(url, post) :
    global CFG
    header = {'Content-Type' : 'application/x-www-form-urlencoded'}
    client = Client(CFG.oauth_consumer_key, client_secret=CFG.oauth_secret, signature_type='BODY')
    uri, headers, body = client.sign(url, 'POST', post, header)
    r = requests.post(url, data=body, headers=headers, allow_redirects=False)
    if ( r.status_code == 302 ) :
        new_url = r.headers.get('Location', False);
        print('New Url',new_url);
        error_url = post.get('launch_presentation_return_url', False)
        print('Error url',error_url);
        if ( new_url.startswith(error_url) ) :
            print('Redirect to return_url')
            return r
        r = requests.get(new_url);
    return r
