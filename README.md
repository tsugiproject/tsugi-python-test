
A Functionality Test for Tsugi
==============================

The idea is to develop a functionality / integration test that can
test any version of Tsugi in any language.

This is early days :)

Install pip (if necessary):

    https://pip.pypa.io/en/stable/installing/

    curl -O https://bootstrap.pypa.io/get-pip.py
    python get-pip.py

Install packages

    pip3 install --user requests
    pip3 install --user oauthlib
    pip3 install --user PyMySQL

Run:

    python3 test.py

Notes:

    http://docs.python-requests.org/en/master/
    http://pymysql.readthedocs.io/en/latest/user/examples.html
    https://github.com/idan/oauthlib/blob/master/oauthlib/oauth1/rfc5849/__init__.py

TODO: Lots of stuff
