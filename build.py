import asyncio
import logging
import os
import json
from pathlib import Path
import shutil
import zipfile

import aiofiles
import aiohttp

snapshot_building = False

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
    None # for normal shulker
]


logger = logging.getLogger("Shulker Labels Builder")
logging.basicConfig(level=logging.INFO,format='[%(asctime)s] [%(name)s/%(levelname)s] %(message)s',datefmt='%H:%M:%S')

class ItemModel():
   def __init__(self,id,type):
      self.type = type
      id = id.removeprefix('assets/minecraft/models/item/')
      id = id.removeprefix('assets/minecraft/models/block/')
      id = id.removesuffix(".json")
      self.id = id
      self._root_ = f"assets/label/models/{type}"
   async def intepret_as_case(self,shulker_definition):
      logger.info(f"generating case for {self.id}")
      result = {
              "when": str(self.id),
              "model": {
                "type": "minecraft:composite",
                "models": [
                  {
                    "type": "minecraft:model",
                    "model": f"label:{self.type}/{self.id}",
                    "tints": []
                  },
                  shulker_definition
                ]
              }
            }
      return result
   async def interpret_block_model(self):
      return {
          "parent": f"block/{self.id}",
          "display": {
            "gui": {
              "rotation": [30,225,0],
              "translation": [0,0,80],
              "scale": [0.4,0.4,0.4]
            },
            "firstperson_righthand": {
              "rotation": [0, 45, 0],
              "translation": [0, 1, 0],
              "scale": [0.3, 0.3, 0.3]
            },
          }
        }
   async def interpret_item_model(self):
      return {
          "parent": f"item/{self.id}",
          "display": {
            "gui": {
              "translation": [0,0,80],
              "scale": [0.7,0.7,0.7]
            },
            "firstperson_righthand": {
              "rotation": [90, 0, -135],
              "translation": [0, 3.2, 0],
              "scale": [0.3, 0.3, 0.3]
            },
          }
        }

   async def write(self):
      logger.info(f"Writing Model {self.id}.json")
      async with aiofiles.open(f"{self._root_}/{self.id}.json","w") as f:
        if self.type == "block":
          await f.write(json.dumps(await self.interpret_block_model()))
        elif self.type == "item":
           await f.write(json.dumps(await self.interpret_item_model()))
        else:
           logger.error(f"Unknown Model type '{self.type}'. Skipping model '{self.id}'")




      
      
      

class ShulkerItemDefinition():
  def __init__(self,color):
      self.color = color
      self.entries = []
      self._root_ = "assets/minecraft/items"

  async def write(self):
    shulker_model_definition ={
      "type": "minecraft:special",
      "model": {
        "type": "minecraft:shulker_box",
        "texture": f"minecraft:shulker_{self.color}",
        "openness": 0
      },
      "base": f"minecraft:item/{self.color}_shulker_box"
    }
    if self.color is not None:
      filename = f"{self.color}_shulker_box.json"
    else:
      filename = "shulker_box.json"
      shulker_model_definition["model"]["texture"] = "minecraft:shulker"
      shulker_model_definition["base"] = "minecraft:item/shulker_box"


    with open(f"{self._root_}/{filename}","w") as f:
      cases = []
      for model in self.entries:
        cases.append(await model.intepret_as_case(shulker_model_definition))

      data = {
         "model": {
            "type": "select",
            "property": "minecraft:display_context",
            "fallback": shulker_model_definition,
            "cases": [
              {
                "when": ["gui","firstperson_lefthand","firstperson_righthand"],
                "model": {
                  "type": "minecraft:select",
                  "property": "minecraft:component",
                  "component": "minecraft:custom_name",
                  "cases": cases,
                  "fallback": shulker_model_definition
                }
              }
            ]
         }
      }
      f.write(json.dumps(data))


class AssetGeatherer():
    def __init__(self):
      self.models:list[ItemModel] = []
      
    async def json_get_request(self,url:str)->dict:
      try:
          async with aiohttp.ClientSession() as client:
             async with client.get(url) as response:
                if response.status == 200:
                   return await response.json()
      except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.error(f"Failed to connect to {url}")
            else:
                logger.exception(f"HTTP error: {e}")
      except Exception as e:
            logger.error(f"Unexpected error: {e}")

    async def download_jar(self,url:str):
      logger.info("Downloading client.jar")
      try:
            async with aiohttp.ClientSession() as client:
                async with client.get(url) as response:
                    response.raise_for_status()
                    async with aiofiles.open(".build/client.jar", 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                        return True
      except aiohttp.ClientResponseError as e:
            if e.status == 404:
                logger.error(f"Failed to connect to {url}")
            else:
                logger.exception(f"HTTP error: {e}")
      except Exception as e:
            logger.error(f"Unexpected error: {e}")

    async def get_version_url(self):
      version_meta = await self.json_get_request("https://launchermeta.mojang.com/mc/game/version_manifest.json")
      if snapshot_building:
        logger.info("Building for latest snapshot")
        target_version = version_meta["latest"]["snapshot"]
      else:
        logger.info("Building for latest release")
        target_version = version_meta["latest"]["release"]
      self.version = target_version
      for version in version_meta["versions"]:
         if version["id"] == target_version:
            return version["url"]            
         
    def local_is_newest(self):
      try:
      # checks if the newest assets are already downloaded or not
        with open(".build/data.json","r") as f:
            data = json.load(f)
        if data["minecraft_version"] == self.version:
            return True
      except Exception:
         return False
      return False

       
    async def run(self):
      version_metadata = await self.json_get_request(await self.get_version_url())
      if not self.local_is_newest() or not Path(".build/client.jar").exists():
        await self.download_jar(version_metadata["downloads"]["client"]["url"])
      known_ids = []
      try:
        with zipfile.ZipFile(".build/client.jar", 'r') as jar:
            # Filter for files in the models directory
            for file_info in jar.infolist():
                if file_info.filename.startswith('assets/minecraft/models/item/'):
                    filename = file_info.filename.removeprefix('assets/minecraft/models/item/')
                    if filename not in known_ids:
                      self.models.append(ItemModel(file_info.filename.removeprefix('assets/minecraft/models/item/'),"item"))
                      known_ids.append(filename)
                elif file_info.filename.startswith('assets/minecraft/models/block/'):
                    filename = file_info.filename.removeprefix('assets/minecraft/models/block/')
                    if filename not in known_ids:
                      self.models.append(ItemModel(filename,"block"))
                      known_ids.append(filename)
                    
      except FileNotFoundError:
        logger.error("Error: JAR file not found.")
      except zipfile.BadZipFile:
        logger.error("Error: client.jar is not a valid ZIP/JAR file.")




async def main():
  os.makedirs(".build",exist_ok=True)
  shutil.rmtree("assets",ignore_errors=True)
  # this class is all wierd idk why i wrote it like that(idk what this code comment is either)
  assets = AssetGeatherer()
  await assets.run()

  # generate files
  os.makedirs("./assets/label/models/block",exist_ok=True)
  os.makedirs("./assets/label/models/item",exist_ok=True)
  os.makedirs("./assets/minecraft/items",exist_ok=True)

  # generate item definitions
  tasks = []
  for shulker in colors:
    shulkerclass = ShulkerItemDefinition(shulker)
    shulkerclass.entries.extend(assets.models)
    tasks.append(shulkerclass.write())


  with open(".build/data.json","w") as f:
     json.dump({
        "minecraft_version": assets.version
     },f)
  # generate item models
  for item_model in assets.models:
     tasks.append(item_model.write())
     


  await asyncio.gather(*tasks)
  logger.info("Done!")



asyncio.run(main())