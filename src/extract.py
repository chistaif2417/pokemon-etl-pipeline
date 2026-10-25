"""Extract: gọi PokeAPI, cache cục bộ, lưu JSON thô vào raw.raw_api_response."""
import hashlib
import json
import logging
import time
from collections import Counter
from pathlib import Path

import requests
from sqlalchemy import text
from sqlalchemy.engine import Engine
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.config import API_BASE, CACHE_DIR, REQUEST_DELAY, REQUEST_TIMEOUT

log = logging.getLogger(__name__)
session = requests.Session()
session.headers["User-Agent"]= "pokemon-etl-pipeline/1.0"

class RetryableError(Exception):
    """Lỗi tạm thời (429, 5xx) đáng để thử lại."""

def parse_url(url: str) -> tuple[str, int]:
    """'https://pokeapi.co/api/v2/pokemon-species/25/' -> ('pokemon-species', 25)."""
    parts = url.rstrip("/").split("/")
    return parts[-2], int(parts[-1])

# ---------- Gọi API + retry ----------
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(
        (RetryableError, requests.ConnectionError, requests.Timeout)
    ),
    reraise=True,
)
def _http_get(url: str) -> dir:
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    if resp.status_code == 429 or resp.status_code >= 500:
        raise RetryableError(f"HTTP {resp.status_code} for {url}")
    resp.raise_for_status() # 404... không retry, báo lỗi luôn
    return resp.json()

# ---------- Cache ----------
def _cache_path(url: str) -> Path:
    key = hashlib.sha1(url.encode()).hexdigest()
    return CACHE_DIR / f"{key}.json"

def fetch(url: str, refresh: bool = False) -> dict:
    """Lấy JSON từ cache nếu có, nếu không thì gọi API rồi lưu cache."""
    path = _cache_path(url)
    if path.exists() and refresh is False:
        log.debug("cache hit: %s", url)
        return json.loads(path.read_text(encoding="utf-8"))

    log.debug("GET: %s", url)
    data = _http_get(url)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data), encoding="utf-8")
    tmp.replace(path)
    time.sleep(REQUEST_DELAY)
    return data

# ---------- Ghi tầng raw ----------
UPSERT_RAW = text("""
    INSERT INTO raw.raw_api_response (endpoint, resource_id, payload)
    VALUES (:endpoint, :resource_id, CAST(:payload AS JSONB))
    ON CONFLICT (endpoint, resource_id)
    DO UPDATE SET payload = EXCLUDED.payload, fetched_at = now()
    WHERE raw.raw_api_response.payload IS DISTINCT FROM EXCLUDED.payload
""")

def save_raw(engine: Engine, records: list[tuple[str, int, str]]) -> None:
    """Upsert danh sách (endpoint, resource_id, payload) trong một transaction."""
    if not records:
        return
    rows = [
        {"endpoint": e, "resource_id": i, "payload": json.dumps(p)}
        for e, i, p in records
    ]
    with engine.begin() as conn:
        conn.execute(UPSERT_RAW, rows)

# ---------- Điều phối ----------
def extract_all (engine: Engine, generations: list[int], refesh: bool = False) -> Counter:
    """Lấy toàn bộ dữ liệu của các thế hệ đã chọn và ghi vào raw. Trả về số bản ghi mỗi endpoint."""
    counts: Counter = Counter()
    type_urls: set[str] = set()
    ability_urls: set[str] = set()

    for gid in generations:
        gen = fetch(f"{API_BASE}/generation/{gid}/", refesh)
        records = [("generation", gen["id"], gen)]

        species_refs = sorted(gen["pokemon_species"], key= lambda r: parse_url(r["url"])[1])
        log.info("Generation %s: %d species", gid, len(species_refs))

        for n, ref in enumerate(species_refs, start=1):
            species = fetch(ref["url"], refesh)
            records.append(("pokemon-species", species["id"], species))

            for variety in species["varieties"]:
                poke = fetch(variety["pokemon"]["url"], refesh)
                records.append(("pokemon", poke["id"], poke))

                type_urls |= {t["type"]["url"] for t in poke["types"]}
                ability_urls |= {a["ability"]["url"] for a in poke["abilities"]}

            if n % 25 == 0:
                log.info("  processed %d/%d species", n, len(species_refs))

        save_raw(engine, records)
        counts.update(endpoint for endpoint, _, _ in records)
    records = []
    for url in sorted(type_urls) + sorted(ability_urls):
        endpoint, rid = parse_url(url)
        records.append((endpoint, rid, fetch(url, refesh)))
    log.info("Get %d type and %d ability", len(type_urls), len(ability_urls))
    save_raw(engine, records)
    counts.update(endpoint for endpoint, _, _ in records)

    return counts