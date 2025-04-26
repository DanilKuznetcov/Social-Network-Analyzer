from datetime import datetime

from network_agent import VKAgent
from preprocessing.preprocessing_utils import (
    TextPreprocessor,
    collect_text_length_statistics,
)
from csv_adapter.csv_utils import CSVPostWriter


topic = "высшее образование"
start = datetime(2024, 2, 1)
end = datetime(2024, 2, 8)

agent = VKAgent()
VK_generator = agent.vk_post_generator(topic, start, end)

# preprocessor = TextPreprocessor(
#     custom_stopwords_path="preprocessing/all_stop_words.txt"
# )
# preprocessor_generator = preprocessor.preprocess_generator(VK_generator)

# Собираем статистику
stats = collect_text_length_statistics(VK_generator)

# Красиво печатаем
for key, value in stats.items():
    print(f"{key}: {value}")

# print(list(preprocessor_generator))
# print(len(list(preprocessor_generator)))

# writer = CSVPostWriter(topic, start, end)
# writer.write_posts(preprocessor_generator)
# writer.close()
