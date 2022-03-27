import requests
import fake_useragent
import os
import pickle

from dotenv import load_dotenv
from bs4 import BeautifulSoup as BS


login_link = "https://kino.pub/user/login"
main_page_link = "https://kino.pub"


def parse_csrf(response):
    key = BS(response.content, 'html.parser')
    for el in key.select("meta"):
        if "csrf-token" in str(el):
            end_index = str(el).find("csrf-token")
            start_index = end_index - 96
            csrf_key = str(el)[start_index:end_index - 8]
            break
    return csrf_key


class App:

    def __init__(self):
        load_dotenv()

        self.user_agent = fake_useragent.UserAgent()
        self.header = {
            "user-agent": self.user_agent.random
        }

        self.session = requests.Session()
        self.login_username = os.getenv("kinopub_login")
        self.login_password = os.getenv("kinopub_pass")

        self.username = None
        self.email = None

    def save_cookies(self, filename="cookies.txt"):
        with open(filename, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def load_cookies(self, filename="cookies.txt"):
        with open(filename, 'rb') as f:
            self.session.cookies.update(pickle.load(f))

    def post_request(self, link, data):
        response = self.session.post(link, data=data, headers=self.header)
        return response

    def get_request(self, link):
        response = self.session.get(link, headers=self.header)
        return response

    def login(self, new_login=False):
        if not new_login:
            self.load_cookies()

        response = self.get_request(main_page_link)
        soup = BS(response.content, 'html.parser')
        dropdown_menu = soup.find("div", class_=["dropdown-menu", "dropdown-menu-right"])
        profile_link = dropdown_menu.select_one("a").get("href")

        response = self.get_request(main_page_link + profile_link)
        soup = BS(response.content, 'html.parser')
        user_info_block = soup.find("div", class_=["p-l-md", "no-padding-xs"])
        user_email_div = user_info_block.select_one("div").text

        self.username = user_info_block.select_one("span").text
        self.email = user_email_div[7:]

        print(self.username + ", you successfully logged in!")

    def new_login(self):
        response = self.get_request(login_link)
        csrf_key = parse_csrf(response)

        first_login_data = {
            "_csrf": csrf_key,
            "login-form[rememberMe]": 1,
            "login-form[login]": self.login_username,
            "login-form[password]": self.login_password
        }

        print("csrf key #1: " + csrf_key)

        login_status = self.post_request(login_link, first_login_data)
        response = self.get_request(login_link)
        csrf_key = parse_csrf(response)

        print("csrf key #2: " + csrf_key)

        login_code = str(input("Enter the code: "))

        second_login_data = {
            "_csrf": csrf_key,
            "login-form[rememberMe]": 1,
            "login-form[login]": self.login_username,
            "login-form[password]": self.login_password,
            "login-form[formcode]": login_code
        }

        self.post_request(login_link, second_login_data)
        self.save_cookies()
        self.login(True)

    def parse_movies(self):
        response = self.get_request(f"{main_page_link}/watchlist/{self.username}")
        soup = BS(response.content, "html.parser")
        items_block = soup.find("div", class_="page-content")
        items_div = items_block.findAll("div")
        items_list = items_div[4].findAll("div")

        movies_list = []
        for div in items_list:
            item_info = div.find("div", class_="item-info")
            item_poster = div.find("div", class_="item-poster")

            try:
                movie_name = item_info.select_one("div > a").text
                movie_remaining_episodes = item_poster.select_one("div > span").text
                movie_rating = item_poster.select_one(".bottomcenter-2x > span > a").text
                movie_link = item_poster.select_one("a").get("href")
                kp_link = item_poster.select_one(".bottomcenter-2x > span > a").get("href")
            except AttributeError:
                continue

            movies_list.append({"Name": movie_name,
                                "Rating": movie_rating.strip(),
                                "Remaining_Episodes": movie_remaining_episodes.strip(),
                                "KinoPub_Link": main_page_link + movie_link,
                                "KinoPoisk_Link": kp_link})
        return movies_list

    def run(self):
        while True:
            action = int(input("Enter the action:\n"
                               "1 - Login via cookies\n"
                               "2 - Sign in\n"
                               "3 - Quit\n"))
            if action == 1:
                self.login()
                break
            elif action == 2:
                self.new_login()
                break
            elif action == 3:
                exit()
            else:
                print("Wrong action!")

        while True:
            action = int(input("Enter the action:\n"
                               "1 - Watchlist\n"
                               "2 - Exit\n"))
            # Movies List From WatchList
            if action == 1:
                movies_list = self.parse_movies()
                dash = "-------------------------------------------------------------------------\n"
                is_save = bool(input("Save the result to file? 1 for yes, 0 for no:"))
                if is_save:
                    open("movies.txt", "w")
                for movie in movies_list:
                    movie_info = dash + \
                          f"Name: {movie['Name']}\n" \
                          f"KinoPoisk Rating: {movie['Rating']}\n" \
                          f"Remaining episodes: {movie['Remaining_Episodes']}\n" \
                          f"KinoPub Link: {movie['KinoPub_Link']}\n" \
                          f"KinoPoisk Link: {movie['KinoPoisk_Link']}\n"
                    print(movie_info, end="")
                    if is_save:
                        with open("movies.txt", "a") as file:
                            file.write(movie_info)

                if is_save:
                    with open("movies.txt", "a") as file:
                        file.write(dash)
                print("-------------------------------------------------------------------------")
            elif action == 2:
                exit()


if __name__ == "__main__":
    app = App()
    app.run()
