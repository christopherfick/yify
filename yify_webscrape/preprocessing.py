import string
import re


def clean_text(text):
    text = text.lower()
    text = remove_text_squarebrackets(text)
    text = remove_punctuation(text)
    text = text.strip()
    text = re.sub(" +", " ", text)
    text = text.capitalize()
    return text


def remove_text_squarebrackets(text):
    return re.sub("[\(\[].*?[\)\]]", "", text)


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))
