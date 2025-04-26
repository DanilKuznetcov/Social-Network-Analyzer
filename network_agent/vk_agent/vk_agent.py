import time
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Настройка вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

from network_agent.vk_agent.api_key import ACCESS_TOKEN


class VKAgent:
    def __init__(self):
        self.API_METHOD = "https://api.vk.com/method/newsfeed.search"
        self.API_V = "5.91"
        self.API_KEY = ACCESS_TOKEN

    def vk_get_request(self, topic: str, start: time, end: time, start_from: str = ""):
        # Request limit is 200
        # Api method doc: https://dev.vk.com/ru/method/newsfeed.search
        params = {
            "access_token": self.API_KEY,
            # Without count vk return only 30. Maximum count = 200
            "count": 200,
            "start_time": int(time.mktime(start.timetuple())),
            "end_time": int(time.mktime(end.timetuple())),
            "q": topic,
            "v": self.API_V,
            "start_from": start_from,
        }
        # ['Response'] contain ['count', 'items', 'next_from', 'total_count']
        return requests.get(self.API_METHOD, params).json()["response"]

    def modify_post(self, post):
        # 'Item' contain ['inner_type', 'comments', 'marked_as_ads', 'type', 'attachments',
        #                  'date', 'from_id', 'id', 'likes', 'owner_id', 'post_type', 'reposts', 'text', 'views']
        need_metrics = [
            "id",
            "date",
            "likes",
            "reposts",
            "comments",
            "views",
            "from_id",
            "owner_id",
            "text",
        ]
        metrics = list(post.keys())
        for metric in metrics:
            if metric not in need_metrics:
                del post[metric]
            elif isinstance(post[metric], dict) and "count" in post[metric]:
                post[metric] = post[metric]["count"]

    def vk_get_posts(self, package: dict, topic: str, start: time, end: time):

        posts = package["items"]

        while "next_from" in package:
            next_from = package["next_from"]
            package = self.vk_get_request(topic, start, end, next_from)
            posts += package["items"]

        for post in posts:
            self.modify_post(post)
            yield post

    def vk_get_package(self, topic: str, start: time, end: time):
        # Time period should contain <1000 posts
        delta = timedelta(hours=8)

        while start < end:
            cur_end = min(start + delta, end)

            # Получаем первый элемент генератора
            resp = self.vk_get_request(topic, start, cur_end)

            if resp is None:
                break  # Нет данных — заканчиваем

            total_count = resp.get("total_count", 0)

            if total_count > 1000:
                delta -= timedelta(hours=1)
                continue
            elif total_count < 600:
                delta += timedelta(hours=1)

            yield (resp, start, cur_end)
            start = cur_end

    def vk_post_generator(self, topic: str, start: time, end: time):
        for package, start, end in self.vk_get_package(topic, start, end):
            for post in self.vk_get_posts(package, topic, start, end):
                yield post


if __name__ == "__main__":
    topic = "COVID-19"
    start = datetime(2024, 8, 11, 11)
    end = datetime(2024, 8, 13, 12)

    agent = VKAgent()
    data = agent.vk_post_generator(topic, start, end)
    # print(f"11.08.2024 11:00 were published: \n {data[1:2]}")
    print(len(list(data)))
