from aiogram.utils import executor
import asyncio
from jiraapi.JiraApi import JiraApi
from tg.TGBot import TGBot
from dotenv import load_dotenv
import os


load_dotenv()
tg = TGBot(os.environ.get('API_TOKEN'))
jira = JiraApi(("nikolay.semenovskiy", "iAASsRo3t3k&"))


async def trigger_tg_bot():
    tasks = await jira.check_updates()
    await tg.trigger(tasks, jira)
    await asyncio.sleep(300)
    await trigger_tg_bot()

if __name__ == "__main__":
    asyncio.run(trigger_tg_bot())
