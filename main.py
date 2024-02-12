import json
from dataclasses import dataclass
#from dataclass_wizard import JSONWizard
from typing import (List, Optional)
from enum import Enum

from collections import Counter

import sys


class Category(Enum):
    DETECT      = 1
    RESPOND     = 2
    PROTECT     = 3

class Value(Enum):
    MINIMAL     = 1
    PARTIAL     = 3
    SIGNIFICANT = 5


@dataclass
class ControlInfo:
    name:       str
    category:   Category
    value:      Value
#    comment:    str

@dataclass
class TechniqueInfo:
    ID: str
    controls:      List[ControlInfo]

def LoadTechniqueInfos(file_path: str) -> List[TechniqueInfo]:
    f = open(file_path, 'r')
    json_dict = json.load(f)

    techniqueInfos: TechniqueInfo = []
    techniques = json_dict['techniques']
    for technique in techniques:
        techniqueID = technique['techniqueID']
        techniqueInfo: TechniqueInfo = TechniqueInfo(techniqueID, [])
        techniqueInfos.append(techniqueInfo)

        controlInfo: ControlInfo = ControlInfo('', '', '')
        for metadata in technique['metadata']:

            if 'divider' in metadata:
                continue

            if (metadata['name'] == 'control'):
                controlInfo.name = metadata['value']
            elif (metadata['name'] == 'category'):
                if (metadata['value'] == 'Detect'):
                    controlInfo.category = Category.DETECT
                elif (metadata['value'] == 'Respond'):
                    controlInfo.category = Category.RESPOND
                elif (metadata['value'] == 'Protect'):
                    controlInfo.category = Category.PROTECT
            elif (metadata['name'] == 'value'):
                if (metadata['value'] == 'Minimal'):
                    controlInfo.value = Value.MINIMAL
                elif (metadata['value'] == 'Partial'):
                    controlInfo.value = Value.PARTIAL
                elif (metadata['value'] == 'Significant'):
                    controlInfo.value = Value.SIGNIFICANT
            elif (metadata['name'] == 'comment'):   # commentが最後の並びのようなので
                techniqueInfo.controls.append(controlInfo)
                controlInfo: ControlInfo = ControlInfo('', '', '')

    return techniqueInfos
    

@dataclass
class ControlLank:
    category:   Category
    value:      Value

def ConstructControlLanks(techniqueInfos: TechniqueInfo) -> dict:
    control_lanks: dict = {}
    for techniqueInfo in techniqueInfos:
        for control in techniqueInfo.controls:
            name = control.name
            if not name in control_lanks:
                control_lanks[name] = []
                control_lanks[name].append(ControlLank(control.category, control.value))
            else:
                control_lanks[name].append(ControlLank(control.category, control.value))

    return control_lanks

if __name__ == "__main__":
    args = sys.argv
    if 2 > len(args):
        print('Arguments are too short')

        sys.exit(-1)

    input_json_file = args[1]
    techniqueInfos: TechniqueInfo = LoadTechniqueInfos(input_json_file)

    control_lanks: dict = ConstructControlLanks(techniqueInfos)

    output_csv_file = input_json_file.replace('.json', '-out.csv')
    output = open(output_csv_file, 'w')
    output.write("control_name, count, score, categories_str\n")
    output.close
    output = open(output_csv_file, 'a')

    for control_name, control_lanks in control_lanks.items():
        categories: Category = []
        count = len(control_lanks)
        score = 0
        for control_lank in control_lanks:
            categories.append(control_lank.category)
            if control_lank.value == Value.MINIMAL:
                score += Value.MINIMAL.value
            elif control_lank.value == Value.PARTIAL:
                score += Value.PARTIAL.value
            elif control_lank.value == Value.SIGNIFICANT:
                score += Value.SIGNIFICANT.value

        categories_str = ""
        for key, value in Counter(categories).items():
            key_str = str(key).lstrip('Category.')
            categories_str += "{0}, {1},".format(key_str, value)

        print("Controle Name: %s, Count: %d, Score: %d, Categories: %s" % (control_name, count, score, categories_str))
        output.write("%s, %d, %d, %s\n" % (control_name, count, score, categories_str))
        

    output.close
