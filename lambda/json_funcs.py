# -*- coding: utf-8 -*-
import json

def read_json():
    with open('db.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data

def replace_pic(object_pic):
    with open('visuals/test_data.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        sources = data['headlineTemplateData']['properties']["backgroundImage"]["sources"]
        sources[0]['url'] = object_pic
        data['headlineTemplateData']['properties']["backgroundImage"]["sources"] = sources
        jsonstring = json.dumps(data, ensure_ascii=False)
        jsonfile = open("tests/after_test_data.json", "w", encoding='utf-8')
        jsonfile.write(jsonstring)
        jsonfile.close()