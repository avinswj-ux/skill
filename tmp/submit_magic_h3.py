import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


IMAGE_PATH = Path(
    "/Users/apple/Documents/ChatGPT/skill/output/K03_安脊十层拆解_代表帧_v1.png"
)
ENDPOINT = (
    "https://autodl.art/api/v1/comfyui/comfyui_workflow/"
    "minimax_h3_lightx2v"
)

PROMPT = """生成连续9秒9:16写实高端床垫广告特效镜头。严格保持参考图中同一位Evan、暖米色展厅、安脊十层结构、层数顺序、材质颜色、水平位置和中心对齐不变，首尾回到参考图构图。

0至0.8秒：十层床垫静止悬浮，背景宾客像时间冻结一样完全不动，只有少量暖金色尘埃从Evan指尖出现。

0.8至4.5秒（第4镜，天然材料介绍）：一圈克制的暖金色半透明能量环从最上层向下扫描。经过亚麻、羊毛、弹性麻等上半层时，各层依次出现柔和轮廓光、细小纤维微粒和轻微呼吸式悬浮，随后恢复稳定。摄影机极慢推进，像魔法显微镜揭示真实材质，不出现文字标签。

4.5至8.2秒（第5镜，支撑结构介绍）：光线由暖金色过渡为低饱和青金色，沿MINI面包簧、五区弹簧和天然黄麻底层依次流动。弹簧只做一次整齐轻微的波浪式回弹，黄麻底层出现稳固的金色几何光纹。少量光点沿层间空气流动，体现透气与支撑；所有结构不能变形、复制或错位。

8.2至9秒：所有魔法光效收束回Evan右手指尖，镜头平稳回到完整十层正面构图；最上方亚麻一角轻微抬起但尚未被抓住，为下一镜抽出亚麻做动作预备。

风格是真实材质结合克制高级的东方魔法视觉，暖金色为主、少量青绿色辅助；不是科幻全息投影，不改变产品真实外观。只需轻柔空气流、纤维摩擦、微弱金属回弹和魔法粒子声，不要对白。

NEGATIVE：禁止床垫层数变化、顺序变化、层板融合、弹簧复制或融化、增加床垫、增加人物、背景人物移动、Evan换脸换衣、镜头绕行、突然切场、夸张爆炸、火焰、闪电、文字、数字、Logo、标签、字幕、二维码和水印。若动作复杂，优先保证产品结构稳定、两阶段扫描清楚、首尾构图一致。"""


def main() -> None:
    image = "data:image/png;base64," + base64.b64encode(
        IMAGE_PATH.read_bytes()
    ).decode("ascii")
    body = {
        "duration": 9,
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
