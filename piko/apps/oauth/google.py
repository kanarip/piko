# coding: utf-8

import os
from flask import Flask
from flask import session

from flask.ext.oauthlib.client import OAuth

from piko import App
app = App('piko')

oauth = OAuth(app)

def google():
    if app.config.get('GOOGLE_CLIENT_ID', False):
        google = oauth.remote_app(
                'google',
                consumer_key            =   app.config.get('GOOGLE_CLIENT_ID', None),
                consumer_secret         =   app.config.get('GOOGLE_CLIENT_SECRET', None),
                request_token_params    =   {
                        'scope': 'https://www.googleapis.com/auth/userinfo.email'
                    },

                base_url                =   'https://www.googleapis.com/oauth2/v1/',
                request_token_url       =    None,
                access_token_method     =   'POST',
                access_token_url        =   'https://accounts.google.com/o/oauth2/token',
                authorize_url           =   'https://accounts.google.com/o/oauth2/auth',
            )

        @google.tokengetter
        def get_google_oauth_token():
            return session.get('google_oauth_token')

        return google
