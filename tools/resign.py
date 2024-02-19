import os
from pathlib import Path


old_dir = '/Users/maohika/work/spla/train/labelImg/classes/predefined_classes.txt_match'
old_f = open(old_dir)
new_dir = '/Users/maohika/work/spla/train/labelImg/classes/predefined_classes.txt_match_new'
new_f = open(new_dir)

remap = {}
new_classes = {}

for i, cls in enumerate(new_f.readlines()):
    new_classes[cls.replace('\n', '')] = i

for i, cls in enumerate(old_f.readlines()):
    c = cls.replace('\n', '')
    remap[i] = new_classes[c] if c in new_classes else None

t_dir = '/Volumes/splatoon3/dataset/match'
out_dir =  '/Users/maohika/Downloads/temp'
os.makedirs(out_dir, exist_ok=True)
for path in Path(t_dir).rglob('*.txt'):
    f = open(path)
    fname = os.path.basename(path)
    if fname == 'classes.txt':
        continue
    o_lines = []
    for line in f.readlines():
        vals = line.split(' ')
        vals[0] = str(remap[int(vals[0])])
        if vals[0] != 'None':
            o_lines.append(' '.join(vals))
    if len(o_lines) > 0:
        o_f = open(f'{out_dir}/{fname}', 'w')
        o_f.writelines(o_lines)
        o_f.flush()
        o_f.close()
        f.close()
