import argparse
import getpass
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


RESULT_ENDPOINT = "https://autodl.art/api/v1/comfyui/comfyui_workflow/result/{}"


def fetch(task_id: str, token: str) -> dict:
    request = urllib.request.Request(
        RESULT_ENDPOINT.format(task_id),
        headers={"Authorization": token},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def find_urls(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from find_urls(item)
    elif isinstance(value, list):
        for item in value:
            yield from find_urls(item)
    elif isinstance(value, str) and value.startswith(("http://", "https://")):
        yield value


def status_of(payload: dict) -> str:
    data = payload.get("data") or {}
    return str(data.get("status") or payload.get("status") or "UNKNOWN").upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_id")
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()
    token = os.environ.get("AUTODL_TOKEN") or getpass.getpass("AutoDL API key: ")

    previous = None
    while True:
        try:
            payload = fetch(args.task_id, token)
        except urllib.error.HTTPError as error:
            print(error.read().decode("utf-8"), flush=True)
            raise

        status = status_of(payload)
        if status != previous:
            print(json.dumps({"status": status}, ensure_ascii=False), flush=True)
            previous = status

        if status in {"SUCCESS", "SUCCEEDED", "COMPLETED", "FINISHED"}:
            urls = list(dict.fromkeys(find_urls(payload)))
            video_urls = [
                url for url in urls
                if any(ext in url.lower() for ext in (".mp4", ".mov", ".webm"))
            ]
            if not video_urls:
                print(json.dumps(payload, ensure_ascii=False), flush=True)
                raise RuntimeError("Completed task did not expose a video URL")
            args.output_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(video_urls[0], args.output_path)
            print(
                json.dumps(
                    {"status": status, "output": str(args.output_path)},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return

        if status in {"FAILED", "ERROR", "CANCELED", "CANCELLED"}:
            print(json.dumps(payload, ensure_ascii=False), flush=True)
            raise RuntimeError(f"Task ended with status {status}")

        time.sleep(10)


if __name__ == "__main__":
    main()
