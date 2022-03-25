import requests
import fake_useragent
import os
import pickle
import http.cookiejar as cookielib

from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS

session = requests.Session()
session.cookie = cookielib.LWPCookieJar()

load_dotenv()

username = os.getenv("kinopub_login")
password = os.getenv("kinopub_pass")

login_link = "https://kino.pub/user/login"

user_agent = fake_useragent.UserAgent()
header = {
    "user-agent": user_agent.random
}

def save_cookies(session, filename="cookies.txt"):
    with open(filename, 'wb') as f:
        pickle.dump(session.cookies, f)


def load_cookies(session, filename="cookies.txt"):
    with open(filename, 'rb') as f:
        session.cookies.update(pickle.load(f))


def parse_csrf(response):
    key = BS(response, 'html.parser')
    for el in key.select("meta"):
        if "csrf-token" in str(el):
            end_index = str(el).find("csrf-token")
            start_index = end_index - 96
            csrf_key = str(el)[start_index:end_index - 8]
            break
    return csrf_key


def post(link, data):
    responce = session.post(link, data=data, headers=header).text
    return responce


def get(link):
    response = session.get(link, headers=header).text
    return response



def parse():
    action = int(input(
    """
    Enter the action:
        1 - Login via cookies
        2 - Sign in
    """
    ))

    if action == 1:
        load_cookies(session)
        response = session.get("https://kino.pub/users/ShyanInc", headers=header)
        html = BS(response.content, 'html.parser')
        nickname = html.select("span._800.h1")[0].text
        print(nickname + ", you successfully logged in!")


    else:
        response = get(login_link)
        csrf_key = parse_csrf(response)

        first_login_data = {
            "_csrf": csrf_key,
            "login-form[rememberMe]": 1,
            "login-form[login]": username,
            "login-form[password]": password
        }

        print("csrf key #1: " + csrf_key)

        login_status = post(login_link, first_login_data)
        response = get(login_link)
        csrf_key = parse_csrf(response)

        print("csrf key #2: " + csrf_key)

        login_code = str(input("Enter the code: "))

        second_login_data = {
            "_csrf": csrf_key,
            "login-form[rememberMe]": 1,
            "login-form[login]": username,
            "login-form[password]": password,
            "login-form[formcode]": login_code
        }

        response = post(login_link, second_login_data)
        main_page = get("https://kino.pub/")

        save_cookies(session)


    profile_link = "https://kino.pub/users/ShyanInc"

if __name__ == "__main__":
    parse()


# r = requests.get("")

# print(r)
# for el in html.select("h3"):
#     if el.get_text():
#         print(el)
