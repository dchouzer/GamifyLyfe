INSTALLED_APPS += (
    'social_auth',
)

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS += (
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_login_redirect',
)

TWITTER_CONSUMER_KEY         = 'YOUR KEY HERE        '
TWITTER_CONSUMER_SECRET      = 'YOUR SECRET HERE                           '
FACEBOOK_APP_ID              = '299553123569374'
FACEBOOK_API_SECRET          = '83a6bc215286c8c0429d134a2db38d0d'
