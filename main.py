import requests
import time
import json
from pprint import pprint
from alive_progress import alive_bar
from urllib.parse import urlencode

def get_token():
    app_id = 7410959
    oauth_url = 'https://oauth.vk.com/authorize'
    oauth_params = {
        'client_id': app_id,
        'display': 'page',
        'scope': 'friends, status, wall, groups, stats, offline',
        'response_type': 'token',
        'v': '5.74'
    }

    print('?'.join((oauth_url, urlencode(oauth_params))))

#My token
access_token = '0639aef390b41e4f1c8eb0aca689bc93e7289edb19ab158d99fa4e2c5c241780269cf666d76a566bbb454'

#Netology token
# access_token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'


def get_user_id():
    user_id = input("Input user ID or screen name: ")
    URL = 'https://api.vk.com/method/users.get'
    params = {
        'user_ids': user_id,
        'access_token': access_token,
        'v': '5.52'
    }
    try:
        response = requests.get(URL, params=params)
        user_id = response.json()['response'][0]['id']
        return user_id
    except KeyError:
        print("Incorrect input, try again.")
        user_id = get_user_id()
        return user_id
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)
        user_id = get_user_id()
        return user_id


def get_groups_list(user_id):
    try:
        URL = 'https://api.vk.com/method/groups.get'
        params = {
            'user_id': user_id,
            'access_token': access_token,
            'v': '5.52'
        }
        response = requests.get(URL, params=params)
        groups_list = response.json()['response']['items']
        return groups_list
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)   
        groups_list = get_groups_list(user_id)
        return groups_list


def get_friends_list(user_id):
    try:
        URL = 'https://api.vk.com/method/friends.get'
        params = {
            'user_id': user_id,
            'access_token': access_token,
            'v': '5.52'
        }
        response = requests.get(URL, params=params)
        friends_list = response.json()['response']['items']
        return friends_list
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)   
        friends_list = get_friends_list(user_id)
        return friends_list


def get_friends_list_offset(user_id, offset):
    try:
        URL = 'https://api.vk.com/method/friends.get'
        params = {
            'user_id': user_id,
            'count': 200,
            'offset': offset,
            'access_token': access_token,
            'v': '5.52'
        }
        response = requests.get(URL, params=params)
        friends_list = response.json()['response']['items']
        return friends_list
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)   
        friends_list = get_friends_list_offset(user_id, offset)
        return friends_list


def is_member(output_groups, group_id, friends_list, friends_limit=0):
    friends_list = ", ".join(list(map(lambda x: str(x), friends_list)))
    API = 'https://api.vk.com/method'
    response = requests.get(url=f"{API}/execute",
    params={"code":
    "return API.groups.isMember({'group_id': '" + str(group_id) + "', 'user_ids': '" + friends_list + "'});",
    "access_token": access_token,
    "v": "5.52"
    })
    response = response.json()
    try:
        response = list(map(lambda x: x['member'], response['response']))
        if response.count(1) <= friends_limit:
            output_groups.append(group_id)
            return output_groups
        else:
            return output_groups
    except KeyError:
        print(f"Group ID: {group_id} - {response['error']['error_msg']}")
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)   
        output_groups = is_member(output_groups, group_id, friends_list, friends_limit=0)
        return output_groups


def get_group_info(group_id):
    try:
        URL = 'https://api.vk.com/method/groups.getById'
        params = {
            'group_id': group_id,
            'fields': 'members_count',
            'access_token': access_token,
            'v': '5.52'
        }
        response = requests.get(URL, params=params)
        group_dict = {}
        group_dict['name'] = response.json()['response'][0]['name']
        group_dict['id'] = response.json()['response'][0]['id']
        group_dict['members_count'] = response.json()['response'][0]['members_count']
        return group_dict
    except requests.exceptions.ReadTimeout:
        print("\n Reconnecting to server. \n")
        time.sleep(3)   
        group_dict = get_group_info(group_id)
        return group_dict


def input_limit():
    friends_limit = input("Count groups with X or less friends in it: ")
    try:
        return int(friends_limit)
    except:
        print("You should input a number!")
        friends_limit = input_limit()
        return int(friends_limit)


def match_groups_friends(friends_list, groups_list, friends_limit, user_id):
    output_groups = []
    if len(friends_list) <= 200:
        with alive_bar(len(groups_list)) as bar:
            print("\nMatching friends and groups...")
            for group in groups_list:
                bar()
                output_groups = is_member(output_groups, group, friends_list, friends_limit)
                time.sleep(0.4)
        return output_groups
    else:
        print("User has more than 200 friends, it could take some time.")
        offset = 0
        friends_list = get_friends_list_offset(user_id, offset)
        while len(friends_list) != 0:
            with alive_bar(len(groups_list)) as bar:
                print("\nMatching friends and groups...")
                for group in groups_list:
                    bar()
                    output_groups = is_member(output_groups, group, friends_list, friends_limit)
                    time.sleep(0.4)
            offset += 200
            friends_list = get_friends_list_offset(user_id, offset)
        return output_groups


def write_json(output_groups):
    output_groups = set(output_groups)
    output_list = []
    with alive_bar(len(output_groups)) as bar:
        print("\nGetting groups info...")
        for group in output_groups:
            bar()
            output_list.append(get_group_info(group))
            time.sleep(0.4)
    
    with open('groups.json', 'w') as groups_file:
        json.dump(output_list, groups_file, ensure_ascii=False, indent=4)


# eshmargunov = id 171691064

if __name__ == "__main__":
    user_id = get_user_id()
    friends_list = get_friends_list(user_id)
    groups_list = get_groups_list(user_id)
    friends_limit = input_limit()

    output_groups = match_groups_friends(friends_list, groups_list, friends_limit, user_id)
    write_json(output_groups)

    print('\nDone! All information was saved to "groups.json" file.')
    