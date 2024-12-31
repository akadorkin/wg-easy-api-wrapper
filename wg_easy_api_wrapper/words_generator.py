import random

ADJECTIVES = [
    "fancy", "small", "vast", "blue", "happy",
    "silent", "loud", "modern", "ancient", "brave",
    "quick", "bright", "calm", "eager", "gentle",
    "jolly", "kind", "mighty", "proud", "swift"
]

NOUNS = [
    "river", "mountain", "sky", "forest", "house",
    "ocean", "lion", "castle", "sun", "storm",
    "cloud", "meadow", "valley", "beach", "hill",
    "stream", "tree", "field", "shore", "path"
]

def get_random_name() -> str:
    """
    Возвращает одно случайное прилагательное + одно случайное существительное.
    Пример: 'happy-lion'
    """
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adj}-{noun}"
