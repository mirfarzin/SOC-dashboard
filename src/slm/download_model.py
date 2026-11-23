"""
Model Pre-Caching Utility for PS02.
Downloads and caches the genuine Small Language Model locally so that all subsequent
inference runs 100% offline without requiring internet access.
"""

import sys
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer

DEFAULT_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
DEFAULT_TARGET_DIR = Path(__file__).resolve().parent.parent.parent / "models" / "SmolLM2-135M-Instruct"


def download_and_cache_model(model_id: str = DEFAULT_MODEL, target_dir: Path | str = DEFAULT_TARGET_DIR):
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    print(f"============================================================")
    print(f"Downloading Local SLM: {model_id}")
    print(f"Target Directory:      {target}")
    print(f"License:               Apache 2.0")
    print(f"Parameters:            ~135 Million (Ultra-lightweight local SLM)")
    print(f"============================================================")

    print("\n1/2 Downloading Tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.save_pretrained(str(target))
    print("Tokenizer cached successfully.")

    print("\n2/2 Downloading Model Weights (safetensors)...")
    model = AutoModelForCausalLM.from_pretrained(model_id)
    model.save_pretrained(str(target))
    print("Model weights cached successfully.")

    print(f"\n[SUCCESS] Model '{model_id}' is now fully cached at '{target}'.")
    print("You can now disconnect from the internet; the assistant will operate 100% OFFLINE.")


if __name__ == "__main__":
    model_to_download = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MODEL
    download_and_cache_model(model_to_download)
