from transformers import BertTokenizer, BertModel
import torch
import numpy as np

from scipy.spatial import distance

tokenizer = BertTokenizer.from_pretrained("DeepPavlov/rubert-base-cased-sentence")
model = BertModel.from_pretrained("DeepPavlov/rubert-base-cased-sentence")


def get_embedding(word):
    inputs = tokenizer(word, return_tensors="pt")
    outputs = model(**inputs)
    word_vect = outputs.pooler_output.detach().numpy()
    return word_vect


def get_distance(first_word, second_word):
    w1 = get_embedding(first_word)
    w2 = get_embedding(second_word)
    cos_distance = np.round(distance.cosine(w1, w2), 2)
    return 1 - cos_distance


get_distance("электрогитара", "электрическая гитара")
