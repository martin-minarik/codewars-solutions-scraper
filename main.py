from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def prepare_driver(chrome_user_data_path, profile):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # e.g. C:\Users\<You>\AppData\Local\Google\Chrome\User Data
    options.add_argument(
        fr"--user-data-dir={chrome_user_data_path}")

    options.add_argument(fr'--profile-directory={profile}')  # e.g. Profile 3

    return webdriver.Chrome(options=options)


def main():
    pass


if __name__ == "__main__":
    main()
