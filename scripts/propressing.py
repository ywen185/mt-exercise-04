import random
import os

currentpath=os.path.dirname(__file__)
previouspath=os.path.dirname(currentpath)

src_path = os.path.join(previouspath, 'data','train.en')
trg_path = os.path.join(previouspath, 'data','train.nl')
src_path_new = os.path.join(previouspath, 'data','train_new.en')
trg_path_new = os.path.join(previouspath, 'data','train_new.nl')

with open(src_path, encoding="utf-8") as f1, open(trg_path, encoding="utf-8") as f2:
    src_lines = f1.readlines()
    trg_lines = f2.readlines()

pairs = list(zip(src_lines, trg_lines))

random.shuffle(pairs)

sample_size = 100000
pairs = pairs[:sample_size]

src_sample, trg_sample = zip(*pairs)

with open(src_path_new, "w", encoding="utf-8") as f1, open(trg_path_new, "w", encoding="utf-8") as f2:
    f1.writelines(src_sample)
    f2.writelines(trg_sample)

