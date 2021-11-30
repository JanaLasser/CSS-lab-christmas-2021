#!/usr/bin/env python
# coding: utf-8

# In[37]:


from torch.utils.data import DataLoader, Dataset
from transformers import AutoTokenizer, AutoConfig
from transformers import AutoModelForSequenceClassification
from transformers import TrainingArguments
from transformers import Trainer
from scipy.special import softmax
from os.path import join
from torch import cuda

import numpy as np
import torch as th
import pandas as pd
import sys
import emoji_resources as er


# In[41]:


emojis = er.emojis
try:
    lang = sys.argv[1]
    if lang == "-f":
        print("running in notebook, setting testing defaults")
        lang = "hi"
        emoji = "🤌"
        test = True
    elif lang in er.languages:
        try:
            emoji = sys.argv[2]
            emoji = emojis[emoji]
        except IndexError:
            print("no emoji supplied!")
        try:
            test = sys.argv[3]
            if test == "test":
                test = True
        except IndexError:
            test = False
    else:
        print(f"unknown language")
        
except IndexError:
    print("no language supplied!")


# In[46]:


class InferenceDataset(Dataset):

    def __init__(self, data, tokenizer, max_token_len):
        self.data = data
        self.tokenizer = tokenizer
        self.max_token_len = max_token_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        data_row = self.data.iloc[index]
        text = data_row.text
        encoding = self.tokenizer.encode_plus(
            text=text,
            add_special_tokens=True,
            max_length=self.max_token_len,
            return_token_type_ids=True,
            padding="max_length",
            truncation=True,
            return_attention_mask=True)

        return dict(input_ids=th.tensor(encoding["input_ids"], dtype=th.long),
                    attention_mask=th.tensor(encoding["attention_mask"], dtype=th.long),
                    token_type_ids=th.tensor(encoding["token_type_ids"], dtype=th.long))


# In[ ]:


checkpoint = "models/twitter-xlm-roberta-base-sentiment" 
model = AutoModelForSequenceClassification        .from_pretrained(checkpoint)
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
#config = AutoConfig.from_pretrained(checkpoint)


# In[49]:


src = "../data/tweets"
file = f"tweets_language-{lang}_emoji-{emoji}_2019-01-01-to-2021-11-28.parquet.gzip"

if test:
    df = pd.read_parquet(join(src, file))
    df = df[0:10]
else:
    df = pd.read_parquet(join(src, file))

df = df.dropna(subset=['text'])

if test:
    batch_size = 10
else:
    batch_size = 4096

inference_set = InferenceDataset(df, tokenizer, max_token_len=128)
inference_params = {'batch_size': batch_size, 'shuffle': False}
inference_loader = DataLoader(inference_set, **inference_params)


# In[53]:


training_args = TrainingArguments(
    "test-trainer",
    per_device_train_batch_size = 16,
    per_device_eval_batch_size = 16,
    num_train_epochs = 5,
    learning_rate = 2e-5,
    weight_decay = 0.01,
    evaluation_strategy = "epoch"
)

trainer = Trainer(
        model,
        training_args,
        tokenizer = tokenizer,
)

device = 'cuda' if cuda.is_available() else 'cpu'
print(f"running on device: {device}")

raw_pred, _, _ = trainer.prediction_loop(inference_loader, description="prediction")
scores = softmax(raw_pred)

df['negative'] = scores[0:, 0]
df['neutral'] = scores[0:, 1]
df['positive'] = scores[0:, 2]


if test:
    print(df[['negative', 'neutral', 'positive',]])
else:
    dst = "../data/sentiment"
    resname = f"sentiment_language-{lang}_emoji-{emoji}_2019-01-01-to-2021-11-28.csv.gzip"
    df[["id", "negative", "neutral", "positive"]]        .to_csv(join(dst, resname), index=False, compression="gzip")

