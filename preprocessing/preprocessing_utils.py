import re
from typing import Iterator, Dict, Any, Union
import warnings
from pymystem3 import Mystem
import nltk
from nltk.corpus import stopwords
from string import punctuation
import numpy as np


warnings.filterwarnings("ignore")


class TextPreprocessor:
    def __init__(self, custom_stopwords_path: str = None):
        """Initialize text preprocessor with optional custom stopwords.

        Args:
            custom_stopwords_path: Path to file with custom stopwords (one per line)
        """
        self._initialize_nltk()
        self.stop_words = self._load_stopwords(custom_stopwords_path)
        self.mystem = Mystem()

    def _initialize_nltk(self):
        """Download required NLTK resources."""
        nltk.download("stopwords", quiet=True)
        nltk.download("punkt", quiet=True)
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)

    def _load_stopwords(self, custom_stopwords_path: str = None) -> list:
        """Load stopwords including custom ones if provided."""
        stop_words = set(stopwords.words("russian"))

        if custom_stopwords_path:
            with open(custom_stopwords_path, "r", encoding="utf-8") as f:
                custom_stopwords = [line.strip() for line in f if line.strip()]
            stop_words.update(custom_stopwords)

        return list(stop_words)

    def _clean_text(self, text: str) -> str:
        """Clean text from links and special tags."""
        text = re.sub(r"http\S+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\[id.+?\]", "", text, flags=re.MULTILINE)
        text = re.sub(r"\[club.+?\]", "", text, flags=re.MULTILINE)
        return text

    def _has_cyrillic(self, text: str) -> bool:
        """Check if text contains cyrillic characters."""
        return bool(re.search("[а-яА-Я]", text))

    def _has_too_many_emojis(self, text: str, threshold: int = 10) -> bool:
        """Check if text contains too many emojis."""
        emoji_count = len(re.findall("[\U0001f34a-\U0001f650]", text))
        return emoji_count >= threshold

    def _preprocess_text(self, text: str) -> str:
        """Lemmatize and normalize text."""
        tokens = self.mystem.lemmatize(text.lower())
        tokens = [
            token
            for token in tokens
            if token not in self.stop_words
            and token != " "
            and token.strip() not in punctuation
        ]
        return " ".join(tokens)

    def preprocess_generator(
        self,
        posts: Iterator[Dict[str, Any]],
        text_field: str = "text",
        min_length: int = 1,
        check_cyrillic: bool = True,
        check_emojis: bool = True,
        emoji_threshold: int = 10,
        min_likes: int = 0,
    ) -> Iterator[Dict[str, Any]]:
        """Lazily preprocess posts in dictionary format.

        Args:
            posts: Iterator of post dictionaries
            text_field: Name of the field containing text to process
            min_length: Minimum text length to keep
            check_cyrillic: Whether to filter non-cyrillic texts
            check_emojis: Whether to filter texts with too many emojis
            emoji_threshold: Maximum allowed emojis per text
            min_likes: Minimum number of likes to keep post

        Yields:
            Post dictionaries with processed text (other fields unchanged)
        """
        seen_texts = set()

        for post in posts:
            # Skip if post doesn't have required field or has too few likes
            if text_field not in post or post.get("likes", 0) < min_likes:
                continue

            original_text = post[text_field]

            # Skip empty posts
            if not original_text or len(original_text.strip()) < min_length:
                continue

            # Clean text
            cleaned = self._clean_text(original_text)

            # Skip if text became too short after cleaning
            if len(cleaned.strip()) < min_length:
                continue

            # Check cyrillic if enabled
            if check_cyrillic and not self._has_cyrillic(cleaned):
                continue

            # Check emojis if enabled
            if check_emojis and self._has_too_many_emojis(cleaned, emoji_threshold):
                continue

            # Preprocess text
            processed = self._preprocess_text(cleaned)

            # Skip empty results and duplicates
            if processed and processed not in seen_texts:
                seen_texts.add(processed)
                # Create new dict with processed text (don't modify original)
                yield {
                    **post,
                    text_field: processed,
                    # 'original_text': original_text  # Optionally keep original
                }


def collect_text_length_statistics(posts: Iterator[Dict]) -> Dict[str, float]:
    """
    Собирает базовую статистику по длине текстов в постах.

    Args:
        posts: Итератор словарей, каждый словарь должен содержать ключ 'text'.

    Returns:
        Словарь со статистикой: общее количество постов, средняя длина, медиана,
        минимум, максимум, и основные квантильные значения.
    """
    lengths = []

    for post in posts:
        text = post.get("text", "")
        lengths.append(len(text))

    if not lengths:
        return {}

    lengths = np.array(lengths)

    stats = {
        "total_posts": int(len(lengths)),
        "mean_length": float(np.mean(lengths)),
        "median_length": float(np.median(lengths)),
        "min_length": int(np.min(lengths)),
        "max_length": int(np.max(lengths)),
        "5_percentile": int(np.quantile(lengths, 0.05)),
        "10_percentile": int(np.quantile(lengths, 0.10)),
        "25_percentile": int(np.quantile(lengths, 0.25)),
        "50_percentile": int(np.quantile(lengths, 0.50)),
        "75_percentile": int(np.quantile(lengths, 0.75)),
        "90_percentile": int(np.quantile(lengths, 0.90)),
        "95_percentile": int(np.quantile(lengths, 0.95)),
    }

    return stats


# Example usage
if __name__ == "__main__":
    # Sample data
    sample_posts = [
        {
            "comments": 0,
            "date": 1723363378,
            "from_id": -136391189,
            "id": 17248,
            "likes": 10,
            "owner_id": -136391189,
            "reposts": 1,
            "text": "К началу 2024 года численность пожилого населения Казахстана достигла 2,7 миллиона человек",
            "views": 272,
        },
        {
            "comments": 2,
            "date": 1723363379,
            "from_id": -136391189,
            "id": 17249,
            "likes": 5,
            "owner_id": -136391189,
            "reposts": 0,
            "text": "💰👍🏻 Не знаете чем себя занять? Попробуйте разместить рекламу!",
            "views": 100,
        },
        {
            "comments": 1,
            "date": 1723363380,
            "from_id": -136391189,
            "id": 17250,
            "likes": 0,  # Will be filtered due to min_likes=1
            "owner_id": -136391189,
            "reposts": 0,
            "text": "Этот пост будет отфильтрован из-за малого числа лайков",
            "views": 50,
        },
    ]

    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        custom_stopwords_path="preprocessing/all_stop_words.txt"
    )

    # Process posts lazily with min_likes=1
    processed_posts = preprocessor.preprocess_generator(
        iter(sample_posts), min_likes=1, text_field="text"
    )

    # Consume the generator
    for i, post in enumerate(processed_posts, 1):
        print(post)
