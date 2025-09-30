import os
# this script is used to geather all item modles and block modles

block_files = list(os.scandir("./block"))
item_files = list(os.scandir("./item"))

with open("item_models.json", "w", encoding="utf-8") as r:
    r.write("[\n")
    
    
    for i, file in enumerate(item_files):
        if i == len(item_files) - 1:
            r.write(f'"{file.name}"\n')
        else:
            r.write(f'"{file.name}",\n')    
    r.write("]")
    r.close()

with open("block_models.json", "w", encoding="utf-8") as r:
    r.write("[\n")
    
    for i, file in enumerate(block_files):
        if i == len(block_files) - 1:
            r.write(f'"{file.name}"\n')
        else:
            r.write(f'"{file.name}",\n')
    r.write("]")
r.close()