from datetime import datetime, timedelta

from network_agent import VKAgent
from preprocessing.preprocessing_utils import (
    TextPreprocessor,
    collect_text_length_statistics,
)
from csv_adapter.csv_utils import CSVPostWriter


topic = "высшее образование"
start = datetime(2024, 1, 1)
end = datetime(2025, 1, 1)

current = start

while current < end:
    # Гарантировано получаем начало следующего месяца
    next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
    # Получаем конец диапазона
    month_end = min(next_month, end)

    print(f"\n=== Обработка: {current.date()} — {month_end.date()} ===")

    agent = VKAgent()
    VK_generator = agent.vk_post_generator(topic, current, month_end)

    preprocessor = TextPreprocessor(
        custom_stopwords_path="preprocessing/all_stop_words.txt"
    )
    preprocessor_generator = preprocessor.preprocess_generator(VK_generator)

    # stats = collect_text_length_statistics(preprocessor_generator)

    # print(f"Статистика:")
    # for key, value in stats.items():
    #     print(f"{key}: {value}")

    folder_name = f"{topic.replace(' ', '_')}: {current.date()} - {month_end.date()}"
    writer = CSVPostWriter(folder_name=folder_name, with_original=True)

    writer.write_posts(preprocessor_generator)
    writer.close()

    current = month_end
