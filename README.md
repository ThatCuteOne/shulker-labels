# Shulker Labels 1.21.5+
Rename your shulker to any model and render an icon on your box
### Usage:
Rename your shulker box in an anvil to the item that u want it to show

**NOTE:** This only supports all models NOT Model Definitions the full lists for supported names can be found [here(Items)](https://github.com/ThatCuteOne/shulker-labels/blob/main/item_models.json) and [here(Blocks)](https://github.com/ThatCuteOne/shulker-labels/blob/main/block_models.json)

Example:
![\<insert image file\>](https://github.com/ThatCuteOne/shulker-labels/blob/main/docs/example1.png)


### Building(if you can call it that)
To Build just run the [build.py](https://github.com/ThatCuteOne/shulker-labels/blob/main/build.py)

**Note:** I have only tested this on linux but it _should_ work on windows
``` 
pyhton ./build.py
```
This will generate all the models and item definitions

### Custom Definitions
Custom Definitions can be defined in the custom_definitions.json the format is a list of dictionaries which contain a "name" value for the name of the shulker and a "model" value for the path to the model(including namespace)

**Code Example:**
``` 
[
    {
        "name" :"my cool custom definition",
        "model" :"mynamespace:item/cool_icon"
    }
]
```