import asyncio
import logging

import uvloop

import aiohttp
from pyrogram import Client as PyrogramClient, errors
from telethon.utils import VALID_USERNAME_RE

from config_reader import load_config
from fragment import Client, Username


logger = logging.getLogger(__name__)


async def main():
    config = load_config()

    async with aiohttp.ClientSession() as session:
        # https://tl.telethon.dev/methods/channels/update_username.html
        # USERNAME_RE = re.compile(r"[a-zA-Z][\w\d]{3,30}[a-zA-Z\d]$")

        with open("resources/input_usernames.txt") as file:
            lines = set(file.read().splitlines())
        logger.info(f"Loaded {len(lines)} unique input lines")

        with open("resources/invalid_usernames.txt") as file:
            invalid_lines = set(file.read().splitlines())

        lines = lines - invalid_lines

        invalid_lines_count = 0
        with open("resources/invalid_usernames.txt", "a") as file:
            usernames_to_check = set()
            for line in lines:
                match = VALID_USERNAME_RE.match(line.strip("@"))
                if match is None:
                    logger.info(f'Failed to match username from "{line}"')
                    file.write(f"{line}\n")
                    invalid_lines_count += 1
                    continue

                usernames_to_check.add(match.group(0))
        logger.info(f"Extracted {len(usernames_to_check)} usernames from input lines")

        logger.info(
            f"Failed to extract valid usernames from {invalid_lines_count} line(s)"
        )

        logger.info(f"Starting to check {len(usernames_to_check)} usernames...")

        client = Client(session)

        coros = []
        for username in usernames_to_check:
            coros.append(asyncio.create_task(client.get_username(username)))
            await asyncio.sleep(0.5)

        result = await asyncio.gather(*coros, return_exceptions=True)
        available_usernames = [
            user
            for user in result
            if not isinstance(user, Exception) and not user.exists
        ]
        with open("resources/free_usernames.txt", "a") as file:
            file.writelines(
                map(lambda username: f"{username.title}\n", available_usernames)
            )

        logger.info(f"Obtained {len(available_usernames)} available usernames")
        if config.try_to_occupy and available_usernames:
            logger.info("Trying to occupy any of them...")

            async with PyrogramClient(
                name=config.session_file_path.removesuffix(".session"),
                api_id=config.api_id,
                api_hash=config.api_hash,
            ) as pyrogram_client:
                for user in available_usernames:
                    user: Username
                    logger.info(f"Trying to occupy @{user.title}")
                    try:
                        await pyrogram_client.set_username(user.title)
                    except errors.exceptions.UsernameInvalid:
                        logger.info(
                            f"Failed to occupy @{user.title}. Username is invalid!"
                        )
                        with open("resources/invalid_usernames.txt", "a") as file:
                            file.write(f"{user.title}\n")
                    else:
                        logger.info(
                            f"@{user.title} is available and was successfully occupied"
                        )
                        break


uvloop.install()
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith("pyrogram"):
            logging.getLogger(logger_name).setLevel(logging.WARNING)

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
    logger.info("Shutting down...")
