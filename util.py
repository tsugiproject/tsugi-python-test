import requests
import re
from oauthlib.oauth1 import Client

def cleanunit(conn, cursor) :
    sql = "DELETE FROM lti_user WHERE user_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
    cursor.execute(sql)
    conn.commit()
    print('Removed {} old unittest users'.format(cursor.rowcount))
    sql = "ALTER TABLE `lti_user` AUTO_INCREMENT = 1"
    cursor.execute(sql)
    conn.commit()

    sql = "DELETE FROM lti_context WHERE context_key LIKE 'unittest:%' AND key_id IN (SELECT key_id from lti_key WHERE key_key='12345')"
    cursor.execute(sql)
    conn.commit()
    print('Removed {} old unittest contexts'.format(cursor.rowcount))
    sql = "ALTER TABLE `lti_context` AUTO_INCREMENT = 1"
    cursor.execute(sql)
    conn.commit()

    # Links are cleaned up ON DELETE CASCADE
    sql = "ALTER TABLE `lti_link` AUTO_INCREMENT = 1"
    cursor.execute(sql)
    conn.commit()

def launch(CFG,url, post) :
    header = {'Content-Type' : 'application/x-www-form-urlencoded'}
    client = Client(CFG.oauth_consumer_key, client_secret=CFG.oauth_secret, signature_type='BODY')
    uri, headers, body = client.sign(url, 'POST', post, header)
    r = requests.post(url, data=body, headers=headers, allow_redirects=False)
    if ( r.status_code == 302 ) :
        new_url = r.headers.get('Location', False)
        # print('New Url',new_url)
        error_url = post.get('launch_presentation_return_url', False)
        # print('Error url',error_url)
        if ( new_url.startswith(error_url) ) :
            # print('Redirect to return_url')
            return r
        r = requests.get(new_url)
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
        exit()
    sql = "SELECT * FROM lti_"+table+" WHERE "+table+"_key = %s"
    cursor.execute(sql, (key, ))
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return result

def getuser(conn, post) :
    return getrow(conn,post,'user_id', 'user')

def getcontext(conn, post) :
    return getrow(conn,post,'context_id', 'context')

def getlink(conn, post) :
    return getrow(conn,post,'resource_link_id', 'link')

def getmembership(conn,user,context) :
    user_id = user.get('user_id',False)
    if user_id is False :
        print('Could not find user_id')
        exit()
    context_id = context.get('context_id',False)
    if context_id is False :
        print('Could not find context_id')
        exit()
    cursor = conn.cursor()
    sql = "SELECT * FROM lti_membership WHERE user_id = %s AND context_id = %s"
    cursor.execute(sql, (user_id, context_id))
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return result

def getresult(conn,user,link) :
    user_id = user.get('user_id',False)
    if user_id is False :
        print('Could not find user_id')
        exit()
    link_id = link.get('link_id',False)
    if link_id is False :
        print('Could not find link_id')
        exit()
    cursor = conn.cursor()
    sql = "SELECT R.*,S.service_key FROM lti_result AS R LEFT JOIN lti_service as S ON R.service_id = S.service_id WHERE R.user_id = %s AND R.link_id = %s"
    cursor.execute(sql, (user_id, link_id))
    result = cursor.fetchone()
    conn.commit()
    cursor.close()
    return result

def switch(di,old,new) :
    if old not in di : return
    di[new] = di[old]
    del(di[old])

def mapuser(user) :
    ret = user
    switch(ret,'displayname','user_displayname')
    switch(ret,'email','user_email')
    return ret

def mapcontext(context) :
    ret = context
    switch(ret,'title','context_title')
    switch(ret,'settings_url','context_settings_url')
    return ret

def maplink(link) :
    ret = link
    switch(ret,'title','link_title')
    switch(ret,'settings_url','link_settings_url')
    return ret

def mapresult(result) :
    ret = result
    switch(ret,'service_key','service')
    return ret

def extractDb(conn,post):
    u = getuser(conn, post)
    c = getcontext(conn, post)
    l = getlink(conn, post)
    m = getmembership(conn, u, c)
    r = getresult(conn, u, l)
    ext = dict()
    ext.update(mapuser(u))
    ext.update(mapcontext(c))
    ext.update(maplink(l))
    ext.update(mapresult(r))
    ext.update(m)
    return ext

def extractPost(post) :
    fixed = dict()
    for (k,v) in post.items():
        if k.startswith('custom_') : 
            nk = k[7:]
            if v.startswith('$') :
                sv = v[1:].lower().replace('.','_')
                if sv == nk : continue
            if nk not in fixed : fixed[nk] = v
        fixed[k] = v

    #print(fixed)
    ret = dict()

    link_key = fixed.get('resource_link_id', None)
    link_key = fixed.get('custom_resource_link_id', link_key)
    ret['link_key'] = link_key

    user_key = fixed.get('person_sourcedid', None)
    user_key = fixed.get('user_id', user_key)
    user_key = fixed.get('custom_user_id', user_key)
    ret['user_key'] = user_key

    context_key = fixed.get('courseoffering_sourcedid', None)
    context_key = fixed.get('context_id', context_key)
    context_key = fixed.get('custom_context_id', context_key)
    ret['context_key'] = context_key

    # LTI 1.x settings and Outcomes
    ret['service'] = fixed.get('lis_outcome_service_url', None)
    ret['sourcedid'] = fixed.get('lis_result_sourcedid', None)

    # LTI 2.x settings and Outcomes
    ret['result_url'] = fixed.get('custom_result_url', None)
    ret['link_settings_url'] = fixed.get('custom_link_settings_url', None)
    ret['context_settings_url'] = fixed.get('custom_context_settings_url', None)

    ret['context_title'] = fixed.get('context_title', None)
    ret['link_title'] = fixed.get('resource_link_title', None)

    # Getting email from LTI 1.x and LTI 2.x
    ret['user_email'] = fixed.get('lis_person_contact_email_primary', None)
    ret['user_email'] = fixed.get('custom_person_email_primary', ret['user_email'])

    # Displayname from LTI 2.x
    if ( fixed.get('custom_person_name_full') ) :
        ret['user_displayname'] = fixed['custom_person_name_full']
    elif ( fixed.get('custom_person_name_given') and fixed.get('custom_person_name_family') ) :
        ret['user_displayname'] = fixed['custom_person_name_given']+' '+fixed['custom_person_name_family']
    elif ( fixed.get('custom_person_name_given') ) :
        ret['user_displayname'] = fixed['custom_person_name_given']
    elif ( fixed.get('custom_person_name_family') ) :
        ret['user_displayname'] = fixed['custom_person_name_family']

    # Displayname from LTI 1.x
    elif ( fixed.get('lis_person_name_full') ) :
        ret['user_displayname'] = fixed['lis_person_name_full']
    elif ( fixed.get('lis_person_name_given') and fixed.get('lis_person_name_family') ) :
        ret['user_displayname'] = fixed['lis_person_name_given']+' '+fixed['lis_person_name_family']
    elif ( fixed.get('lis_person_name_given') ) :
        ret['user_displayname'] = fixed['lis_person_name_given']
    elif ( fixed.get('lis_person_name_family') ) :
        ret['user_displayname'] = fixed['lis_person_name_family']

    # Trim out repeated spaces and/or weird whitespace from the user_displayname
    if ( ret.get('user_displayname') ) :
        ret['user_displayname'] = re.sub( '\s+', ' ', ret.get('user_displayname') ).strip()

    # Get the role
    ret['role'] = 0
    roles = ''
    if ( fixed.get('custom_membership_role') ) : # From LTI 2.x
        roles = fixed['custom_membership_role']
    elif ( fixed.get('roles') ) : # From LTI 1.x
        roles = fixed['roles']

    if ( len(roles) > 0 ) :
        roles = roles.lower()
        if ( roles.find('instructor') is not False ) : ret['role'] = 1
        if ( roles.find('administrator') is not False ) : ret['role'] = 1

    return ret

def verifyDb(conn,post) :
    extract = extractPost(post)
    db = extractDb(conn, post)
    for (k,v) in extract.items() :
        # Might want to fix this...
        if k == 'resource_link_description' : continue
        if k.startswith('launch_') : continue
        if k.startswith('tool_') : continue
        if k not in db:
            print('Missing post key in database',k)
            print('------ Post')
            print(extract)
            print('------ Db')
            print(db)
            exit()
