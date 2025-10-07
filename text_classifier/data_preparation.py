import json
import datasets
import pandas as pd
from tqdm import tqdm
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import ChatPromptTemplate


def load_llm():

    llm = OllamaLLM(model="llama3.2")

    system_text = "You are a professional translator. \
        Given a text in English, your task is to translate it into German."

    human_text = "Here is the sentence: {sentence}\
        Output only the German sentence and avoid any other additional text."

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_text),
            ("human", human_text)
        ]
    )

    chain = prompt | llm

    return chain



chitchat_data = datasets.load_dataset("aarohanverma/simple-daily-conversations-cleaned", split="train")
query_data = datasets.load_dataset("Arun63/rag_domain_query_classification", split="train")
sample_size = 2048

# Convert raw data to DataFrames
chitchat_df = pd.DataFrame(chitchat_data)
query_df = pd.DataFrame(query_data)


chitchat_df = chitchat_df.rename(columns={"data": "query"})

# Extract relevant fields from the JSON in the 'output' column
query_output = query_df["output"].apply(json.loads)
query_df["query_type"] = query_output.apply(lambda x: x["query_type"])
query_df["query"] = query_output.apply(lambda x: x["original_query"])

# Filter out chitchat entries from query_df
query_df = query_df[query_df["query_type"] != "chitchat"]

# Assign labels
chitchat_df["label"] = 0
query_df["label"] = 1


# Sample and merge datasets
merged_df = pd.concat([
    query_df.sample(int(sample_size / 2)),
    chitchat_df.sample(sample_size)
])[["query", "label"]].reset_index(drop=True)

print("EN data loaded.")

chain = load_llm()

for _, row in tqdm(merged_df.iterrows(), total=len(merged_df), desc="DE data translation"):
    translated_query = chain.invoke({"sentence": row["query"]})
    merged_df.loc[len(merged_df)] = [translated_query, row["label"]]


merged_df.to_json("data/processed_train.json")