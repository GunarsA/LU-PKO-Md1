# Pārskats latviešu valodā

`report.typ` ir rediģējamais Typst avots, bet `report.pdf` ir 3 lappušu pārskats.
Dokuments ietver prasītās sadaļas, faktiskos eksperimentu rezultātus, divus Ganta
grafikus, SA konverģences līkni un algoritma plūsmas diagrammu. Diagramma ir
rediģējama failā `sa_diagram.typ` un izmanto tikai Typst iebūvētos elementus.

Pārskatā ir iekļauta saite uz repozitoriju:
[GunarsA/LU-PKO-Md1](https://github.com/GunarsA/LU-PKO-Md1).

Ar instalētu Typst, no projekta galvenās mapes:

```console
typst compile report/report.typ report/report.pdf
```

Mapē `assets` ir mērījumu CSV kopija, ilustrāciju izpildes JSON kopijas,
ģenerētās tabulas šūnas un attēli. Typst dokumenta kompilēšanai Python nav vajadzīgs.
CSV kopija fiksē tieši pārskatā izmantotos mērījumus un to izpildes laikus.

Ja vēlies pārgatavot attēlus un tabulu no projekta aktuālajiem rezultātiem:

```console
python -m pip install -r requirements.txt
python report/prepare_assets.py
typst compile report/report.typ report/report.pdf
```

Sagatavošanas skripts izmanto `results/experiments.csv`,
`results/report/baseline.json` un `results/report/sa.json`. Pēc jauniem
eksperimentiem pārbaudi arī pārskata tekstā ierakstītos secinājumus un skaitļus;
skripts tos automātiski nepārraksta. `preview-*.png` ir PDF vizuālās pārbaudes attēli.
