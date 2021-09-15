class MessageTemplates:

    @staticmethod
    def get_task_url(task_id):
        return f'https://tracker.softlex.pro/browse/{task_id[0]}'

    @staticmethod
    def end_of_day_notify() -> str:
        return "Рабочий день подходит к концу - спасибо за работу!\n" \
            + "Не забудь залогировать потраченное сегодня на задачи время в журнале работ.\n" \
            + "Хорошего вечера!"
    
    @staticmethod
    def issue_list_notify(username: str, task_id: str) -> str:
        return f"Привет, {username}\n" \
            + f"Тебе назначена задача \"{task_id}\"!\n" \
            + f"Ссылка на задачу: {MessageTemplates.get_task_url(task_id)}\nУспехов!"
    
    @staticmethod
    def finished_notify(username: str, task_id: str) -> str:
        return f"Привет, {username}\n" \
            + f"Задача \"{task_id}\" проверена и успешно завершена!\n" \
            + f"Ссылка на задачу: {MessageTemplates.get_task_url(task_id)}\nСпасибо!"
    
    @staticmethod
    def rejected_notify(username: str, task_id: str) -> str:
        return f"Привет, {username}\n" \
            + f"Задача \"{task_id}\" проверена и отклонена.\n" \
            + f"Ссылка на задачу: {MessageTemplates.get_task_url(task_id)}\nУспехов!"
