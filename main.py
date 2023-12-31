from selenium import webdriver
import tomllib
from types import SimpleNamespace
from selenium.webdriver.support.wait import WebDriverWait
from utils import enter_codewars, enter_solutions_page, scrape_solutions, save_solutions, write_summary_readme


def load_config():
    with open("config.toml", "rb") as file:
        config = tomllib.load(file)

    match config:
        case {
            "_session_id": str(),
            "summary_readme_title": str(),
            "username": str(),
            "repository": str(),
            "branch": str(),
        }:
            pass
        case _:
            raise ValueError(f"invalid configuration: {config}")

    return config


def prepare_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    return webdriver.Chrome(options=options)


def prepare_driver_context():
    driver = prepare_driver()
    driver.implicitly_wait(3)

    wait = WebDriverWait(driver, timeout=60, poll_frequency=1)

    first_tab_handle = driver.current_window_handle
    driver.execute_script("window.open('about:blank','image_tab');")
    driver.switch_to.window(driver.window_handles[-1])
    second_tab_handle = driver.current_window_handle
    driver.switch_to.window(first_tab_handle)

    return SimpleNamespace(
        driver=driver,
        wait=wait,
        first_tab_handle=first_tab_handle,
        second_tab_handle=second_tab_handle
    )


def main():
    config = load_config()
    driver_context = prepare_driver_context()

    enter_codewars(driver_context, config["_session_id"])
    enter_solutions_page(driver_context)
    solutions = scrape_solutions(driver_context)

    save_solutions(solutions)

    write_summary_readme(solutions,
                         title=config["summary_readme_title"],
                         username=config["username"],
                         repository_url=config["repository"],
                         branch=config["branch"])


if __name__ == "__main__":
    main()
