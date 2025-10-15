import torch
from pathlib import Path
from langdetect import detect
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline
from src.config import CONFIG



model_dir = Path("backend/src/nlp") / CONFIG.input_classifier.model_name.split("/")[-1]
assert model_dir.exists(), f"Model path does not exist: {model_dir}"

# Load manually
tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_dir, local_files_only=True)


if torch.cuda.is_available():
    model = model.to("cuda")
    try:
        if torch.cuda.is_bf16_supported():
            model = model.to(dtype=torch.bfloat16)
        else:
            model = model.to(dtype=torch.float16)
    except Exception:
        pass
    device_index = 0
else:
    device_index = -1

clf = TextClassificationPipeline(
    model=model,
    tokenizer=tokenizer,
    device=device_index
)


async def lang_check(query: str = "") -> str:
    language = "de" if detect(query) == "de" else "en"
    return language


async def retrieve_check(query: str = "") -> bool:
    if not query:
        return False
    
    prediction = clf(query)
    return True if prediction[0]["label"] == "LABEL_1" else False