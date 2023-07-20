from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tomllib


def load_config():
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)

    match config:
        case {
            "chrome_user_data_path": str(),
            "chrome_profile": str()
        }:
            pass
        case _:
            raise ValueError(f"invalid configuration: {config}")

    return config


def prepare_driver(user_data_path, profile):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # e.g. C:\Users\<You>\AppData\Local\Google\Chrome\User Data
    options.add_argument(
        fr"--user-data-dir={user_data_path}")

    options.add_argument(fr'--profile-directory={profile}')  # e.g. Profile 3

    return webdriver.Chrome(options=options)


def main():
    config = load_config()
    driver = prepare_driver(user_data_path=config["chrome_user_data_path"], profile=config["chrome_profile"])


if __name__ == "__main__":
    main()
