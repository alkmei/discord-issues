import asyncio
import logging

from bot import main

if __name__ == "__main__":
    # This runs the bot.
    # The asyncio.run() function handles the async event loop.
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot shutting down...")
