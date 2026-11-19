"""Model and data loading. CPU only, fp32."""
from pathlib import Path

import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parent.parent
SWE_BLIMP_CSV = ROOT / "data" / "swe_blimp" / "swe_blimp_v1.csv"

DEFAULT_MODEL = "jekunz/smollm-135m-cpt-fineweb-swedish"
TARGET_PHENOMENON = "EMBEDDED V2 AdvP."


def load_model(name: str = DEFAULT_MODEL):
    tok = AutoTokenizer.from_pretrained(name)
    model = AutoModelForCausalLM.from_pretrained(name, dtype=torch.float32)
    model.eval()
    return model, tok


def load_swe_blimp(phenomenon: str | None = None) -> pd.DataFrame:
    df = pd.read_csv(SWE_BLIMP_CSV, sep=";")
    df["phenomenon"] = df["phenomenon"].str.strip()
    if phenomenon is not None:
        df = df[df["phenomenon"] == phenomenon].reset_index(drop=True)
    return df
