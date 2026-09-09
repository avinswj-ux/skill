import base64
import getpass
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


FIRST_FRAME_PATH = Path(
    "/Users/apple/Documents/ChatGPT/skill/output/K02_Evan指尖悬停_视觉定稿_v1.png"
)
LAST_FRAME_PATH = Path("/tmp/chatcut-k03-k04-seam-0.jpg")
ENDPOINT = (
    "https://autodl.art/api/v1/comfyui/comfyui_workflow/"
    "minimax_h3_lightx2v"
)

PROMPT = """生成一条连续6秒、9:16竖屏、写实高端手工床垫广告特效镜头。严格从首帧自然运动到尾帧，不切镜，不改变人物身份、服装、展厅透视、暖米色3500K灯光和床垫位置。Evan始终位于画面右侧，苏始终位于左后侧。

0.00至1.20秒：固定中景。Evan右手食指悬停在完整床垫表面上方约2厘米，身体只有轻微自然呼吸；苏正在介绍床垫，只做极轻微的自然动作。床垫保持完整，不提前出现特效。

1.20至1.80秒：Evan食指缓慢向下移动并只点击一次床垫。接触瞬间出现一圈克制、半透明、暖金色的圆形魔法波纹，波纹贴着床面向外扩散；指尖和床垫接触关系真实，床面只产生很轻的受力下陷。

1.80至2.80秒：点击触发时间冻结。苏与背景人物、衣摆和空气尘埃同时静止；环境声快速抽空。Evan是唯一仍能轻微移动的人，他保持右手靠近接触点并抬眼看向床垫，不重复点击。

2.80至5.20秒：暖金色光线从接触点进入床垫，完整床垫垂直升起并在原位置连续展开为清楚、水平、平行、中心对齐的多层手工结构。上层表现亚麻、羊毛、弹性麻等柔软天然材料，下层出现薄型小弹簧与更厚的主体弹簧支撑系统。每层依次亮起柔和轮廓光和少量纤维光尘，具有真实重量与缓停惯性；不出现文字标签。

5.20至6.00秒：分层稳定悬浮，接触点的暖金色能量沿所有层快速扩散，形成一次柔和但明亮的白金色魔法闪光。最后0.20秒逐渐过曝到尾帧的高亮状态，画面构图和亮度严格落到提供的尾帧，方便无缝衔接下一段分层介绍。

摄影机基本锁定，只允许非常轻微、连续的向前推进；禁止突然改变景别、绕行、横移或切换场景。声音只保留轻微展厅底声、一次点击声、低频空气移动、纤维摩擦与柔和魔法闪光声；无对白、无旁白、无音乐。

NEGATIVE：禁止重复第一段动作，禁止二次点击，禁止床垫在点击前拆解，禁止苏或背景人物在冻结后继续移动，禁止换脸换衣，禁止人物复制，禁止增加人物，禁止错误手指、额外手臂或手掌穿入床垫，禁止床垫横向漂移，禁止结构融化、复制、交叉或变成全息投影，禁止夸张爆炸、火焰、闪电，禁止文字、数字、Logo、铭牌、字幕、二维码和水印。优先保证“悬停→单次点击→时间冻结→原位分层→白金闪光”五个事件连续清楚。"""


def data_url(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    token = os.environ.get("AUTODL_TOKEN") or getpass.getpass("AutoDL API key: ")
    body = {
        "duration": 6,
        "resolution": "480p竖",
        "first_frame": data_url(FIRST_FRAME_PATH),
        "last_frame": data_url(LAST_FRAME_PATH),
        "prompt": PROMPT,
    }
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": token,
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
