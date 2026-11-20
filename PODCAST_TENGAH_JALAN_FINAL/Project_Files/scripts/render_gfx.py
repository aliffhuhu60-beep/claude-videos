import json, subprocess, urllib.parse, os, sys
from concurrent.futures import ThreadPoolExecutor
P = json.load(open('/home/user/work/out/plan.json'))
G = '/home/user/work/out/gfx'; os.makedirs(G, exist_ok=True)
jobs = []
for i, p in enumerate(P['panels']):
    qd = dict(id=p['id'], dur=p['dur'], cues=','.join(str(c) for c in p['cues']))
    if p['lines']: qd['lines'] = p['lines']
    jobs.append(('panels.html', f'{G}/panel_{i:02d}', p['dur'], urllib.parse.urlencode(qd)))
for i, o in enumerate(P['overlays']):
    qd = dict(id=o['kind'], dur=o['dur'], t1=o.get('t1', ''), t2=o.get('t2', ''))
    jobs.append(('overlays.html', f'{G}/ov_{i:02d}', o['dur'], urllib.parse.urlencode(qd)))
az = [s for s in P['segments'] if s['kind'] == 'azan'][0]
jobs.append(('azan.html', f'{G}/azan', round(az['out1'] - az['out0'], 3), f"dur={az['out1']-az['out0']}"))
jobs.append(('credits.html', f'{G}/credits', 6.0, ''))
jobs.append(('overlays.html', f'{G}/bug', 1/30, 'id=bug'))
jobs.append(('overlays.html', f'{G}/splitbg', 1/30, 'id=splitbg'))
only = sys.argv[1:] 
def run(j):
    html, out, dur, qs = j
    if only and not any(o in out for o in only): return
    r = subprocess.run(['node', 'render_frames.js', html, out, str(dur), '30', qs], cwd='/home/user/work/gfx', capture_output=True, text=True)
    if 'pageerror' in r.stderr or r.returncode: print('ERR', out, r.stderr[-500:])
    return out
with ThreadPoolExecutor(3) as ex:
    for r in ex.map(run, jobs): pass
print('gfx done', len(jobs))
