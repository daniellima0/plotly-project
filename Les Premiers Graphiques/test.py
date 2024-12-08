import json
from pprint import pprint

# Load your JSON data from the file
with open('../Données anciennes-20241108/preprocess-topaz-data732-part01/topaz-data732--france--www.fdesouche.com--20190101--20211231.json', 'r') as file:
    data = json.load(file)

my_dict = data["data-all"]["2019"]["9"]["10"][0]
pprint(my_dict)

# Salvar o output do pprint em um arquivo de texto
# with open('output.txt', 'w', encoding='utf-8') as f:
#     pprint(my_dict, stream=f)
