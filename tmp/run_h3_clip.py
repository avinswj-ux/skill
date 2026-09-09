#!/usr/bin/env python3
"""Submit one MiniMax H3 multi-reference video task and download its result.

The API key is read only from H3_API_KEY and is never written to disk.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


BASE_URL = "https://autodl.art"
WORKFLOW_ID = "minimax_h3_lightx2v_v5"


def data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def request_json(url: str, *, api_key: str, payload: dict | None = None) -> dict:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        method="GET" if payload is None else "POST",
        headers={"Content-Type": "application/json", "Authorization": api_key},
    )
    try:
        with urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--duration", required=True, type=int)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--meta", required=True, type=Path)
    parser.add_argument("refs", nargs="+", type=Path)
    args = parser.parse_args()

    api_key = os.environ.get("H3_API_KEY")
    if not api_key:
        raise SystemExit("H3_API_KEY is not set")
    if not 1 <= args.duration <= 10:
        raise SystemExit("duration must be 1-10 seconds")
    if len(args.refs) > 9:
        raise SystemExit("at most 9 reference images are supported")

    payload: dict[str, object] = {
        "duration": args.duration,
        "prompt": args.prompt_file.read_text(encoding="utf-8").strip(),
        "resolution": "1080p横",
        "seed": 78260723,
    }
    for index, path in enumerate(args.refs):
        payload[f"ref_image_{index}"] = data_url(path)

    submit_url = f"{BASE_URL}/api/v1/comfyui/comfyui_workflow/{WORKFLOW_ID}"
    submitted = request_json(submit_url, api_key=api_key, payload=payload)
    if submitted.get("code") != "Success":
        raise RuntimeError(f"Submit failed: {submitted}")
    task_id = submitted["data"]["task_id"]
    print(f"{args.name}: submitted {task_id}", flush=True)

    status_url = f"{BASE_URL}/api/v1/comfyui/comfyui_workflow/result/{task_id}"
    final: dict | None = None
    for _ in range(120):
        result = request_json(status_url, api_key=api_key)
        if result.get("code") != "Success":
            raise RuntimeError(f"Query failed: {result}")
        data = result.get("data") or {}
        status = data.get("status")
        print(f"{args.name}: {status}", flush=True)
        if status not in {"QUEUED", "RUNNING", "queued", "running"}:
            final = result
            break
        time.sleep(10)
    if final is None:
        raise TimeoutError(f"Timed out waiting for task {task_id}")

    args.meta.parent.mkdir(parents=True, exist_ok=True)
    args.meta.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    results = (final.get("data") or {}).get("results") or []
    video = next((item for item in results if item.get("type") == "video"), None)
    if not video or not video.get("url"):
        raise RuntimeError(f"No video result: {final}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(video["url"], timeout=300) as response:
        args.output.write_bytes(response.read())
    print(f"{args.name}: saved {args.output}", flush=True)


if __name__ == "__main__":
    main()
