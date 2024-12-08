import json

# contar quantas mençoes da keyword pays tem no ano de 2022 pro primeiro json e pro segundo
with open('../Données-20241108/fr.sputniknews.africa--20221101--20221231/fr.sputniknews.africa--20221101--20221231.json', 'r') as file:
    old_data = json.load(file)

with open('../Données-20241108/fr.sputniknews.africa--20220630--20230630/fr.sputniknews.africa--20220630--20230630.json', 'r') as file:
    recent_data = json.load(file)
    
print("old_data\n", old_data["data"]["2022"]["12"]["1"][0]["kws"])
# print("recent_data\n", recent_data["metadata"]["year"]["2022"]["kws"]["pays"])