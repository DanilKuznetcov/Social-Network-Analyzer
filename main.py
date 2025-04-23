from datetime import datetime

from network_agent import VKAgent
from preprocessing.preprocessing_utils import TextPreprocessor

topic = "COVID-19"
start = datetime(2024, 8, 11, 11)
end = datetime(2024, 8, 11, 12)

agent = VKAgent()
VK_generator = agent.vk_post_generator(topic, start, end)

preprocessor = TextPreprocessor(
    custom_stopwords_path="preprocessing/all_stop_words.txt"
)

preprocessor_generator = preprocessor.preprocess_generator(VK_generator)

# print(list(preprocessor_generator))
print(len(list(preprocessor_generator)))
