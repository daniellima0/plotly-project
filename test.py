import json

file_name = './Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json'

# open and load file
f = open(file_name, 'r', encoding='utf-8')
data = json.loads(f.read())
f.close()

print(data["data"]["2022"]["12"]["9"][0].keys())