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

def getlink(conn, post) :
    return getrow(conn,post,'resource_link_id', 'link')

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

'''
    $retval['key'] = isset($FIXED['oauth_consumer_key']) ? $FIXED['oauth_consumer_key'] : null;
    $retval['nonce'] = isset($FIXED['oauth_nonce']) ? $FIXED['oauth_nonce'] : null;
    $link_id = isset($FIXED['resource_link_id']) ? $FIXED['resource_link_id'] : null;
    $link_id = isset($FIXED['custom_resource_link_id']) ? $FIXED['custom_resource_link_id'] : $link_id;
    $retval['link_id'] = $link_id;

    $user_id = isset($FIXED['person_sourcedid']) ? $FIXED['person_sourcedid'] : null;
    $user_id = isset($FIXED['user_id']) ? $FIXED['user_id'] : $user_id;
    $user_id = isset($FIXED['custom_user_id']) ? $FIXED['custom_user_id'] : $user_id;
    $retval['user_id'] = $user_id;

    $context_id = isset($FIXED['courseoffering_sourcedid']) ? $FIXED['courseoffering_sourcedid'] : null;
    $context_id = isset($FIXED['context_id']) ? $FIXED['context_id'] : $context_id;
    $context_id = isset($FIXED['custom_context_id']) ? $FIXED['custom_context_id'] : $context_id;
    $retval['context_id'] = $context_id;

    // Sanity checks
    if ( ! $retval['key'] ) return false;
    if ( ! $retval['nonce'] ) return false;
    if ( in_array(self::USER, $needed) && ! $retval['user_id'] ) return false;
    if ( in_array(self::CONTEXT, $needed) && ! $retval['context_id'] ) return false;
    if ( in_array(self::LINK, $needed) && ! $retval['link_id'] ) return false;

    // LTI 1.x settings and Outcomes
    $retval['service'] = isset($FIXED['lis_outcome_service_url']) ? $FIXED['lis_outcome_service_url'] : null;
    $retval['sourcedid'] = isset($FIXED['lis_result_sourcedid']) ? $FIXED['lis_result_sourcedid'] : null;

    // LTI 2.x settings and Outcomes
    $retval['result_url'] = isset($FIXED['custom_result_url']) ? $FIXED['custom_result_url'] : null;
    $retval['link_settings_url'] = isset($FIXED['custom_link_settings_url']) ? $FIXED['custom_link_settings_url'] : null;
    $retval['context_settings_url'] = isset($FIXED['custom_context_settings_url']) ? $FIXED['custom_context_settings_url'] : null;

    $retval['context_title'] = isset($FIXED['context_title']) ? $FIXED['context_title'] : null;
    $retval['link_title'] = isset($FIXED['resource_link_title']) ? $FIXED['resource_link_title'] : null;

    // Getting email from LTI 1.x and LTI 2.x
    $retval['user_email'] = isset($FIXED['lis_person_contact_email_primary']) ? $FIXED['lis_person_contact_email_primary'] : null;
    $retval['user_email'] = isset($FIXED['custom_person_email_primary']) ? $FIXED['custom_person_email_primary'] : $retval['user_email'];

    // Displayname from LTI 2.x
    if ( isset($FIXED['person_name_full']) ) {
        $retval['user_displayname'] = $FIXED['custom_person_name_full'];
    } else if ( isset($FIXED['custom_person_name_given']) && isset($FIXED['custom_person_name_family']) ) {
        $retval['user_displayname'] = $FIXED['custom_person_name_given'].' '.$FIXED['custom_person_name_family'];
    } else if ( isset($FIXED['custom_person_name_given']) ) {
        $retval['user_displayname'] = $FIXED['custom_person_name_given'];
    } else if ( isset($FIXED['custom_person_name_family']) ) {
        $retval['user_displayname'] = $FIXED['custom_person_name_family'];

    // Displayname from LTI 1.x
    } else if ( isset($FIXED['lis_person_name_full']) ) {
        $retval['user_displayname'] = $FIXED['lis_person_name_full'];
    } else if ( isset($FIXED['lis_person_name_given']) && isset($FIXED['lis_person_name_family']) ) {
        $retval['user_displayname'] = $FIXED['lis_person_name_given'].' '.$FIXED['lis_person_name_family'];
    } else if ( isset($FIXED['lis_person_name_given']) ) {
        $retval['user_displayname'] = $FIXED['lis_person_name_given'];
    } else if ( isset($FIXED['lis_person_name_family']) ) {
        $retval['user_displayname'] = $FIXED['lis_person_name_family'];
    }

    // Trim out repeated spaces and/or weird whitespace from the user_displayname
    if ( isset($retval['user_displayname']) ) {
        $retval['user_displayname'] = trim(preg_replace('/\s+/', ' ',$retval['user_displayname']));
    }

    // Get the role
    $retval['role'] = 0;
    $roles = '';
    if ( isset($FIXED['custom_membership_role']) ) { // From LTI 2.x
        $roles = $FIXED['custom_membership_role'];
    } else if ( isset($FIXED['roles']) ) { // From LTI 1.x
        $roles = $FIXED['roles'];
    }

    if ( strlen($roles) > 0 ) {
        $roles = strtolower($roles);
        if ( ! ( strpos($roles,'instructor') === false ) ) $retval['role'] = 1;
        if ( ! ( strpos($roles,'administrator') === false ) ) $retval['role'] = 1;
    }
'''




