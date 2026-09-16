# LLM Chain Calibration — plan projekta

Status: faza 0 — planiranje. Početak: 16.09.2026.

## Ideja u dve rečenice

Kad model sam rešava zadatak i prijavi koliko je siguran u odgovor, ta sigurnost
je manje-više kalibrisana — kad kaže 80%, u proseku je u pravu oko 80% puta.
Ovaj projekat testira da li ta kalibracija puca kada isti zadatak ne rešava
jedan model nego lanac agenata (planer → izvršilac → proverivač), gde svaki
korak nasleđuje grešku prethodnog a i dalje prijavljuje visoku sigurnost.

## Istraživačko pitanje

Da li multi-agentski pipeline sistematski precenjuje svoju pouzdanost u odnosu
na jednokratni (single-shot) poziv istog modela, na istim zadacima?

## Hipoteza

Lanac agenata će pokazati veću grešku kalibracije (ECE) nego single-shot,
zato što:
- svaki agent u lancu vidi samo izlaz prethodnog koraka, ne i sopstvenu
  nesigurnost tog koraka,
- verifikator (poslednji korak) ocenjuje da li je odgovor *interno konzistentan*,
  ne da li je *tačan* — pa lako da visoku ocenu pogrešnom, ali urednom,
  rezonovanju.

Ako se hipoteza ne potvrdi — ako nema razlike ili je lanac bolje kalibrisan —
to je i dalje validan, pošten nalaz. Isti princip kao kod EX YU projekta:
izmeriti i prijaviti, ne pretpostaviti.

## Zašto ovo (veza sa dosadašnjim radom)

- `ecomm-orchestrator` (github.com/Du1eks) već implementira odeljenja agenata
  sa handoff ugovorima — ovaj projekat pretvara intuiciju iz tog rada u
  merljivo pitanje.
- Isti metodološki refleks kao u EX YU projektu (izmeriti pouzdanost umesto
  pretpostaviti je) — samo prebačen sa NLP anotacije na agentske sisteme.
- NE dira srpski jezik niti EX YU korpus. Potpuno odvojen projekat, engleski
  od početka (zadaci, kod, nalazi).

## Obim — šta ulazi u prvu verziju

| Odluka | Izbor | Zašto |
|---|---|---|
| Domen zadataka | Matematika (GSM8K, podskup od ~100 zadataka) | Tačnost se proverava automatski (tačno poklapanje broja), nema potrebe za izvršavanjem koda ili ljudskom proverom |
| Pristup modelima | OpenRouter API (jedan ključ, više modela) | Izbegava održavanje 3-4 različita SDK-a; lakša proširenja kasnije |
| Model(i) u prvom prolazu | Jedan jak model (npr. Claude) | Prvo dokazati efekat na jednom modelu pre širenja |
| Uslov A | Single-shot: model rešava zadatak i u istom pozivu prijavljuje sigurnost 0–100% | Kontrolna grupa |
| Uslov B | Lanac od 3 agenta: Planner (rastavi zadatak, prijavi sigurnost u plan) → Executor (izvrši plan korak po korak, prijavi sigurnost u rešenje) → Verifier (proveri rešenje, prijavi finalnu sigurnost) | Finalna sigurnost Verifier-a = "sigurnost sistema" |
| Veličina uzorka | ~100 zadataka po uslovu za prvi prolaz | Dovoljno za grubu ECE procenu, jeftino po API pozivima |
| Format izlaza modela | Strukturiran (JSON: `{"answer": ..., "confidence": ...}`) | Izbegava ručno parsiranje slobodnog teksta |

## Minimalna verzija koja i dalje ima smisla

Ako ponestane vremena pre prvog roka (ETH, 30.11.2026):
- 50 zadataka (ne 100), jedan model, samo matematika.
- I dalje daje broj (ECE za oba uslova) i grafik (reliability diagram) —
  dovoljno da se pomene u prijavi i na razgovoru sa mentorom.

Širenje ako ostane vremena (posle prve verzije):
- Drugi domen zadataka (npr. HumanEval — kod sa testovima).
- Drugi model preko OpenRouter-a, poređenje da li se obrazac ponavlja.
- Analiza GDE tačno lanac gubi kalibraciju — koji korak (Executor ili
  Verifier) najviše doprinosi preteranom pouzdanju. Ovo je najzanimljiviji
  deo ako prva verzija pokaže efekat, analogno `obrasci_neslaganja.md` iz
  EX YU projekta.

## Metrike

- **Expected Calibration Error (ECE)** — grupisati predviđanja po
  prijavljenoj sigurnosti (binovi od po 10%), uporediti prosečnu sigurnost
  sa stvarnom tačnošću po binu.
- **Brier score** — dopunska mera, osetljivija na pojedinačne velike greške.
- **Reliability diagram** — grafik: x = prijavljena sigurnost, y = stvarna
  tačnost, dijagonala = savršena kalibracija.
- Glavno poređenje: ECE(single-shot) naspram ECE(lanac), sa intervalom
  poverenja (bootstrap) da se vidi da li je razlika stvarna ili šum.

## Struktura repozitorijuma

```
llm-chain-calibration/
├── config/
│   └── config.py          # modeli, putanje, OpenRouter podešavanja
├── data/
│   ├── raw/                # preuzet GSM8K podskup
│   └── results/            # sirovi izlazi modela (odgovor + confidence po zadatku)
├── docs/
│   ├── plan_projekta.md    # ovaj fajl
│   └── napredak_projekta.md  # dnevnik napretka (dodaće se)
├── src/
│   ├── tasks/               # učitavanje GSM8K, provera tačnosti odgovora
│   ├── agents/              # single_shot.py, planner.py, executor.py, verifier.py, chain.py
│   ├── eval/                # ece.py, brier.py, reliability_plot.py
│   └── utils/               # OpenRouter klijent, structured output parsing
├── notebooks/
│   └── analiza.ipynb        # interaktivna analiza i grafici
├── results/
│   └── figures/             # reliability dijagrami, ECE poređenja
├── tests/
└── requirements.txt
```

## Plan po nedeljama (budžet: 3–5h nedeljno, ~40h do početka novembra)

| Nedelja | Datum (okvirno) | Zadatak |
|---|---|---|
| 1 | 16–22.09 | Repo skeleton (urađeno). OpenRouter nalog i API ključ. Preuzeti GSM8K podskup (100 zadataka). |
| 2 | 23–29.09 | Prompt template za single-shot sa structured confidence izlazom. Ručno testirati na 5–10 zadataka, proveriti da parsiranje radi. |
| 3 | 30.09–06.10 | Izgraditi lanac (Planner → Executor → Verifier). Ručno testirati na istih 5–10 zadataka. |
| 4 | 07–13.10 | Pun eksperiment, Uslov A (single-shot) na svih ~100 zadataka. Sačuvati sirove rezultate. |
| 5 | 14–20.10 | Pun eksperiment, Uslov B (lanac) na istih ~100 zadataka. |
| 6 | 21–27.10 | Izračunati ECE, Brier, reliability dijagrame za oba uslova. Prva uporedna analiza. |
| 7 | 28.10–03.11 | **Kontrolna tačka: minimalna verzija mora biti gotova do ovde.** Ako ima vremena: drugi model ili drugi domen zadataka. |
| 8 | 04–10.11 | Analiza gde tačno lanac gubi kalibraciju (koji korak). Prvi nacrt README-a i nalaza. |
| 9 | 11–17.11 | Doterivanje, grafici za README, provera da je repo čitljiv nekome ko ga prvi put otvara. |
| 10 | 18–24.11 | Finalno poliranje pre ETH roka (30.11). Odluka da li ide na GitHub kao javan repo. |

Rok ETH je 30.11.2026 — ova tabela cilja da glavni nalaz bude gotov do
sredine novembra, sa nedelju-dve rezerve za pisanje i doterivanje.

## Kriterijum uspeha

- Nalaz postoji i izmeren je, bez obzira na smer: ili je lanac lošije
  kalibrisan (potvrđuje hipotezu — jak nalaz), ili nije (i dalje objavljiv
  negativan rezultat, u skladu sa metodološkim stavom iz EX YU projekta).
- Repo je čitljiv, reprodukovan (neko drugi može da pokrene i dobije iste
  brojeve), i ima kratak, jasan README sa glavnim grafikom.

## Rizici

- **Trošak API poziva** — GSM8K odgovori su kratki, lanac je 3x više poziva
  po zadatku nego single-shot. Za 100 zadataka × (1 + 3) poziva × 1 model,
  trošak je i dalje mali (par dolara). Ne započinjati puni eksperiment pre
  nego što se proceni tačna cena na uzorku od 10 zadataka.
- **Parsiranje confidence vrednosti** — rešava se strogim structured output
  formatom (JSON schema), ne slobodnim tekstom.
- **Vremenski budžet** — 3–5h nedeljno je malo. Minimalna verzija (50
  zadataka, jedan model, jedan domen) je namerno definisana kao "dovoljno
  gotovo" da postoji fallback ako nedelje 4–6 iz tabele kasne.

## Gde ovo ide u prijave

- **EPFL** — Data Science Lab i Machine Learning and Optimization Lab rade
  na pouzdanosti i evaluaciji modela; ovo je konkretan, mali prilog koji se
  može pomenuti ili priložiti.
- **Tsinghua** — NIJE doslovni nastavak study plana koji je već napisan (taj
  je o višejezičnoj evaluaciji). Ovde služi kao opšti signal da kandidat
  rigorozno meri sisteme pre nego što im veruje — ista crta karaktera,
  druga tema.
- **ETH** — manje direktno relevantno za prijem (ETH gleda više na ocene),
  ali koristan materijal za intervju ako do njega dođe.
- Ne menja niti dopunjuje nijedan postojeći fajl u `Desktop/master` folderu.

## Sledeći koraci (odmah)

1. [ ] Napraviti OpenRouter nalog, dobiti API ključ.
2. [ ] Preuzeti GSM8K test split, izvući nasumičan podskup od 100 zadataka
       (fiksiran seed radi ponovljivosti).
3. [ ] Napisati prompt template za single-shot uslov sa JSON izlazom
       (`answer`, `confidence`).
4. [ ] Ručno proveriti izlaz na 5–10 zadataka pre nego što se pokrene bilo
       šta na celom uzorku.
