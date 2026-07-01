
import re
import json
import logging

log = logging.getLogger("MentorMind")

def safe_parse_json(raw, fallback=None):
    if not raw or "Error" in str(raw): return fallback or {}
    try:
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        match   = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match: return json.loads(match.group())
        return fallback or {}
    except Exception as e:
        log.error(f"JSON parse error: {e}")
        return fallback or {}

def safe_int(val, default=5):
    if val is None: return default
    if isinstance(val, list): val = val[0] if val else default
    try: return int(val)
    except: return default
