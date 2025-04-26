from datetime import datetime

from network_agent import VKAgent
from preprocessing.preprocessing_utils import TextPreprocessor
from csv_adapter.csv_utils import CSVPostWriter


topic = "высшее образование"
start = datetime(2024, 2, 1)
end = datetime(2024, 2, 2)

agent = VKAgent()
VK_generator = agent.vk_post_generator(topic, start, end)

print(len(list(VK_generator)))

# preprocessor = TextPreprocessor(
#     custom_stopwords_path="preprocessing/all_stop_words.txt"
# )
# preprocessor_generator = preprocessor.preprocess_generator(VK_generator)

# print(list(preprocessor_generator))
# print(len(list(preprocessor_generator)))

# writer = CSVPostWriter(topic, start, end)
# writer.write_posts(preprocessor_generator)
# writer.close()
