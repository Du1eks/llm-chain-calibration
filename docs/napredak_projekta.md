# Napredak projekta

## 16.09.2026 — Faza 0: planiranje

- Definisana ideja, istraživačko pitanje i hipoteza (v. `plan_projekta.md`).
- Odlučeno: GSM8K matematički zadaci, OpenRouter za pristup modelima,
  single-shot naspram lanca od 3 agenta (Planner → Executor → Verifier).
- Napravljena struktura repozitorijuma.
- Sledeće: OpenRouter nalog, preuzimanje GSM8K podskupa, prompt template
  za single-shot uslov.

## 16–19.09.2026 — Infrastruktura, Uslov A i B implementirani, prvi pun eksperiment

- Promena u odnosu na `plan_projekta.md`: pristup modelu preko Claude API-ja
  direktno (ne OpenRouter) — korisnik ima Anthropic kredit. Model:
  `claude-haiku-4-5` umesto "jednog jakog modela" — dva razloga: (1) budžet
  (100 zadataka × 4 poziva bi sa Opus-om potrošilo skoro ceo kredit), (2)
  validnost — kalibracija se meri nad greškama, a jači model na GSM8K pravi
  premalo grešaka da bi poređenje imalo signal. Extended thinking isključen
  u oba uslova (`temperature=0`, bez `thinking` parametra) da poređenje
  "jedan korak naspram tri koraka" ne bude pomešano sa "model interno
  rezonuje u više koraka".
- Izgrađena cela infrastruktura: `config/config.py` (model, cena, putanje,
  budžetska kočnica), GSM8K loader sa reproducibilnim uzorkovanjem
  (`src/tasks/gsm8k.py`), ocenjivanje odgovora (`src/tasks/grading.py`),
  tanak omotač oko Claude API-ja sa praćenjem troška i tvrdim limitom
  (`src/utils/llm.py`), Pydantic šeme za sve agente (`src/agents/schemas.py`).
- **Napomena o SDK-u**: instalirana verzija `anthropic` (1.6.0) je uklonila
  `temperature` kao tipizirani parametar iz `messages.create()`/`.parse()`.
  Server i dalje prihvata sampling parametre za Haiku 4.5 preko
  `extra_body={"temperature": ...}` — rešeno tako, potvrđeno testom pre
  ugradnje u `llm.py`.
- Implementiran Uslov A (`src/agents/single_shot.py`) i Uslov B — lanac
  Planner → Executor → Verifier (`src/agents/{planner,executor,verifier,chain}.py`).
  Svaki agent u lancu vidi tekst prethodnog koraka, ali **nikad** njegovu
  prijavljenu sigurnost — direktno iz hipoteze u planu.
- **Sonda tačnosti** potvrdila rizik "plafon tačnosti": GSM8K sa
  `min_steps=0` je 100% tačan za Haiku na probi od 20 zadataka — nema
  signala za ECE. Prešli na `min_steps=5` (samo zadaci sa ≥5 kalkulatorskih
  koraka), gde je proba pala na 95% (19/20). Jedina izmena obima uzorka,
  doneta na osnovu izmerenog broja, ne pretpostavke.
- **Pun eksperiment pušten na 100 zadataka (`min_steps=5`, seed=42), oba
  uslova, ukupan trošak ~$0.75:**

  | Metrika | Single-shot (Uslov A) | Lanac (Uslov B) |
  |---|---|---|
  | Tačnost | 97.0% | 78.0% |
  | ECE | 0.0598 | 0.1973 |
  | Brier score | 0.0155 | 0.2079 |

  Bootstrap 95% CI za ECE(A) − ECE(B): **−0.1375, [−0.2262, −0.0641]** —
  interval ne sadrži nulu, razlika je statistički značajna, ne šum.

  **Hipoteza je potvrđena**: lanac agenata je i manje tačan i znatno lošije
  kalibrisan od single-shot poziva istog modela na istim zadacima. Bitno za
  interpretaciju: pad tačnosti (97%→78%) je sam po sebi veliki nalaz — lanac
  ne pravi samo "iste greške sa više sigurnosti", nego uvodi dodatne greške
  (videti pilot iz koraka 6/8: `gsm8k-972`, `gsm8k-39` tačni u single-shot-u,
  pogrešni u lancu) koje prijavljena sigurnost ne prati na dole.
- Grafik: `results/figures/reliability_diagram.png`. Napomena za doterivanje
  (nedelja 9): linije koje spajaju retke binove sa 1–2 zadatka prave
  vizuelni cik-cak u donjem delu grafika — nije greška u računu, vredi
  ukloniti liniju za binove sa malo tačaka pri finalnom poliranju.
- Sledeće: nalaz u README.md (ovaj commit), pa nedelja 8 iz plana — analiza
  gde tačno lanac gubi kalibraciju (Planner vs. Executor vs. Verifier
  confidence, već sačuvani odvojeno u `data/results/chain.jsonl`).
