import glob
import os

ls = glob.glob('../data/wars/submissions/*/*/*', recursive=True)

for file in ls:
    old_name = file.split('/')[-1].split('_')
    end = old_name[0]
    index = old_name[-1]
    name = file.split('/')[-2]+ index + ('.' + end if end=='asm' else '' )
    path = f"{'/'.join(file.split('/')[:-1])}/{name}"
    # rename file
    os.rename(file, path)

