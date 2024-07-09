import logging
from functools import lru_cache, wraps

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template

from .config import Config


def get_logger(app: Flask) -> logging.Logger:
    logger = logging.getLogger("yandex-captcha")
    logger.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    return logger


def with_captcha(logger: logging.Logger, config: Config, route_func):
    @lru_cache(32)
    def inject_captcha(page_content: str) -> str:
        try:
            soup = BeautifulSoup(page_content)

            if soup.head is None:
                raise ValueError("Encountered page without head tag")
            script_html = '<script src="https://smartcaptcha.yandexcloud.net/captcha.js" defer></script>'
            script = BeautifulSoup(script_html, "html.parser")
            soup.head.append(script)

            form = soup.find("form")
            if form is None or isinstance(form, str):
                raise ValueError("Encountered page without form tag")

            submit_button = form.find(
                lambda tag: tag.name in ["input", "button"]
                and tag.get("type") == "submit"
            )
            if submit_button is None:
                raise ValueError("Encountered page without submit button inside form")
            if submit_button.parent is None or submit_button.parent.parent is None:
                raise ValueError(
                    "Encountered page with submit button in unexpected location inside the form"
                )

            captcha_html = f"""
                <div id="captcha-container" class="smart-captcha" data-sitekey="{config.client_key}">
                    <input type="hidden" name="smart-token">
                </div>
            """
            captcha = BeautifulSoup(captcha_html, "html.parser")
            submit_button.parent.parent.insert_before(captcha)

            return str(soup)

        except Exception as e:
            logger.error(f"Failed to inject captcha: {e}\n{page_content = }")
            return page_content

    def check_captcha(token: str, user_ip: str) -> str | None:
        try:
            response = requests.get(
                "https://smartcaptcha.yandexcloud.net/validate",
                {"secret": config.server_key, "token": token, "ip": ""},
            )
            if response.status_code != 200:
                raise ValueError(f"{response.status_code = }, {response.content = }")

            if response.json().get("status", "") == "ok":
                return None
            else:
                return "Complete the captcha to proceede"

        except Exception as e:
            logger.error(f"Failed to validate captcha: {e}")
            return (
                "Sorry, captcha service is currently unavailable. "
                "Please, try again later or contact the admins if the problem persists."
            )

    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if request.method == "GET":
            response = route_func(*args, **kwargs)
            return inject_captcha(response)
        elif request.method == "POST":
            token = request.form.get("smart-token", "")
            user_ip = request.remote_addr or ""
            error = check_captcha(token, user_ip)
            if error is not None:
                return render_template(
                    "register.html",
                    errors=[error],
                    name=request.form.get("name", ""),
                    email=request.form.get("email", ""),
                )
            return route_func(*args, **kwargs)
        else:
            return route_func(*args, **kwargs)

    return wrapper


def load(app: Flask):
    logger = get_logger(app)
    config = Config.from_env(logger)
    if not config.enabled:
        return

    app.view_functions["auth.register"] = with_captcha(
        logger, config, app.view_functions["auth.register"]
    )
