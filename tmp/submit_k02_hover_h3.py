import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


IMAGE_PATH = Path(
    "/Users/apple/Documents/ChatGPT/skill/output/K02_Evan指尖悬停_视觉定稿_v1.png"
)
ENDPOINT = (
    "https://autodl.art/api/v1/comfyui/comfyui_workflow/"
    "minimax_h3_lightx2v"
)

PROMPT = """生成连续3秒、9:16、写实高端床垫广告微动态镜头。首帧和尾帧严格回到参考图构图。保持同一位Evan、同一位苏、暖米色展厅、床垫外观、服装、站位、灯光和镜头焦段完全稳定。

0至1秒：Evan身体只有自然呼吸，右手食指悬停在床垫表面上方约3厘米，不接触床垫；他视线落在指尖。苏保持疑惑和观察状态，头部只轻微侧转。

1至2.3秒：Evan食指非常缓慢地下移不到1厘米后停住，仍然不触碰床垫；手腕与其余手指保持自然稳定。苏眨眼一次，并把视线从Evan移向床垫。背景宾客只允许极轻微、真实的环境动作。

2.3至3秒：两人保持动作预备状态，Evan指尖停在床垫上方约2厘米，最后一帧构图、人物姿态和床垫位置尽量与参考图一致，方便下一镜继续向下点击。

摄影机完全锁定，无推拉、无摇移、无变焦。表演克制自然，没有对白，只保留轻微展厅环境声和衣料呼吸声。

NEGATIVE：禁止指尖接触床垫、禁止点击波纹、禁止床垫凹陷或提前拆解、禁止床垫变形、禁止换脸换衣、禁止人物复制、禁止增加人物、禁止错误手指或额外手臂、禁止手掌穿入床垫、禁止苏夸张表情、禁止镜头移动、禁止背景突变、禁止文字、Logo、标签、字幕、二维码和水印。优先保证人物身份、手部结构、床垫外观和首尾衔接。"""


def main() -> None:
    image = "data:image/png;base64," + base64.b64encode(
        IMAGE_PATH.read_bytes()
    ).decode("ascii")
    body = {
        "duration": 3,
        "resolution": "480p竖",
        "first_frame": image,
        "last_frame": image,
        "prompt": PROMPT,
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": os.environ["AUTODL_TOKEN"],
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            print(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print(error.read().decode("utf-8"))
        raise


if __name__ == "__main__":
    main()
