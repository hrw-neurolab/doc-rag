### Query text classifier

The classifier model aims to perform binary classification on user input to determine whether RAG is needed for the chat, or if the LLM could directly reply.

The implementation collects data from two Hugging Face datasets: [*Simple Daily Conversations*](https://huggingface.co/datasets/aarohanverma/simple-daily-conversations-cleaned) and [*RAG Domain Query Classification*](https://huggingface.co/datasets/Arun63/rag_domain_query_classification). The datasets are then translated into German, creating a bilingual training set.

Currently, Llama 3.2 running on Ollama is used for translation, and the classifier model is based on [XLM-RoBERTa](https://huggingface.co/docs/transformers/en/model_doc/xlm-roberta).

use the following command lines to create training data and train the text classifier model.

```
python3 data_preparation.py
```

```
python3 train.py
```

Output are saved under `data` and `models` respectively.