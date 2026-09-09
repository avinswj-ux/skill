import sys, json, concurrent.futures, getpass, time
from pathlib import Path
from run_h3_clip import request_json, data_url, BASE_URL, WORKFLOW_ID

root = Path('/Users/apple/Documents/ChatGPT/skill/output')
meta = root / 'fashion_h3_tasks.json'
key = getpass.getpass('API token: ')
common = '10秒9:16竖屏真实品牌运动男装摄影。参考图1为已确认关键帧，严格保持其人物身份、五官比例、发型、年龄、肤色、身材、服装结构、配色、鞋履和场景。参考图2只作脸部身份补充，不能继承它的衣服和背景。全片只有同一个人，不换装。真实毛孔、自然眨眼和呼吸、衣料微动；目光自然看向行进方向，偶尔侧看，不持续盯镜头。中性白平衡，稳定自然光。禁止换脸、增生人物、手脚畸形、衣服变色、口袋拉链漂移、鞋底变形、瞬移、频闪、文字水印。不要添加旁白字幕。'
jobs = [
 ('今日Look01_黑色机能短裤_关键帧_v1.png', '城市机能', '0–4秒全身跟拍，模特沿步道向前自然走两步，双臂轻摆。4–7秒镜头缓慢推进至膝上中景，模特稍放慢步伐，侧看城市绿植，展示黑色夹克胸部拉链和袖口。7–10秒镜头轻微后退恢复全身，模特自然站定，重心轻移，保持服装完整可见。'),
 ('今日Look02_橙色冲锋衣_关键帧_v1.png', '山地运动', '0–3秒从参考姿势开始，模特轻轻放下扶帽的手，帽子保持自然戴起。3–7秒沿山间步道稳步向前，镜头平稳后退跟拍，展示橙色夹克的帽体、拉链和侧袋。7–10秒自然停步，头部轻转看向山景，镜头小幅推进到膝上中景；动作克制，衣料褶皱真实，不发生任何换装。'),
 ('今日Look03_藏蓝Polo灰色马甲_关键帧_v1.png', '运动叠穿', '0–3秒模特轻轻松开马甲衣摆，手自然落下，马甲全程敞开，展示藏蓝Polo领口和短拉链。3–7秒向前自然走两步，镜头缓慢后退保持完整全身，马甲多袋及拼接纹理清晰。7–10秒模特停步微侧身约15度，看向步道前方，镜头轻微推进，保留自然眨眼呼吸。')]

def submit(job):
    filename, name, action = job
    payload = dict(duration=10, resolution='1080p竖', seed=212238359716024, prompt=common+action,
        ref_image_0=data_url(root / filename), ref_image_1=data_url(root/'identity/母版身份代理_脸部_v1.png'))
    result = request_json(f'{BASE_URL}/api/v1/comfyui/comfyui_workflow/{WORKFLOW_ID}', api_key=key, payload=payload)
    return dict(name=name, response=result)

if sys.argv[1] == 'submit':
    if meta.exists():
        raise SystemExit('Task record already exists; query it instead of resubmitting')
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(submit, jobs):
            results.append(r)
            meta.write_text(json.dumps(results,ensure_ascii=False,indent=2))
            print(json.dumps(r,ensure_ascii=False),flush=True)
else:
    results=json.loads(meta.read_text())
    while True:
        pending=False
        for r in results:
            task_id=(r['response'].get('data') or {}).get('task_id')
            if task_id:
                r['result']=request_json(f'{BASE_URL}/api/v1/comfyui/comfyui_workflow/result/{task_id}',api_key=key)
            data=r.get('result',{}).get('data') or {}
            status=data.get('status','UNKNOWN')
            print(json.dumps(dict(name=r['name'],status=status,results=data.get('results')),ensure_ascii=False),flush=True)
            pending |= status.upper() in ('QUEUED','RUNNING','PENDING','PROCESSING')
        meta.write_text(json.dumps(results,ensure_ascii=False,indent=2))
        if not pending: break
        time.sleep(30)
