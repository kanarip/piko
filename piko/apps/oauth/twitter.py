# coding: utf-8

import os
from flask import Flask
from flask import session

from flask.ext.oauthlib.client import OAuth

from piko import App
app = App('piko')

oauth = OAuth(app)

def twitter():
    if app.config.get('TWITTER_API_KEY', False):
        twitter = oauth.remote_app(
                'twitter',
                register = False,
                consumer_key = app.config.get('TWITTER_API_KEY', None),
                consumer_secret = app.config.get('TWITTER_API_SECRET', None),
                base_url = 'https://api.twitter.com/1.1/',
                request_token_url = 'https://api.twitter.com/oauth/request_token',
                access_token_url = 'https://api.twitter.com/oauth/access_token',
                authorize_url = 'https://api.twitter.com/oauth/authenticate',
            )

        @twitter.tokengetter
        def get_twitter_token():
            if 'twitter_oauth' in session:
                resp = session['twitter_oauth_token']
                return resp['oauth_token'], resp['oauth_token_secret']

        return twitter
