# use this file for python you need to execute in django shell
# after Alation installs

import bootstrap_rosemeta # This will load the Django Framework
from django.contrib.auth.models import User
from rosemeta.models.models_user import UserProfile
from rosemeta.models import SiteSettings, OCFConfiguration
from connector_metadata.models.base import Connector
from alation_conf import conf
from alation_license.util import get_b64_license as b64_license
from symbol import return_stmt
from util.site import get_site_id
from api_authentication.models import RefreshToken
import argparse
import requests
import json

def main():
    # Load all the command line options
    parser = argparse.ArgumentParser(
        description='pass action and any parameters required by that action',
        epilog='For use in self hosting automation, NOT for production'
    )
    parser.add_argument('-a', '--action', default='createUser', help='what action we taking?')
    parser.add_argument('-e', '--email_or_user', default='', help='User to add, or configure OCF etc.')
    parser.add_argument('-p', '--password', default='', help='Password for admin login or OCF.')
    parser.add_argument('-u', '--uri', default='', help='URI, e.g. for OCF action')
    parser.add_argument('-d', '--dsid', default='', help='datasource for OCF action')
    cmdargs = parser.parse_args()

    action = cmdargs.action
    print (f'django_bootstrap: attempting to run action {action}')
    
    if 'createUser' == action:
        createUser(cmdargs)
    elif 'saveAAV2_url' == action:
        saveAAV2_url() # no params
    else:
        print ('django_bootstrap: unknown action requested')
        return
  
def createUser(args):
    em = args.email_or_user
    pw = args.password

    print('django_bootstrap: creating admin user: ' + em)
    u = User.objects.create(username=em, email=em) # Create the user object
    u.confirm_email(u.confirmation_key)
    u.set_password(pw)
    u.is_superuser = True
    u.is_active = True
    u.save()

    names = u.username.split('@')[0].split('.') # first and last in array
    fn = names[0][:1].upper() + names[0][1:] or names[0] # extract first name with upper 1st char
    ln = names[1][:1].upper() + names[1][1:] or names[0] # extract last name with lower 1st char
    fullname = fn + ' ' + ln
    print ('django_bootstrap: generated display name from email: ' + fullname)

    up = UserProfile.objects.create(user=u)
    up.assign_role(0)
    up.is_admin = True
    up.knows_features = [u'welcome',
        u'user_profile_modal',
        u'welcome_modal',
        u'welcome_tour_menu']
    up.title='Alation Insider'
    up.description='I was created through a bootstrap. You might say I am a robot like ALLIE.'
    up.display_name=fullname
    up.save()

    # disable auto signups
    # this code effectively toggles the User Signup Moderation Preference in auth
    print ('django_bootstrap: toggling signup moderation prefs')
    policy = SiteSettings.get(key='account_policy')
    policy['moderate_signups'] = True
    SiteSettings.set('account_policy', policy, u)

    # save off a refresh token for api calls
    print ('django_bootstrap: acquiring refresh token')
    raw_token, refresh_token_obj = RefreshToken.generate_token(u, 'tf_sandbox')
    f = open('/home/alation/refresh_token.txt', 'w')
    f.write(raw_token)
    f.close()
    return

def saveAAV2_url():
    # save off the URL to install AAv2 - will use later in user_data
    license = b64_license()
    version_key = conf['alation_analytics-v2.version.version_key']
    data = {
        "license-data": {"license": license},
        "data": {
            "value": version_key,
            "siteid": get_site_id(),
        },
        "operation": "alation_analytics_pkg",
    }
    url = conf['alation_analytics-v2.download.url.prod']
    res = requests.post(url, json=data)
    # except out if request failed for any reason (no connectivity, bad request)
    res.raise_for_status()
    aav2url = res.json()['message']['pkg_url']
    print ('django_bootstrap: url to aav2 tar found and will be saved to /home/alation/aav2_url.txt')
    print (aav2url)
    f = open('/home/alation/aav2_url.txt', 'w')
    f.write(aav2url)
    f.close()
    return

# Run main
if __name__ == "__main__":
    main()
