import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, DataCollatorWithPadding
)



# if torch.backends.mps.is_available():
#     device = "mps"
# elif torch.cuda.is_available():
#     device = "cuda"
# else:
#     device = "cpu"



df = pd.read_json("data/processed_train.json")
df = df.sample(frac=1).dropna().reset_index(drop=True)
train_df, test_df = train_test_split(df, test_size=0.2)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

model = AutoModelForSequenceClassification.from_pretrained("xlm-roberta-base")
tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")


def tokenize_function(examples):
    return tokenizer(examples["query"], padding="max_length", truncation=True, max_length=128)

# Apply the tokenizer to the dataset
train_tokenized = train_dataset.map(tokenize_function, batched=True)
test_tokenized = test_dataset.map(tokenize_function, batched=True)

# Inspect tokenized samples
print(train_tokenized)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)


timestamp = datetime.now().strftime('%m%d%H%M%S')

training_args = TrainingArguments(
    output_dir=f"models/{timestamp}",
    eval_strategy="epoch",
    learning_rate=1e-5,
    weight_decay=0.01,
    per_device_train_batch_size=16,
    num_train_epochs=3
)

trainer = Trainer(
    model=model,                        # Pre-trained BERT model
    args=training_args,                 # Training arguments
    train_dataset=train_tokenized,
    eval_dataset=test_tokenized,
    tokenizer=tokenizer,
    data_collator=data_collator,        # Efficient batching
)

# Start training
trainer.train()