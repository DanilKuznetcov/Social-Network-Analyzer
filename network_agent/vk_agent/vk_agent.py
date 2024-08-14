import time
import requests
from datetime import datetime, timedelta

from api_key import ACCESS_TOKEN


class VKAgent:
    def __init__(self):
        self.API_METHOD = 'https://api.vk.com/method/newsfeed.search'
        self.API_V = '5.91'
        self.API_KEY = ACCESS_TOKEN

    def vk_get_request(self, topic: str, start: time, end: time, start_from: str = ''):
        # Request limit is 200
        # Api method doc: https://dev.vk.com/ru/method/newsfeed.search
        params = {
            'access_token': self.API_KEY,
            # Without count vk return only 30. Maximum count = 200
            'count': 200,
            'start_time': time.mktime(start.timetuple()),
            'end_time': time.mktime(end.timetuple()),
            'q': topic,
            'v': self.API_V,
            'start_from': start_from,
        }
        # ['Response'] contain ['count', 'items', 'next_from', 'total_count']
        return requests.get(self.API_METHOD, params).json()['response']

    def modify_post(self, post):
        # 'Item' contain ['inner_type', 'comments', 'marked_as_ads', 'type', 'attachments',
        #                  'date', 'from_id', 'id', 'likes', 'owner_id', 'post_type', 'reposts', 'text', 'views']
        need_metrics = ['id', 'date', 'likes', 'reposts', 'comments', 'views', 'from_id', 'owner_id', 'text']
        metrics = list(post.keys())
        for metric in metrics:
            if metric not in need_metrics:
                del post[metric]
            elif isinstance(post[metric], dict) and 'count' in post[metric]:
                post[metric] = post[metric]['count']

    def vk_get_package(self, topic: str, start: time, end: time):
        # Package limit is 1000, more will be skipped
        package = []
        next_from = ''
        while True:
            resp = self.vk_get_request(topic, start, end, next_from)
            # In-built posts modification for reductions API req
            for post in resp['items']:
                self.modify_post(post)
            package.extend(resp['items'])
            if 'next_from' not in resp:
                break
            next_from = resp['next_from']
        return package

    def specify_time_periods(self, topic: str, start: time, end: time):
        # Time period should contain less 1000 posts
        periods = []
        delta = timedelta(hours=8)

        while start < end:
            cur_end = min(start + delta, end)
            total_count = self.vk_get_request(topic, start, cur_end)['total_count']

            if total_count > 1000:
                delta -= timedelta(hours=1)
                continue
            elif total_count < 600:
                # Too small petiod entails exceeding limit in 5 API req/sec
                delta += timedelta(hours=1)

            periods.append((start, cur_end))
            start = cur_end
        return periods

    def vk_get_data(self, topic: str, start: time, end: time):
        data = []
        periods = self.specify_time_periods(topic, start, end)
        for start, end in periods:
            package = self.vk_get_package(topic, start, end)
            data.extend(package)
        return data


if __name__ == '__main__':
    topic = 'COVID-19'
    start = datetime(2022, 8, 11, 11)
    end = datetime(2022, 8, 11, 12)

    agent = VKAgent()
    data = agent.vk_get_data(topic, start, end)
    print(f"11.08.2022 11:00 were published: \n {data[1:2]}")
