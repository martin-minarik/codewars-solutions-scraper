from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tomllib
import locators


def load_config():
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)

    match config:
        case {
            "_session_id": str(),
        }:
            pass
        case _:
            raise ValueError(f"invalid configuration: {config}")

    return config


def prepare_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    return webdriver.Chrome(options=options)


def main():
    config = load_config()
    driver = prepare_driver()

    input("Ready? (Enter)")


if __name__ == "__main__":
    main()
