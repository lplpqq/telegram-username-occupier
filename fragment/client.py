import logging
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from fragment.base import BaseSession
from fragment.models import Status, Username

BASE_FRAGMENT_API_URL = "https://fragment.com"
STANDARD_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "uk-UA,uk;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}
STATUS_MAPPING = {
    "tm-status-taken": Status.TAKEN,
    "tm-status-avail": Status.ON_SELL,
    "tm-status-unavail": Status.SOLD,
}

logger = logging.getLogger(__name__)


class Client(BaseSession):
    def __init__(self, session: ClientSession, **kwargs) -> None:
        session.headers.update(STANDARD_HEADERS)
        super().__init__(BASE_FRAGMENT_API_URL, session, **kwargs)

    async def get_username(self, username: str) -> Username:
        html_response, response = await self._get(f"/username/{username}")

        if response.url.query_string == f"query={username}":
            logger.info(f"Username: {username} is not occupied!")
            return Username(title=username, exists=False)

        soup = BeautifulSoup(html_response, "lxml")
        status_element = soup.find(
            "span", class_=re.compile("tm-section-header-status")
        )
        username_status = STATUS_MAPPING[status_element["class"][-1]]

        logger.info(f"Username: {username} exists. Status element: {username_status}")
        return Username(title=username, exists=True, status=username_status)
