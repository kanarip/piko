# coding: utf-8

import os
from flask import Flask
from flask import session

from flask.ext.oauthlib.client import OAuth

from piko import App
app = App('piko')

oauth = OAuth(app)

def facebook():
    if app.config.get('FACEBOOK_APP_ID', False):
        facebook = oauth.remote_app(
                'facebook',
                register                =   False,
                consumer_key            =   app.config.get('FACEBOOK_APP_ID', None),
                consumer_secret         =   app.config.get('FACEBOOK_APP_SECRET', None),
                request_token_params    =   {'scope': 'email'},
                base_url                =   'https://graph.facebook.com',
                request_token_url       =   None,
                access_token_url        =   '/oauth/access_token',
                access_token_method     =   'GET',
                authorize_url           =   'https://www.facebook.com/dialog/oauth'
            )

        @facebook.tokengetter
        def get_facebook_oauth_token():
            return session.get('facebook_oauth_token')

        return facebook
