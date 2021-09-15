import asyncio
import datetime
import os

from aiogram.utils import executor
from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State

try:
    from MessageTemplates import MessageTemplates
except ModuleNotFoundError:
    from .MessageTemplates import MessageTemplates
import json

LOGIN = State()


class TGBot:
    def __init__(self, api_token: str) -> None:
        storage = MemoryStorage()
        self.bot = Bot(token=api_token)
        self.dispatcher = Dispatcher(bot=self.bot, storage=storage)
        self.set_handlers()
        self.logins = self.get_logins()

    def get_logins(self):
        with open('storage/users.json', 'r') as f:
            try:
                return dict(json.loads(f.read()))
            except json.decoder.JSONDecodeError as e:
                return {}

    def set_login(self, login):
        with open('storage/users.json', 'w') as f:
            users = self.get_logins()
            users.update(login)
            f.write(json.dumps(users))

    def set_handlers(self):
        @self.dispatcher.message_handler(commands=['start'])
        async def start_command_handler(message: types.Message):
            await self.bot.send_message(chat_id=message.from_user.id, text=f'Привет, {message.from_user.username}!\n' \
                                        + 'Пришли свой логин от Jira')
            await LOGIN.set()

        @self.dispatcher.message_handler(state=LOGIN)
        async def login_handler(message: types.Message, state: FSMContext):
            user = {message.text: message.from_user.id}
            self.set_login(user)
            await self.bot.send_message(chat_id=message.from_user.id, text="Отлично, жди обновления с трекера!")
            await state.finish()

        @self.dispatcher.message_handler(commands=['help'])
        async def help_handler(message: types.Message):
            await self.bot.send_message(
                chat_id=message.from_user.id,
                text="Привет!\nЯ бот компании Sofltex, который отслеживает обновления с Jira.\n" \
                     + "Для того чтобы начать работу со мной тебе нужно ввести команду /start."
            )

    @staticmethod
    async def switch_status(task_id, status, assignee):
        if status.lower() in "issue list" or status.lower() in "backlog":
            return MessageTemplates.issue_list_notify(assignee, task_id)
        elif status.lower() in "rejected":
            return MessageTemplates.rejected_notify(assignee, task_id)
        elif status.lower() in "finished" or status.lower() in "решенные":
            return MessageTemplates.finished_notify(assignee, task_id)
        return None

    async def trigger(self, task_ids: list, jira):
        await self.notify_all()
        for task_id in task_ids:
            if task_id is None:
                continue
            issue = jira.issue(task_id[0])
            status = issue.fields.status.name
            assignee = issue.fields.assignee.name
            summary = issue.fields.summary
            if assignee not in self.logins:
                continue
            name = str(issue.fields.assignee)
            text = await self.switch_status(f'{task_id[0]} {summary}', status, name)
            if text is None:
                continue
            await self.bot.send_message(chat_id=self.logins[assignee], text=text)

    async def notify_all(self):
        for _, v in self.logins.items():
            message = MessageTemplates.end_of_day_notify()
            await self.bot.send_message(chat_id=v, text=message)
        now = datetime.datetime.now()
        future = datetime.datetime(now.year, now.month, now.day, 18, 30)
        future += datetime.timedelta(days=1)
        await asyncio.sleep((future-now).seconds)


if __name__ == '__main__':
    load_dotenv()
    tg = TGBot(os.environ.get('API_TOKEN'))
    executor.start_polling(tg.dispatcher, skip_updates=True)