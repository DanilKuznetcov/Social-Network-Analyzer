from vk_agent import get_posts
from datetime import datetime, timedelta

start = datetime(2022, 8, 11, 11)
end = datetime(2022, 8, 11, 12)
delta = timedelta(hours=1)

filtered = get_posts('COVID-19', start, end, delta)
