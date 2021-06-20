import requests, pickle
import sys
import json
import random
import time
import re
from datetime import datetime
import os

class Credentials:
    def __init__(self):
        if os.environ.get('INSTA_USERNAME') and os.environ.get('INSTA_PASSWORD'):
            self.username = os.environ.get('INSTA_USERNAME')
            self.password = os.environ.get('INSTA_PASSWORD')
        elif len(sys.argv) > 1:
            self.username = sys.argv[1]
            self.password = sys.argv[2]
        elif 1==1:
            self.username = 'mayur._gajjar'
            self.password = 'mngajjar'
        else:
            sys.exit('Please provide INSTA_USERNAME and INSTA_PASSWORD environement variables or as an argument as such: ./insta-unfollower.py USERNAME PASSWORD.\nAborting...')

credentials = Credentials()

cache_dir = 'cache'

unfollow_users_cache = '%s/unfollowers.json' % (cache_dir)

instagram_url = 'https://www.instagram.com'
login_route = '%s/accounts/login/ajax/' % (instagram_url)
profile_route = '%s/%s/'
query_route = '%s/graphql/query/' % (instagram_url)
unfollow_route = '%s/web/friendships/%s/unfollow/'

session = requests.Session()

def login():
    session.headers.update({
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'www.instagram.com',
        'Origin': 'https://www.instagram.com',
        'Referer': 'https://www.instagram.com/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'),
        'X-Instagram-AJAX': '7a3a3e64fa87',
        'X-Requested-With': 'XMLHttpRequest'
    })

    reponse = session.get(instagram_url)

    csrf = re.findall(r"csrf_token\":\"(.*?)\"", reponse.text)[0]
    if csrf:
        session.headers.update({
            'x-csrftoken': csrf
        })
    else:
        print("No csrf token found in cookies, maybe you are temp ban? Wait 1 hour and retry")
        return False

    time.sleep(random.randint(2, 6))

    post_data = {
        'username': credentials.username,
        'enc_password': '#PWD_INSTAGRAM_BROWSER:0:{}:{}'.format(int(datetime.now().timestamp()), credentials.password)
    }

    response = session.post(login_route, data=post_data, allow_redirects=True)
    response_data = json.loads(response.text)

    if 'two_factor_required' in response_data:
        print('Please disable 2-factor authentication to login.')
        sys.exit(1)

    if 'message' in response_data and response_data['message'] == 'checkpoint_required':
        print('Please check Instagram app for a security confirmation that it is you trying to login.')
        sys.exit(1)

    return response_data['authenticated']

def get_user_profile(username):
    response = session.get(profile_route % (instagram_url, username))
    extract = re.search(r'window._sharedData = (.+);</script>', str(response.text))
    response = json.loads(extract.group(1))
    return response['entry_data']['ProfilePage'][0]['graphql']['user']

def unfollow(user):
    response = session.get(profile_route % (instagram_url, user['username']))
    time.sleep(random.randint(2, 4))

    # update header again, idk why it changed
    session.headers.update({
        'x-csrftoken': response.cookies['csrftoken']
    })
    try:
        response = session.post(unfollow_route % (instagram_url, user['id']))
        f = open('res.json', 'w')
        f.write(response.text)
        f.close()
        response = json.loads(response.text)
    except Exception as e:
        print(e)
        return False

    if response['status'] != 'ok':
        print('Error while trying to unfollow {}. Retrying in a bit...'.format(user['username']))
        print('ERROR: {}'.format(response))
        return False
    return True

class Unfollower:
    def __init__(self):
        self.timestamp = time.time()
        self.session_cache = f'{cache_dir}/{self.timestamp}-session.txt'
        self.userlist = {}
        # self.start = start
        # self.end = end

        if not os.path.isdir(cache_dir):
            os.makedirs(cache_dir)

        self.is_logged = login()
        if self.is_logged == False:
            sys.exit('login failed, verify user/password combination')

        with open(f'{self.session_cache}', 'wb') as f:
            pickle.dump(session.cookies, f)

        time.sleep(random.randint(2, 4))

        self.connected_user = get_user_profile(credentials.username)
        print('You\'re now logged as {} ({} followers, {} following)'.format(self.connected_user['username'], self.connected_user['edge_followed_by']['count'], self.connected_user['edge_follow']['count']))

        if os.path.isfile('cache/formatted_users.json'):
            self.userlist = json.load(open('cache/formatted_users.json'))

    def unFollowUser(self, start, end):
        for i in range(start, end):
            user = self.userlist[i]
            result = unfollow(user)
            print(f'Unfollowed: {user["username"]}: ', result)


# IG = Unfollower()
# IG.unFollowUser(0, 50)
