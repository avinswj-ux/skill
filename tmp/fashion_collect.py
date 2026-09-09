import json, urllib.request, subprocess
from pathlib import Path
root=Path('/Users/apple/Documents/ChatGPT/skill/output')
for item in json.loads((root/'fashion_h3_tasks.json').read_text()):
    data=item.get('result',{}).get('data') or {}
    for result in data.get('results',[]):
        if result.get('type')!='video': continue
        path=root/f"今日_{item['name']}_10秒1080竖屏.mp4"
        if not path.exists(): urllib.request.urlretrieve(result['url'],path)
        probe=subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,duration,codec_type','-of','json',str(path)],text=True)
        print(str(path),probe)
        sheet=root/f"今日_{item['name']}_视频检查.jpg"
        if not sheet.exists():
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(path),'-vf','fps=1/3,scale=270:-1,tile=3x1','-frames:v','1',str(sheet)],check=True)
