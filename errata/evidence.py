from __future__ import annotations
import json
from pathlib import Path
from dataclasses import asdict


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, default=str)+"\n", encoding='utf-8')


def append_jsonl(path, data):
    with open(path,'a',encoding='utf-8') as f: f.write(json.dumps(data,sort_keys=True,ensure_ascii=False,default=str)+'\n')
