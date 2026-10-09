#set document(title: "Trenažieru zāles grafika optimizācija", author: "Gunārs Ābeltiņš")
#set page(paper: "a4", margin: (x: 18mm, y: 16mm), numbering: "1", number-align: center)
#let ink = rgb("#253632")
#let accent = rgb("#083f35")
#set text(font: "Calibri", size: 11pt, lang: "lv", fill: ink)
#set par(justify: false, leading: .5em, spacing: .75em)
#set heading(numbering: "1.")
#show heading.where(level: 1): set text(size: 13pt, fill: accent)
#show heading.where(level: 2): set text(size: 11pt, fill: accent)
#show figure.caption: set text(size: 9pt, fill: rgb("#50675f"))
#set table(
  inset: 5pt,
  stroke: (top: none, left: none, right: none, bottom: .4pt + rgb("#d2e3dd")),
  fill: (x, y) => if y == 0 { rgb("#deeee7") } else if calc.even(y) { rgb("#f1f7f4") } else { white },
)
#show table.cell.where(y: 0): strong
#import "sa_diagram.typ": sa-diagram

#block(width: 100%, fill: rgb("#eaf4ef"), radius: 5pt, inset: 10pt)[
  #text(size: 18pt, weight: "bold", fill: accent)[Trenažieru zāles grafika optimizācija]
  #v(1mm)
  #text(size: 9.5pt)[#link("https://estudijas.lu.lv/course/view.php?id=16881")[Praktiskā kombinatoriālā optimizācija] · Latvijas Universitāte] \
  *Gunārs Ābeltiņš* · studenta apliecības Nr. *ga26014*
]

= Uzdevuma formulējums
Ar pasniedzēju saskaņotais uzdevums ir treniņu plānošana ar *fiksētu
vingrinājumu secību*. Visi cilvēki ierodas laikā 0. Katram vingrinājumam dots
konkrēts aprīkojuma eksemplārs un pozitīvs vesels ilgums minūtēs. Cilvēks un
iekārta vienlaikus piedalās tikai vienā vingrinājumā; tas netiek pārtraukts.
Dažādas iekārtas var lietot paralēli. Atpūtu, pārvietošanos un sagatavošanu ignorē.

Mērķis ir minimizēt *visu cilvēku kopējo gaidīšanas laiku*, ieskaitot gaidīšanu
pirms pirmā vingrinājuma un starp vingrinājumiem:
$ W = sum_(i=1)^n (C_i - sum_(j=1)^(m_i) p_(i j)), $
Te $C_i$ ir treniņa pabeigšanas laiks, $m_i$ ir vingrinājumu skaits un
$p_(i j)$ ir to ilgumi. Pēdējā cilvēka pabeigšanas laiku (*makespan*) ziņo
atsevišķi, bet neoptimizē.

= Algoritma apraksts
== Domēns
Risinājums ir cilvēku identifikatoru saraksts: katrs cilvēks parādās vienu reizi
par katru savu vingrinājumu. Parādīšanās vienmēr nozīmē viņa *nākamo*
vingrinājumu. Piemēram, `[0, 1, 0]` ieplāno cilvēka 0 pirmo, cilvēka 1 pirmo
un cilvēka 0 otro vingrinājumu. Fiksētā secība saglabājas.

== Novērtēšana
Katru vingrinājumu sāk, tiklīdz brīvs gan cilvēks, gan iekārta. To *pievieno
aiz pēdējā ieplānotā vingrinājuma* uz šīs iekārtas; agrākos brīvos intervālos
to neievieto. To izmantošanai jāmaina prioritāšu saraksts. No iegūtā grafika
aprēķina kopējo gaidīšanu un pēdējās pabeigšanas laiku.

== Gājiens
Nejauši izvēlas divas pozīcijas ar atšķirīgiem cilvēku identifikatoriem.
Ar vienādu varbūtību tos samaina vai vienu izņem un ievieto otras pozīcijā.
Identifikatoru skaits saglabājas, tāpēc arī jaunais grafiks ir pieļaujams.

== Algoritms
Izmantota pašrocīgi implementēta *simulētā atkvēlināšana* (SA) Python vidē;
gatavas optimizācijas bibliotēkas nav izmantotas. Bāzes sarakstā vispirms
ir visu cilvēku pirmie vingrinājumi ievades secībā, tad otrie utt.
Diagrammā $x$ ir pašreizējais, $y$ ir kaimiņš un $b$ ir labākais risinājums.
Sliktāku gājienu reizēm pieņem, lai izkļūtu no lokāla minimuma.
Temperatūru ģeometriski samazina no 50 līdz 0,1; beigās atgriež labāko grafiku.
Eksperimentos ir 1000 vai 5000 iterācijas, un nejaušību kontrolē sēkla.

#v(1mm)
#sa-diagram

#pagebreak()
= Testēšanas apraksts
Izveidoti 14 JSON piemēri: 6 mazi un 8 lielāki ar 5, 10, 20 un 30 cilvēkiem,
katram 3 līdz 8 vingrinājumiem. Katrā lielumā ir divi noslodzes varianti.
Katru piemēru testē ar sēklām 0 līdz 4 un abiem iterāciju budžetiem:
kopā *140 SA izpildes*, 14 bāzes grafiki un 6 precīzās meklēšanas izpildes.
Laiku mēra ar `time.perf_counter()`, neiekļaujot pārbaudes un failu saglabāšanu.

== Precīzā meklēšana un pareizības pārbaudes
Maziem piemēriem pašrocīgi pārmeklē visus prioritāšu sarakstus. Zaru atmet,
ja jau uzkrātā gaidīšana sasniedz labāko zināmo vērtību: turpinājumā tā nevar samazināties.

Meklēšana aptver optimumu: jebkura pieļaujama grafika cilvēku un iekārtu
secības veido aciklisku precedences grafu. Tā agrākais izpildījums gaidīšanu
nepalielina, un topoloģisko secību var atveidot ar prioritāšu sarakstu.
Precīzo meklēšanu veic līdz 10 vingrinājumiem, ar 10 sekunžu un
1 000 000 mezglu limitu. Pārtrauktu meklēšanu neatzīmē kā optimālu.

#align(center)[#table(
  columns: (2fr, 1fr, 1fr, 1fr),
  table.header([Mazais piemērs], [Bāze, min], [Optimums, min], [Labākais SA, min]),
  [Viens cilvēks], [0], [0], [0],
  [Bez konfliktiem], [0], [0], [0],
  [Viena iekārta: 3 un 1 min], [3], [1], [1],
  [Krustota iekārtu secība], [0], [0], [0],
  [Atkārtota iekārtas lietošana], [2], [1], [1],
  [Trīs cilvēki], [5], [3], [3],
)]

Visi seši optimumi ir pierādīti; SA tos sasniedza katrā sēklā un budžetā.
Izturēti 8 testi par secību, ilgumiem, pārklāšanos, pilnīgumu, gaidīšanu,
atkārtojamību un limitiem. Precīzais solveris sakrita ar neatkarīgu iekārtu
secību pārmeklēšanu 14 mazos piemēros. Pārbaudīts arī katrs eksperimenta grafiks.

== Lielāko piemēru rezultāti
#text(size: 10pt)[#table(
  columns: (1.5fr, .8fr, .7fr, .9fr, .9fr, .9fr, .8fr),
  table.header([Cilvēki /\ noslodze], [Iek. /\ vingr.], [Bāze], [SA 1000\ labākais], [SA 5000\ labākais], [SA 5000\ vidējais], [SA 5000\ laiks, s]),
  ..eval(read("assets/large_table.typ"), mode: "code"),
)]

Gaidīšanas vērtības ir minūtēs, bet izpildes laiks ir piecu SA izpilžu
vidējais sekundēs. Lielo piemēru optimumi nav pierādīti; tabulā norādīti
labākie novērotie rezultāti. 5000 iterācijas uzlaboja labāko rezultātu 7 no
8 lielajiem piemēriem; `gym_05_low` labākā vērtība palika 14.

#pagebreak()
= Grafiku salīdzinājums un secinājumi
Piemērs `gym_10_high`: 10 cilvēki, 3 iekārtas. Abu grafiku laika mērogs ir
vienāds; krāsa un apzīmējums `P1`, `P2` utt. norāda cilvēku.

#figure(image("assets/baseline_gantt.png", width: 100%),
  caption: [Bāzes grafiks: kopējā gaidīšana 605 min, pēdējā pabeigšana 108 min.])

#figure(image("assets/sa_gantt.png", width: 100%),
  caption: [SA grafiks: sēkla 2, 5000 iterācijas; gaidīšana 376 min, pēdējā pabeigšana 109 min.])

#figure(image("assets/convergence.png", width: 100%),
  caption: [Labākās kopējās gaidīšanas izmaiņas SA izpildes laikā (sēkla 2).])

Gaidīšana samazinās par *37,9 %*, lai gan pēdējais cilvēks pabeidz minūti vēlāk:
abi kritēriji ir atšķirīgi. Attēlos ir sēkla 2; labākais rezultāts piecās
izpildēs ir 337 min, bet vidējais ir 377,2 min.

SA uzlaboja bāzi visos astoņos lielajos piemēros. Pie 30 cilvēkiem un augstas
noslodzes labākā gaidīšana samazinājās no 5304 līdz 3324 min (*37,3 %*).
5000 iterācijas parasti uzlaboja kvalitāti, bet prasīja ilgāku izpildi.
Vienādi temperatūras galapunkti nozīmē arī atšķirīgu dzesēšanas ātrumu.

*Ierobežojumi:* piecas sēklas ir neliels salīdzinājums; temperatūra nav pielāgota
katram piemēram. Noslodzes variantos atšķiras arī treniņi, tāpēc iekārtu skaita
ietekme nav izolēta. Lielo piemēru SA rezultātiem nav optimalitātes garantijas.

= Programmas kods un testa piemēri
*GitHub repozitorijs:* #text(fill: rgb("#9b3c22"))[\[IEVIETOT GITHUB REPOZITORIJA SAITI\]]

Repozitorijā ir Python kods, JSON testa piemēri, CSV mērījumi un palaišanas
instrukcija. Eksperimentus atkārto ar `python main.py experiments`;
pilnie mērījumi ir `results/experiments.csv`.
