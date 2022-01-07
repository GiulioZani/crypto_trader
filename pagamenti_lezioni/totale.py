import json

dati = json.load(open('data.json'))
ore_fatte = dati["ore_fatte"]
pagamenti = dati["pagamenti"]
totale_ore = sum([ore for _, ore in ore_fatte])
euro_ora = 13.0
totale_euro = totale_ore*euro_ora
totale_pagati = sum([euro for _, euro in pagamenti])
cronologia_lezioni = '\n'.join([f'{data} {ora}h' for data, ora in ore_fatte])
cronologia_pagamenti = '\n'.join([f'{date} €{euro}' for date, euro in pagamenti])

print(
f"""

Cronologia lezioni (calcolato in ore, es: 1.25=1:15):
{cronologia_lezioni}

Cronologia pagamenti:
{cronologia_pagamenti}

ore totali:{totale_ore}
euro l'ora:{euro_ora}
totale:€{totale_euro}

debito:€{totale_euro - totale_pagati}
""")
