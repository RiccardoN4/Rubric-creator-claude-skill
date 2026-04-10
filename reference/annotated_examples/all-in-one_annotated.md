# all-in-one

Nota terminologica: nel JSON PaperBench il terzo tipo foglia canonico e` `Result Analysis`; nelle analisi aggregate era spesso abbreviato come RM / "Result Match". In questo file uso i nomi esatti del codice.

## A) Header

`all-in-one` e` il caso piu' vicino alla media strutturale del benchmark tra quelli selezionati: 234 nodi totali, 174 foglie, 60 nodi interni, profondita` massima 6, profondita` media delle foglie 4.25, branching factor medio 3.88, 5 figli al root. La distribuzione dei tipi foglia e` `Code Development` 92 (52.9%), `Code Execution` 62 (35.6%), `Result Analysis` 20 (11.5%).

Il paper introduce il Simformer, un metodo di simulation-based inference che vuole essere davvero "all-in-one": apprende congiuntamente posterior, likelihood e altri conditionali arbitari, sfrutta attention masks strutturate e guided diffusion per vincoli/intervals. E` stato scelto come esempio perche' il mix dei tipi e` quasi identico alle medie globali e del topic `Simulation-based inference`, quindi e` un ottimo caso guida per insegnare a un generatore automatico che cosa assomiglia a una rubric "tipica" del benchmark.

Confronto con i pattern globali di [report.md](../report.md) e [structural_principles.md](../structural_principles.md):

- 234 nodi contro una media `official-20` di 560.90.
- 5 figli al root contro una media ufficiale di 6.85.
- profondita` massima 6 contro una media ufficiale di 5.80.
- profondita` media delle foglie 4.25, molto vicina alla media ufficiale di 4.47.
- distribuzione dei tipi quasi sovrapponibile al topic `Simulation-based inference`: qui 52.9% / 35.6% / 11.5% contro 52.7% / 35.6% / 11.8%.
- distribuzione molto vicina anche alla media globale sulle foglie per `Code Development` (53.1%) e abbastanza vicina per `Code Execution` (32.9%) e `Result Analysis` (14.0%).

Questo file e` particolarmente utile perche' mostra un pattern diverso sia da `stochastic-interpolants` sia da `robust-clip`:

- il root non e` dominato da sezioni sperimentali separate;
- c'e` invece un grande blocco top-level `results` che ingloba tutte le Section 4.1-4.4;
- il metodo e la preparazione vengono esplicitamente tenuti fuori da quel blocco.

Snippet del primo livello:

```json
{
  "requirements": "The paper \"All-in-one simulation-based inference\" has been reproduced.",
  "sub_tasks": [
    {
      "requirements": "Variance Exploding SDE (VESDE) is implemented, as described in A2.1",
      "weight": 1
    },
    {
      "requirements": "The Simformer model, training process and inference process has been implemented",
      "weight": 3
    },
    {
      "requirements": "Baseline methods Neural Posterior Estimation (NPE), Neural Ratio Estimation (NRE), and Neural Likelihood Estimation (NLE) are implemented",
      "weight": 1
    },
    {
      "requirements": "The benchmark tasks are prepared",
      "weight": 1
    },
    {
      "requirements": "The recorded metrics show that the results from section 4 are replicated",
      "weight": 6
    }
  ]
}
```

## B) Annotazioni al primo livello

### 1. `Variance Exploding SDE (VESDE) is implemented, as described in A2.1` (peso 1)

Questo nodo isola una dipendenza metodologica comune a tutto il paper: la parametrizzazione SDE concreta usata in pratica. Tenerlo al primo livello e` coerente con il fatto che VESDE non appartiene a un singolo benchmark applicativo, ma all'intero stack del metodo.

Il peso 1 segnala che e` un prerequisito metodologico necessario, ma non il cuore valutativo della replica. I suoi discendenti sono pochi e diretti: drift, diffusion, perturbation kernel, costanti e time range.

### 2. `The Simformer model, training process and inference process has been implemented` (peso 3)

Questo e` il blocco metodologico centrale: tokenizer, transformer, masks, loss, sampling di conditionali arbitrari, guided diffusion per intervals. E` coerente con il paper, che in Section 3 presenta il metodo come composizione di questi ingredienti.

Il peso 3 lo pone nettamente sopra prerequisiti e baseline, ma ancora sotto il macro-blocco risultati da 6. Questo suggerisce una semantica molto PaperBench: costruire il metodo conta molto, ma la prova finale resta la riuscita empirica complessiva.

La struttura sottostante e` organizzata per capacità fondamentali del modello:

- architettura/tokenizer;
- masks;
- training;
- sampling;
- interval conditioning.

Questa organizzazione, per capability del metodo, e` un pattern molto utile da imitare.

### 3. `Baseline methods Neural Posterior Estimation (NPE), Neural Ratio Estimation (NRE), and Neural Likelihood Estimation (NLE) are implemented` (peso 1)

Questo figlio raccoglie il blocco baseline. La sua separazione al root e` coerente con il paper: le baseline non sono dettagli periferici di una singola figura, ma fanno parte del setup sperimentale trasversale.

Il peso 1 e` basso, coerente con un ruolo di supporto/comparazione. La rubric non espande qui i benchmark, ma solo le scelte implementative di riferimento: libreria `sbi`, batch size, optimizer, early stopping.

### 4. `The benchmark tasks are prepared` (peso 1)

Questo nodo raccoglie l'intero "task zoo" usato dal paper: benchmark classici, Tree, HMM, Lotka-Volterra, SIRD, Hodgkin-Huxley, piu' C2ST. Tenerlo al primo livello e` coerente con il fatto che i task sono un'infrastruttura comune riutilizzata in piu' sezioni dei risultati.

Il peso 1 indica che, come le baseline, questo blocco e` trattato come preparazione indispensabile ma non come claim finale.

### 5. `The recorded metrics show that the results from section 4 are replicated` (peso 6)

Questo e` il vero fulcro dell'albero. Il fatto che tutto il blocco risultati di Section 4 sia raccolto sotto un solo figlio del root e` la scelta strutturale piu' importante di questa rubric. A differenza di `robust-clip`, dove le sezioni sperimentali erano gia` al primo livello, qui il root separa chiaramente "build the world" da "validate the claims".

Il peso 6, il piu' alto di tutto il primo livello, rende esplicito che l'output sperimentale aggregato e` il driver principale del punteggio. I discendenti mostrano una sottostruttura molto regolare:

- hyperparameters shared across results;
- VESDE choice shared across results;
- Section 4.1 benchmark tasks;
- Section 4.2 Lotka-Volterra;
- Section 4.3 SIRD;
- Section 4.4 Hodgkin-Huxley.

Questa e` probabilmente la miglior lezione strutturale dell'intera rubric: un root compatto, con un solo macro-blocco risultati, dentro il quale le sezioni del paper si dispiegano con ordine.

## C) Annotazioni ai livelli intermedi

### Sottoalbero 1: implementazione del Simformer

Snippet:

```json
{
  "requirements": "The Simformer model, training process and inference process has been implemented",
  "weight": 3,
  "sub_tasks": [
    {
      "requirements": "The Simformer architecture and tokenizer has been implemented",
      "weight": 2
    },
    {
      "requirements": "The condition and attention masks are correctly computed for each sample passed to the Simformer",
      "weight": 2
    },
    {
      "requirements": "The code for training the Simformer model has been implemented",
      "weight": 2
    },
    {
      "requirements": "Code for sampling arbitrary conditionals from a trained Simformer model has been implemented",
      "weight": 2
    },
    {
      "requirements": "The Simformer supports conditioning on intervals.",
      "weight": 1
    }
  ]
}
```

La logica di decomposizione e` per capacità costitutive del metodo, non per sezione del paper. Questo e` coerente con Section 3, che presenta il Simformer come un insieme di moduli: tokenizer, masks, denoising score matching, arbitrary conditionals, guided diffusion.

Il branching factor e` moderato e uniforme: 5 figli, con quattro blocchi da peso 2 e uno da peso 1. L'interval conditioning e` presente ma trattato come estensione della pipeline, coerente con il fatto che nel paper e` importante ma entra soprattutto in Section 4.4.

### Sottoalbero 2: Section 4.1 benchmark tasks

Snippet:

```json
{
  "requirements": "The recorded metrics show that the results in section 4.1 have been replicated",
  "weight": 3,
  "sub_tasks": [
    {
      "requirements": "Simformers used for all experiments in Section 4.1 have 6 layers",
      "weight": 1
    },
    {
      "requirements": "The experiments in 4.1 related to approximating the posterior distribution have been replicated",
      "weight": 3
    },
    {
      "requirements": "The experiments in 4.1 related to evaluating arbitrary conditionals have been replicated",
      "weight": 3
    }
  ]
}
```

Questo sottoalbero segue con grande fedelta` la struttura della sezione risultati del paper:

- una piccola premessa di setup specifico (6 layers);
- un blocco per la parte "posterior approximation" di Fig. 4a;
- un blocco per la parte "arbitrary conditionals" di Fig. 4b.

Il dato strutturale piu' utile e` che qui il sottoalbero e` dominato da `Code Execution` (46 foglie su 51 nella Section 4.1). Non perche' il paper sia meno tecnico, ma perche' la rubric interpreta la comparazione sistematica task x model x simulation-budget come una batteria di run da enumerare esplicitamente.

### Sottoalbero 3: Section 4.4 observation intervals

Snippet:

```json
{
  "requirements": "The recorded metrics show that the results in section 4.4 have been replicated",
  "weight": 3,
  "sub_tasks": [
    {
      "requirements": "The Simformer used for all experiments in Section 4.4 has 8 layers",
      "weight": 1
    },
    {
      "requirements": "The Simformer used in Section 4.4 uses the dense attention mask",
      "weight": 1
    },
    {
      "requirements": "Results when inferring the posterior distribution given only the summary statistics have been replicated",
      "weight": 4
    },
    {
      "requirements": "Results when applying an observation interval have been replicated",
      "weight": 4
    }
  ]
}
```

Qui la logica di decomposizione e` "scenario A vs scenario B": prima inferenza standard da summary statistics, poi inferenza sotto vincolo energetico via guided diffusion. Questa struttura riflette bene la narrativa della sezione, che prima stabilisce il caso base e poi introduce il constraint.

Il branching factor resta basso ma i pesi cambiano molto: i due nodi scenario hanno peso 4, i due nodi di setup hanno peso 1. E` coerente con una rubric che tratta `layers` e `dense attention mask` come condizioni sperimentali, e i due blocchi di inferenza come veri claim da verificare.

## D) Annotazioni alle foglie

### Foglie `Code Development`

#### CD-1

```json
{
  "requirements": "The drift term for Variance Exploding SDE is defined as $f(x, t)=0$",
  "weight": 2,
  "task_category": "Code Development"
}
```

Questa foglia e` rappresentativa dello stile "equation-first" della rubric: requirement breve, matematicamente preciso, direttamente allineato con Appendix A2.1. E` `Code Development` perche' verifica una scelta implementativa nel codice del metodo.

All'interno del parent VESDE, compare prima delle costanti, coerentemente con una micro-gerarchia da definizione del processo a iperparametri del processo.

#### CD-2

```json
{
  "requirements": "During training, for each training sample, the condition mask $M_C$ is randomly sampled as either 1) the joint distribution ... 5) a Bernoulli distribution with p=0.7 ...",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questa foglia e` molto importante per il generatore automatico: mostra come una regola apparentemente semplice del metodo venga trasformata in un requirement lungo, enumerativo e proceduralizzato. E` `Code Development` perche' descrive la logica di sampling del mask durante il training.

Nel parent `The condition and attention masks are correctly computed ...`, questa foglia precede la parte sull'attention mask. L'ordine e` coerente con una dipendenza naturale: prima definisci cosa e` osservato/non osservato, poi adatti le dipendenze nel grafo.

#### CD-3

```json
{
  "requirements": "Algorithm 1 has been fully implemented to sample from conditions specified by the constraint function.",
  "weight": 3,
  "task_category": "Code Development"
}
```

Questa foglia mostra come la rubric promuova a singola foglia pesante un blocco algoritmico intero quando il paper fornisce pseudocodice esplicito. E` `Code Development` perche' il focus e` l'implementazione dell'algoritmo di guided diffusion, non il suo output numerico.

Sta sotto `The Simformer supports conditioning on intervals.` insieme a self-recurrence, constraint function e scaling function. L'ordine e` da ingredienti dell'algoritmo a implementazione completa, quindi abbastanza chiaramente dipendente.

### Foglie `Code Execution`

#### EX-1

```json
{
  "requirements": "For the Linear Gaussian task, NPE has been trained for 10^3, 10^4, and 10^5 simulations (in separate training runs)",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` il prototipo del blocco benchmark di `all-in-one`: tantissime foglie `Code Execution` quasi isomorfe che enumerano training runs sistematici per task e budget. E` esecuzione pura, non implementazione.

L'ordinamento con i fratelli e` regolare e quasi tabellare: prima baseline/metodo 1, poi metodo 2, ecc. Non sembra raccontare una dipendenza forte, ma piuttosto seguire una matrice task x model.

#### EX-2

```json
{
  "requirements": "For the SLCP task, for each model trained for 10^3, 10^4, and 10^5 simulations, Classifier Two-Sample Test accuracy between the model-generated posteriors and ground-truth posteriors have been calculated",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` utile perche' delimita bene il confine tra `Execution` e `Result Analysis`: calcolare C2ST resta `Code Execution`; dire che Simformer richiede 10x meno simulazioni o che tutti i modelli stanno sotto una certa soglia diventa `Result Analysis`.

Nel parent della Section 4.1, segue naturalmente dopo training runs e posterior samples. Qui l'ordine dei fratelli codifica una pipeline abbastanza esplicita: train -> sample -> score -> analyze.

#### EX-3

```json
{
  "requirements": "The Simformer trained on 10^5 simulations of Lotka-Volterra is used with a dense attention mask to infer the posterior distribution on a uniform grid between t=0 and t=15, given the four synthetic observations and posterior predictive samples for unobserved predator and prey variables.",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia rappresenta bene la parte applicativa del paper. E` `Code Execution` perche' chiede di eseguire concretamente un'istanza del metodo su un caso sintetico definito, non solo di implementarne il supporto.

Nel parent `Samples from the Simformer have been generated, conditioning on four synthetic prey observations`, viene dopo la generazione delle osservazioni e prima del check qualitativo sul ground-truth. Anche qui l'ordine e` chiaramente dipendente.

### Foglie `Result Analysis`

#### RM-1

```json
{
  "requirements": "Across all four benchmark tasks ... all Simformer variants almost always outperform neural posterior estimation (NPE) wrt. C2ST accuracy",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia cattura il claim principale di Section 4.1. Lo stile e` tipico dei result nodes comparativi PaperBench: aggregazione su piu' task, avverbio di tendenza (`almost always`), metrica esplicita.

Sta nel nodo intermedio `Results Analysis`, che raccoglie solo tre foglie ad alta densita` semantica. La struttura e` molto chiara: prima esegui tantissimi run, poi sintetizzi i claim globali in poche foglie analitiche.

#### RM-2

```json
{
  "requirements": "Using the Simformer trained for 10^5 simulations of Lotka-Volterra, the C2ST performance (posterior distribution) is below 0.65",
  "weight": 2,
  "task_category": "Result Analysis"
}
```

Qui la result analysis assume forma soglia-centrica: non confronto qualitativo, ma criterio numerico da soddisfare. E` comunque `Result Analysis` perche' il requirement verifica la qualita` dell'esito, non la procedura di calcolo.

Nel parent `The recorded metrics show that results in section 4.2 have been replicated.`, questo nodo vive accanto a un altro result node per arbitrary conditionals. La coppia mostra bene come la rubric scinda il claim di Section 4.2 in due metriche finali parallele.

#### RM-3

```json
{
  "requirements": "The additional constraint on energy consumption significantly constrained the parameters posterior, in particular the maximal sodium and potassium conductances",
  "weight": 2,
  "task_category": "Result Analysis"
}
```

Questa foglia e` un buon esempio di result node non puramente numerico: qui si verifica un effetto strutturale atteso del constraint, non soltanto un singolo valore. E` molto coerente con Section 4.4, dove il claim del paper riguarda la capacita` di guided diffusion di restringere la posterior sotto un vincolo energetico.

Nel parent `Results when applying an observation interval have been replicated`, compare dopo la foglia di execution che applica guided diffusion e prima dei checks finali su energia sotto soglia e posterior predictive trace. L'ordine segue quindi `apply constraint -> observe structural effect -> check downstream consequences`.

## E) Pattern chiave da replicare

- Una rubric "tipica" puo' avere pochi figli al root se il root separa macro-funzioni forti: metodo, baseline, task prep, risultati.
- In un paper con forte componente metodologica, il root puo' avere un singolo grande figlio `results` che ingloba tutte le sezioni sperimentali, invece di mettere ogni sezione del paper direttamente al primo livello.
- Il blocco `results` puo' essere l'unico figlio molto pesante del root, mentre metodo e preparazione restano piu' leggeri ma distinti.
- All'interno del blocco risultati, le sottosezioni del paper (`4.1`, `4.2`, `4.3`, `4.4`) vengono poi recuperate quasi uno-a-uno.
- Section 4.1 mostra un pattern molto forte di enumerazione sistematica dei run: task x model x simulation budget diventa una griglia di foglie `Code Execution`.
- Quando il paper ha claim globali sintetici dopo una grande griglia sperimentale, la rubric tende a comprimerli in poche foglie `Result Analysis` ad alto contenuto semantico.
- Le foglie `Code Development`, `Code Execution` e `Result Analysis` qui sono quasi perfettamente bilanciate rispetto alle medie globali/topic: questo rende la rubric un buon template generale.
- L'ordine locale segue molto bene il pattern globale `Code Development -> Code Execution -> Result Analysis`, specialmente dentro il macro-blocco `results`.
- I pesi locali distinguono bene setup da scenario/result block: setup spesso 1, scenari o blocchi di claim 3-4.
- Le rubriche per paper "all-in-one" tendono a riflettere non solo le sezioni del paper, ma anche la ripetizione del medesimo schema su piu' casi applicativi: `setup specifico -> scenario 1 -> scenario 2 -> metriche/claim finali`.
