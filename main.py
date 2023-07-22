from selenium import webdriver
import tomllib
from types import SimpleNamespace
from selenium.webdriver.support.wait import WebDriverWait
from utils import enter_codewars, enter_solutions_page, scrape_solutions, save_solutions


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


def prepare_context():
    config = load_config()
    driver = prepare_driver()
    driver.implicitly_wait(3)

    wait = WebDriverWait(driver, timeout=60, poll_frequency=1)

    first_tab_handle = driver.current_window_handle
    driver.execute_script("window.open('about:blank','image_tab');")
    driver.switch_to.window(driver.window_handles[-1])
    second_tab_handle = driver.current_window_handle
    driver.switch_to.window(first_tab_handle)

    return SimpleNamespace(config=config,
                           driver=driver,
                           wait=wait,
                           first_tab_handle=first_tab_handle,
                           second_tab_handle=second_tab_handle
                           )


def main():
    context = prepare_context()
    enter_codewars(context)
    enter_solutions_page(context)

    solutions = scrape_solutions(context)

    solutions = sorted(solutions, key=lambda s: s["kyu"])
    save_solutions(solutions)


if __name__ == "__main__":
    main()
