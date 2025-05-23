import json
import copy
import os
try:
  os.mkdir("./assets/label/models/block")
  os.mkdir("./assets/label/models/item")
  os.mkdir("./assets/minecraft/items")
except:
    pass



# generate data for cases
base_definition = {
  "model": {
    "type": "select",
    "property": "minecraft:display_context",
    "cases": [
      {
        "when": "gui",
        "model": {
          "type": "minecraft:select",
          "property": "minecraft:component",
          "component": "minecraft:custom_name",
          "cases": [],
          "fallback": {
            "type": "minecraft:special",
            "model": {
              "type": "minecraft:shulker_box",
              "texture": "minecraft:shulker_black",
              "openness": 0
            },
            "base": "minecraft:item/black_shulker_box"
          }
        }
      }
    ],
    "fallback": {
      "type": "minecraft:special",
      "model": {
        "type": "minecraft:shulker_box",
        "texture": "minecraft:shulker_black",
        "openness": 0
      },
      "base": "minecraft:item/black_shulker_box"
    }
  }
}
cases = []

def index_cases(file,model_type):
    with open(file,encoding="UTF-8") as file:
        models = json.load(file)
        for model in models:
            model = model[:-5]
            cases.insert(0,{"name":f"{model}"})
            cases[0]["model"] = f"label:{model_type}/{model}"


print("Geathering cases from block models...")
index_cases("block_models.json","block")
print("Geathering cases from item models...")
index_cases("item_models.json","item")
with open("custom_definitions.json",encoding="UTF-8") as file:
    definitions = json.load(file)
    for definition in definitions:
        cases.insert(0,definition)
# remove duplicates
print("Removing Duplicates..")
seen = set()
cases = [d for d in cases if not (d['name'] in seen or seen.add(d['name']))]


case_template ={
              "when": "",
              "model": {
                "type": "minecraft:composite",
                "models": [
                  {
                    "type": "minecraft:model",
                    "model": "",
                    "tints": []
                  },
                  {
                    "type": "minecraft:special",
                    "model": {
                      "type": "minecraft:shulker_box",
                      "texture": "minecraft:shulker_black",
                      "openness": 0
                    },
                    "base": "minecraft:item/black_shulker_box"
                  }
                ]
              }
            }
print("Interpreting Cases..")
interpreted_cases = []
for x in cases:
    ctemp = copy.deepcopy(case_template)
    ctemp["when"] = x["name"]
    ctemp["model"]["models"][0]["model"] = x["model"]
    interpreted_cases.append(ctemp)
base_definition['model']["cases"][0]["model"]["cases"] = interpreted_cases


# apply template to item model definitions
template = base_definition
print("Generateing Item model Definitions..")
colors =[
    "black",
    "blue",
    "brown",
    "cyan",
    "gray",
    "green",
    "light_blue",
    "light_gray",
    "lime",
    "magenta",
    "orange",
    "pink",
    "purple",
    "red",
    "white",
    "yellow",
    ""
]
def write_no_color(path):
    path["base"] = str("minecraft:item/shulker_box")
    path["model"]["texture"] = str("shulker")
def write(color,path):
    path["base"] = str("minecraft:item/"+color+"_shulker_box")
    path["model"]["texture"] = str("shulker_"+color)
for c in colors:
    if c == "":
        for models in template['model']["cases"][0]["model"]["cases"]:
            write_no_color(models["model"]["models"][1]) 
        write_no_color(template['model']["cases"][0]["model"]["fallback"])
        write_no_color(template['model']["fallback"])
        out_file = open("./assets/minecraft/items/shulker_box.json","w")
    else:
        for models in template['model']["cases"][0]["model"]["cases"]:
            write(c,models["model"]["models"][1]) 
        write(c,template['model']["cases"][0]["model"]["fallback"])
        write(c,template['model']["fallback"])
        out_file = open(str("./assets/minecraft/items/"+c+"_shulker_box.json"),"w")
    json.dump(template,out_file,indent=2)


# generate models
print("Generateing Block Models..")
block_model = {
  "parent": "",
  "display": {
    "gui": {
      "rotation": [30,225,0],
      "translation": [0,0,80],
      "scale": [0.4,0.4,0.4]
    }
  }
}
with open("block_models.json",encoding="UTF-8") as file:
    models = json.load(file)
for model_name in models:
    out_file = open(f"./assets/label/models/block/{model_name}","w")
    f = block_model
    model_name_pure = model_name[:-5]
    f["parent"] = "block/"+ model_name_pure
    json.dump(f,out_file,indent=2)
print("Generateing Item Models..")
item_model = {
  "parent": "item/fire_charge",
  "display": {
    "gui": {
      "translation": [0,0,80],
      "scale": [0.7,0.7,0.7]
    }
  }
}
with open("item_models.json",encoding="UTF-8") as file:
    models = json.load(file)
for model_name in models:
    out_file = open(f"./assets/label/models/item/{model_name}","w")
    f = item_model
    model_name_pure = model_name[:-5]
    f["parent"] = "item/"+ model_name_pure
    json.dump(f,out_file,indent=2)
print("Completed!")