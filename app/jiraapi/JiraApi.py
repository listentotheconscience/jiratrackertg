from jira import JIRA
from jira.resources import Issue
from jira.exceptions import JIRAError
import json
import pandas as pd


class JiraApi:
    BASE_JIRA_URL = "https://tracker.softlex.pro"

    def __init__(self, auth_data: tuple) -> None:
        self.jira = JIRA(server=self.BASE_JIRA_URL, basic_auth=auth_data)
        self.login = auth_data[0]

    @staticmethod
    def get_all_issues(jira_client: JIRA, project_name, fields):
        issues = []
        i = 0
        chunk_size = 100
        while True:
            chunk = jira_client.search_issues(f'project = {project_name}', startAt=i, maxResults=chunk_size,
                                              fields=fields)
            i += chunk_size
            issues += chunk.iterable
            if i >= chunk.total:
                break
        return issues

    def issue(self, task_id):
        return self.jira.issue(id=task_id, fields="assignee,status,summary")

    @classmethod
    def try_to_login(cls, login: str, password: str) -> bool:
        try:
            JIRA(server=cls.BASE_JIRA_URL, basic_auth=(login, password))
            return True
        except JIRAError as e:
            return False

    @staticmethod
    def issue_parse(item):
        if isinstance(item, Issue):
            item = item.raw
        try:
            return {
                item['key']: {
                    "status": item['fields']['status']['name'],
                    "assignee": item['fields']['assignee']['name']
                }
            }
        except TypeError:
            return {}

    @staticmethod
    def issues_for_json(issues) -> list:
        return [item.raw for item in issues]

    def create_json_if_not_exists(self, project_name: str):
        json_path = f'storage/{project_name}.json'
        import os.path as path
        if not path.exists(json_path):
            with open(json_path, 'w') as f:
                issues = self.get_all_issues(self.jira, project_name, ["status", "assignee", "summary"])
                f.write(json.dumps(self.issues_for_json(issues), sort_keys=True, indent=4))

    @staticmethod
    def get_unique_codes(codes):
        if len(codes) < 1:
            return
        output = []
        prev = None
        for code in codes:
            if code[0] is not prev:
                output.append(code[0])
                prev = code[0]
        return output

    async def check_updates(self):
        projects = [item.id for item in self.jira.projects()]
        task_ids = []
        for project in projects:
            self.create_json_if_not_exists(project)

            issues = self.get_all_issues(self.jira, project, ["status", "assignee", "summary"])
            # print(issues)
            prev_data = json.load(open(f'storage/{project}.json', 'r'))

            now = {}
            for i in issues:
                now.update(self.issue_parse(i))

            prev = {}
            for j in prev_data:
                prev.update(self.issue_parse(j))

            left = pd.DataFrame(data=now)
            right = pd.DataFrame(data=prev)
            try:
                compare = left.compare(right)
                task_ids.append(self.get_unique_codes(sorted(compare)))
            except Exception as e:
                pass

            with open(f'storage/{project}.json', 'w') as f:
                f.write(json.dumps(self.issues_for_json(issues), sort_keys=True, indent=4))

        return task_ids
