// Native Typst diagram: no external packages or raster images required.
#let node(body, fill: rgb("#eaf4ef")) = block(
  width: 100%, inset: (x: 7pt, y: 5pt), radius: 3pt,
  above: 0pt, below: 0pt,
  stroke: .5pt + rgb("#91afa3"), fill: fill,
  align(center, body),
)
#let arrow = block(width: 100%, height: 10pt, above: 0pt, below: 0pt)[
  #place(top + center, box(width: 8pt, height: 10pt)[
    #place(top + left, line(start: (4pt, 0pt), end: (4pt, 8pt), stroke: .7pt + rgb("#50675f")))
    #place(top + left, line(start: (1pt, 5pt), end: (4pt, 8pt), stroke: .7pt + rgb("#50675f")))
    #place(top + left, line(start: (7pt, 5pt), end: (4pt, 8pt), stroke: .7pt + rgb("#50675f")))
  ])
]
#let branch-arrow(label) = stack(dir: ttb, spacing: 0pt,
  align(center, text(size: 9pt, weight: "bold", label)), arrow,
)

#let sa-diagram = block(breakable: false)[
  #set text(size: 10pt)
  #set par(justify: false, leading: .35em, spacing: 0pt)
  #stack(dir: ttb, spacing: 0pt,
    node[*Sākums:* bāzes saraksts $x$; labākais $b=x$; iterācija $k=0$.],
    arrow,
    node[*Ja $k<N$:* nosaka $T_k$, izveido kaimiņu $y$, dekodē grafiku un aprēķina $Delta=W(y)-W(x)$.],
    arrow,
    node(fill: rgb("#fff4dc"))[*Pieņemt gājienu?* $Delta<=0$ vai $u<exp(-Delta/T_k)$, kur $u$ nejauši izvēlēts no $[0,1)$.],
    grid(columns: (1fr, 1fr), column-gutter: 8pt, row-gutter: 0pt,
      branch-arrow[ Jā ], branch-arrow[ Nē ],
      node(fill: rgb("#dcf0e7"))[*Pieņemt:* $x=y$. Ja $W(x)<W(b)$, saglabā $b=x$.],
      node(fill: rgb("#faede6"))[*Noraidīt:* pašreizējais $x$ un labākais $b$ nemainās.],
      arrow, arrow,
    ),
    node[*Nākamā iterācija:* $k=k+1$. Ja $k<N$, atgriežas pie kaimiņa izveides ar zemāku $T_k$; citādi *atgriež labāko $b$*.],
  )
]
