# robust-clip

Nota terminologica: nel JSON PaperBench il terzo tipo foglia canonico e` `Result Analysis`; nelle analisi aggregate precedenti era spesso abbreviato come RM / "Result Match". In questo file uso i nomi esatti del codice.

## A) Header

`robust-clip` e` una rubric di taglia medio-piccola ma con struttura molto diversa da `stochastic-interpolants`: 146 nodi totali, 106 foglie, 40 nodi interni, profondita` massima 5, profondita` media delle foglie 3.52, branching factor medio 3.62 e 6 figli al root. Le foglie sono distribuite come segue: `Code Development` 70 (66.0%), `Code Execution` 8 (7.5%), `Result Analysis` 28 (26.4%).

Il paper introduce FARE, una procedura di adversarial fine-tuning non supervisionato per rendere robusto il vision encoder CLIP senza riaddestrare i downstream LVLM. La struttura della rubric riflette molto da vicino l'organizzazione del paper: setup iniziale, fine-tuning, valutazione Section 4.1, targeted attacks Section 4.2, zero-shot classification Section 4.3, e benchmark aggiuntivi Section 4.4.

Perche' questo esempio e` importante:

- e` vicino alla mediana dimensionale del benchmark ma ha una quota di `Result Analysis` molto alta;
- mostra una decomposizione quasi "table-driven", guidata dalle sezioni sperimentali piu' che dal solo metodo;
- e` utile per capire come PaperBench annota rubriche in cui gran parte del valore sta nella verifica di trend comparativi, non solo nell'implementazione.

Confronto con i pattern globali di [report.md](../report.md) e [structural_principles.md](../structural_principles.md):

- 146 nodi contro una media `official-20` di 560.90.
- 6 figli al root, vicino alla media ufficiale di 6.85.
- profondita` massima 5 contro una media ufficiale di 5.80.
- profondita` media delle foglie 3.52, ben sotto la media ufficiale di 4.47.
- `Result Analysis` molto sopra la media ufficiale (26.4% vs 14.0%) e sopra la media del topic `Vision / OOD / robustness` (15.9%).
- `Code Execution` molto sotto la media ufficiale (7.5% vs 32.9%) e sotto la media del topic (35.5%).
- `Code Development` resta dominante, ma meno estremamente che nel caso piccolo (66.0% vs media ufficiale 53.1%).

Snippet del primo livello:

```json
{
  "requirements": "The core contributions of the paper have been reproduced.",
  "sub_tasks": [
    {
      "requirements": "The relevant visual and text encoders, as well as the relevant models, have been successfully configured and imported.",
      "weight": 1
    },
    {
      "requirements": "The models have been fine-tuned correctly, consistent with section 3 and Appendix B.",
      "weight": 2
    },
    {
      "requirements": "The experiments for evaluation on the common tasks from language model literature, listed in Section 4.1, have been correctly reproduced.",
      "weight": 3
    },
    {
      "requirements": "The experiments for evaluating robustness to targeted attacks from section 4.2 have been reproduced.",
      "weight": 2
    },
    {
      "requirements": "The experiments from section 4.3 for the evaluation of zero-shot classification have been reproduced.",
      "weight": 2
    },
    {
      "requirements": "LLaVA, with TeCoA and FARE as the backbone vision models, has been successfully evaluated on hallucinations, chain of thought, and jailbreaking, as in section 4.4.",
      "weight": 2
    }
  ]
}
```

## B) Annotazioni al primo livello

### 1. `The relevant visual and text encoders, as well as the relevant models, have been successfully configured and imported.` (peso 1)

Questo nodo raccoglie il bootstrap tecnico: LLaVA, OpenFlamingo, i due encoder CLIP, e il freezing corretto del solo text encoder. La separazione al primo livello e` coerente con il fatto che tutte le valutazioni successive dipendono da questo wiring iniziale, ma non coincide ancora con una specifica sezione sperimentale del paper.

Il peso 1 indica che la rubric tratta questo blocco come prerequisito: necessario, ma non principale. I discendenti sono quasi tutti foglie dirette `Code Development`, quindi il nodo ha funzione di "import/configuration gate" piu' che di pipeline autonoma.

### 2. `The models have been fine-tuned correctly, consistent with section 3 and Appendix B.` (peso 2)

Questo nodo rappresenta la sostanza metodologica del paper: implementazione di PGD, training loop TeCoA, training loop FARE, e iperparametri di fine-tuning su ImageNet. E` corretto che sia figlio diretto del root perche' corrisponde al contributo tecnico centrale, separato dai benchmark a valle.

Il peso 2, maggiore del setup ma inferiore al blocco Section 4.1, e` coerente con una rubric che considera importante la correttezza del metodo ma assegna ancora piu' massa alla valutazione sul benchmark principale.

La struttura sottostante e` mista:

- una decomposizione per componenti algoritmiche (`PGD`, `TeCoA loop`, `FARE loop`);
- una decomposizione per protocollo di training (`ImageNet`, epochs, optimizer, schedule, batch size).

### 3. `The experiments for evaluation on the common tasks from language model literature, listed in Section 4.1, have been correctly reproduced.` (peso 3)

Questo e` il blocco piu' pesante del primo livello. La scelta e` coerente con il paper: Section 4.1 copre il benchmark piu' ampio e "main-paper-facing", con OF e LLaVA, quattro dataset, attacchi untargeted, tabella principale e transfer attacks.

E` importante che questo nodo sia separato dal resto del primo livello invece di essere fuso con 4.2 o 4.3: la rubric segue molto da vicino il layout del paper e tratta Section 4.1 come macro-unità autonoma. I suoi figli corrispondono a dataset prep, metriche, pipeline d'attacco, riproduzione dei trend di Table 1, e transfer attacks.

### 4. `The experiments for evaluating robustness to targeted attacks from section 4.2 have been reproduced.` (peso 2)

Qui la rubric isola il blocco "stealthy targeted attacks" del paper. Questo figlio ha senso al primo livello perche' la Section 4.2 introduce un protocollo diverso, una diversa nozione di successo dell'attacco, target strings specifiche e un diverso tipo di claim rispetto alla Section 4.1.

Il peso 2, inferiore alla Section 4.1 ma allineato con 4.3 e 4.4, e` coerente con un blocco importante ma secondario rispetto alla tabella comparativa principale del paper.

### 5. `The experiments from section 4.3 for the evaluation of zero-shot classification have been reproduced.` (peso 2)

Questo nodo raccoglie l'altra grande faccia del paper: non solo LVLM robustness, ma anche trasferimento su zero-shot classification con un ampio set di dataset. La separazione a root riflette fedelmente il fatto che Section 4.3 usa un protocollo di evaluation diverso da 4.1 e 4.2.

La struttura sottostante e` piu' piatta di quanto il paper potrebbe suggerire: dataset import, prompt-template averaging, attacchi AutoAttack, e poi un nodo risultati con forte contenuto `Result Analysis`. Questo e` uno dei motivi per cui la profondita` media del paper resta bassa.

### 6. `LLaVA, with TeCoA and FARE as the backbone vision models, has been successfully evaluated on hallucinations, chain of thought, and jailbreaking, as in section 4.4.` (peso 2)

Questo nodo segue Section 4.4 quasi come un mini-indice: hallucinations/POPE, SQA-I, jailbreaking. Il fatto che tre benchmark abbastanza diversi siano raggruppati nello stesso figlio e` coerente con il paper, che li presenta come "other tasks" e non come contributi metodologici separati.

Il peso 2 suggerisce che la rubric li considera estensioni importanti dei claim principali, ma non superiori a 4.1. Anche qui la preview strutturale e` nitida: per ciascun benchmark compaiono quasi sempre tre fasi, `implement/setup -> run/report -> trend analysis`.

## C) Annotazioni ai livelli intermedi

### Sottoalbero 1: fine-tuning del metodo

Snippet:

```json
{
  "requirements": "The models have been fine-tuned correctly, consistent with section 3 and Appendix B.",
  "weight": 2,
  "sub_tasks": [
    {
      "requirements": "The PGD algorithm has been implemented correctly.",
      "weight": 1
    },
    {
      "requirements": "The training loop for TeCoA has been implemented correctly, consistent with section 3.2.",
      "weight": 1
    },
    {
      "requirements": "The training loop for FARE has been implemented correctly, consistent with section 3.3.",
      "weight": 1
    },
    {
      "requirements": "TeCoA^2, TeCoA^4, FARE^2, and FARE^4 have been trained correctly via finetuning on ImageNet, using the hyperparameters in section B.1.",
      "weight": 1
    }
  ]
}
```

La logica di decomposizione qui e` "metodo + protocollo": prima i componenti algoritmici, poi il training concreto dei quattro modelli robusti. Questa struttura riflette bene il paper, che alterna Section 3 (loss e formulazione) e Appendix B.1/B.3 (dettagli di training).

Il branching factor e` basso e regolare: 4 figli quasi equiponderati, poi ulteriore espansione solo dove servono dettagli operativi. La scelta e` coerente con il fatto che TeCoA e FARE sono descritti come varianti relativamente compatte del fine-tuning, non come pipeline multi-stage molto ramificate.

I pesi qui sono quasi tutti 1: la rubric non segnala una gerarchia forte tra PGD, loss e hyperparameters. Per un generatore automatico, questo suggerisce che nei blocchi metodologici di paper simili i dettagli di training sono trattati come checklist quasi-uniforme.

### Sottoalbero 2: Section 4.1 come benchmark principale

Snippet:

```json
{
  "requirements": "The experiments for evaluation on the common tasks from language model literature, listed in Section 4.1, have been correctly reproduced.",
  "weight": 3,
  "sub_tasks": [
    {
      "requirements": "The image captioning datasets and the visual question answering datasets listed in Section 4.1 have been correctly prepared.",
      "weight": 1
    },
    {
      "requirements": "The evaluation metrics for image captioning and visual question answering have been correctly implemented.",
      "weight": 1
    },
    {
      "requirements": "The pipeline of untargeted high-precision and low-precision attacks ... has been correctly implemented ...",
      "weight": 2
    },
    {
      "requirements": "Versions of OF and LLaVA have been correctly evaluated on the datasets, and their trends match those in table 1 ...",
      "weight": 2
    },
    {
      "requirements": "The transfer attacks from Section 4.1 have been correctly reproduced.",
      "weight": 2
    }
  ]
}
```

Questa e` la parte piu' istruttiva della rubric. Il nodo segue quasi perfettamente la narrativa della sezione:

- prepara i dataset;
- implementa metriche;
- implementa la pipeline d'attacco;
- produce la tabella principale e ne verifica i trend;
- aggiunge i transfer attacks.

Il branching factor riflette il fatto che Section 4.1 non e` un singolo esperimento ma un bundle di benchmark correlati. A differenza di `stochastic-interpolants`, qui il sottoalbero non e` organizzato attorno a `training -> sampling`, ma attorno a `benchmark plumbing -> attack protocol -> comparative outcomes`.

I pesi 2 assegnati alla attack pipeline, ai risultati Table 1 e ai transfer attacks sono coerenti con l'importanza relativa di questi tre blocchi rispetto al solo dataset prep/metric prep. Non e` una prova che siano "piu' importanti" in senso assoluto; e` pero' un chiaro segnale di priorita` locale.

### Sottoalbero 3: Section 4.4 e, in particolare, jailbreaking

Snippet:

```json
{
  "requirements": "The jailbreaking attacks are correctly evaluated on LLaVA with TeCoA, FARE, and the original CLIP encoder ...",
  "weight": 2,
  "sub_tasks": [
    {
      "requirements": "A single image is prepared for the jailbreaking attacks to be run on.",
      "weight": 1,
      "task_category": "Code Development"
    },
    {
      "requirements": "The jailbreaking attacks and prompts are implemented correctly.",
      "weight": 1,
      "task_category": "Code Development"
    },
    {
      "requirements": "The jailbreaking attacks are set to have the following parameters: 5000 iterations and alpha = 1/255.",
      "weight": 1,
      "task_category": "Code Development"
    },
    {
      "requirements": "Jailbreaking attacks are run on LLaVA with CLIP, FARE^4, and TeCoA^4 ...",
      "weight": 1,
      "task_category": "Code Execution"
    },
    {
      "requirements": "The number of passed prompts is reported ... in a format comparable to Table 7.",
      "weight": 1,
      "task_category": "Code Execution"
    },
    {
      "requirements": "The trends are consistent with those in section 4.4 ...",
      "weight": 4
    }
  ]
}
```

Questo sottoalbero e` quasi un esempio da manuale del pattern globale trovato in [structural_principles.md](../structural_principles.md): preparazione e implementazione (`Code Development`), esecuzione e reporting (`Code Execution`), poi interpretazione dei trend (`Result Analysis`), con ordine coerente `CD -> EX -> RM`.

Il dettaglio piu' forte e` il peso 4 assegnato al nodo finale di trend analysis. Questo rende esplicito che, in una sezione paper-driven di benchmarking, la rubric valuta soprattutto se l'output riproduce il claim comparativo corretto, non solo se la pipeline gira.

## D) Annotazioni alle foglie

### Foglie `Code Development`

#### CD-1

```json
{
  "requirements": "LLaVA-1.5 7B is set up to use the OpenAI CLIP ViT-L/14@224 vision encoder (rather than the default ViT-L/14@336).",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questa foglia e` rappresentativa perche' mostra uno dei pattern lessicali piu' tipici nelle rubric PaperBench: configurazione puntuale di una scelta non-default. E` `Code Development` perche' il giudizio riguarda una modifica di wiring/configurazione nel codice.

La relazione col parent `The models for LLaVA-1.5 7B ... have been correctly configured and imported.` e` strettissima: i fratelli sono altre scelte strutturali di caricamento e compatibilita` tra stack software. L'ordine non sembra codificare una dipendenza dura, ma una checklist di setup.

#### CD-2

```json
{
  "requirements": "The visual encoder is properly isolated from the text encoder, ensuring that only the visual encoder weights are updated during fine-tuning while the text encoder weights remain frozen.",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questa foglia e` un buon esempio di requirement ibrido tra architettura e training protocol. E` comunque `Code Development` perche' chiede che il codice imponga una specifica policy di aggiornamento dei parametri.

Sta allo stesso livello dei nodi di import/configurazione perche' la separazione dei pesi aggiornabili e` trattata come parte del setup di base del metodo. La rubric non la annida sotto TeCoA o FARE, scelta coerente con il fatto che il freezing del text encoder e` trasversale.

#### CD-3

```json
{
  "requirements": "For the COCO samples with score at least 10, and for the Flickr30k samples with score at least 2, an additional single precision attack is made ... using the ground-truth that led to the lowest score for each sample.",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questa foglia mostra lo stile dei requirement per attack pipelines: non un generico "run APGD", ma una micro-regola di controllo del flusso. E` `Code Development` perche' prescrive logica di orchestrazione dell'esperimento.

Nel parent `The attack pipeline has been correctly implemented for image captioning`, compare dopo la parte di tracking dei CIDEr e prima dei risultati finali, in modo coerente con una dipendenza procedurale: prima misuri e salvi il best-so-far, poi decidi quali campioni meritano l'attacco single-precision.

### Foglie `Code Execution`

#### EX-1

```json
{
  "requirements": "For each (vision encoder, VLM) pair, for each type of attack (clean, epsilon = 2/255, epsilon = 4/255), the average over the metrics has been computed and reported.",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` utile perche' chiarisce un pattern importante di PaperBench: quando il requirement riguarda la produzione effettiva di una tabella o di un aggregato numerico, il tipo puo' diventare `Code Execution` anche se il testo contiene `computed and reported`.

Sta dopo due foglie `Code Development` che preparano le metriche per dataset, e prima dei nodi `Result Analysis` che interpretano i trend. L'ordine e` quindi coerente con la sequenza globale `prepare -> compute/report -> judge`.

#### EX-2

```json
{
  "requirements": "The total number of successful attacks (out of 25) is reported, for each (target, epsilon, encoder) tuple.",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Qui `Code Execution` coincide con il reporting strutturato del protocollo targeted attack. Il requirement non chiede ancora di dire se FARE e` migliore di TeCoA; chiede di produrre i conteggi necessari.

Rispetto ai fratelli della Section 4.2, questa foglia fa da ponte tra la parte puramente implementativa dei target attacks e il nodo successivo `The trends ... are consistent`, che e` invece interamente analitico.

#### EX-3

```json
{
  "requirements": "The POPE scores (Adversarial, Popular, and Random) have been calculated for the five visual encoders with LLaVA.",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` rappresentativa del fatto che in `robust-clip` la categoria `Code Execution` e` usata soprattutto per benchmark evaluation e reporting, non per lunghi training run. E` un buon contrasto con altri paper dove `Execution` corrisponde soprattutto a training/evaluation loops.

Nel suo parent, compare tra `The POPE benchmark has been implemented correctly.` e `The above POPE scores have been reported ...`, quindi la sequenza dei fratelli riflette chiaramente una dipendenza lineare.

### Foglie `Result Analysis`

#### RM-1

```json
{
  "requirements": "Compared to TeCoA, FARE overall has better clean performance and better robust performance.",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questo e` il prototipo del result node comparativo: non fissa un numero, ma un trend aggregato tra metodi. La classificazione `Result Analysis` e` inevitabile, perche' la foglia verifica un'interpretazione del risultato, non la produzione della tabella.

Sta nel nodo `Versions of OF and LLaVA have been correctly evaluated ... and their trends match those in table 1 ...`, insieme ad altri claim sintetici derivati da Table 1. I fratelli formano quindi una lista di "claims to recover" piu' che di operazioni da eseguire.

#### RM-2

```json
{
  "requirements": "The original CLIP encoder attains the best performance on clean data.",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia mostra il secondo stile tipico di `Result Analysis`: claim qualitativo semplice, quasi headline-like. E` breve, assertiva, e completamente orientata al confronto.

Nel parent `The performance of the original CLIP encoder on clean and robust examples follows the trends described in Section 4.1.`, i due figli sono ordinati in modo molto naturale: prima clean best-performance, poi poor robustness. Questo accoppia le due facce del messaggio principale sul CLIP base.

#### RM-3

```json
{
  "requirements": "FARE and TeCoA defend against significantly more attacks than CLIP.",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia, dal blocco jailbreaking, e` rappresentativa perche' condensa in una sola frase il claim ad alto livello della tabella. Lo stile e` coerente con molti result nodes del benchmark: soggetti multipli, verbo comparativo, baseline esplicita.

E` figlia del nodo `The trends are consistent ...`, che ha peso locale 4 nel sottoalbero jailbreaking. Questo segnala che, in questa sezione, la rubric attribuisce molta importanza alla corretta lettura del pattern globale dei risultati.

## E) Pattern chiave da replicare

- In paper benchmark-heavy, il primo livello puo' ricalcare quasi direttamente la struttura delle sezioni sperimentali del paper.
- Un singolo figlio del root puo' corrispondere a un'intera sezione (`4.1`, `4.2`, `4.3`, `4.4`) se quella sezione ha un protocollo di evaluation distinto.
- La profondita` puo' restare relativamente bassa anche in presenza di molti benchmark, se i claims vengono attaccati direttamente ai nodi di sezione e non a lunghi sottoalberi per dataset.
- In questa rubric `Result Analysis` e` molto piu' presente della media: non perche' ci siano tante metriche numeriche puntuali, ma perche' la rubric codifica esplicitamente molti trend comparativi del paper.
- `Code Execution` qui non coincide soprattutto con training runs; coincide spesso con il calcolo/reporting di score, conteggi e tabelle.
- I blocchi valutativi mostrano bene il pattern globale `Code Development -> Code Execution -> Result Analysis`, spesso in forma quasi lineare.
- I pesi al root non sono uniformi: Section 4.1 riceve il peso piu' alto, coerentemente con il suo ruolo di benchmark principale; setup iniziale resta al minimo.
- Nei sottoalberi di benchmarking i nodi `Result Analysis` possono ricevere localmente piu' peso dei nodi operativi, perche' la rubric valuta soprattutto se i claim del paper vengono realmente recuperati.
- Le foglie `Code Development` hanno spesso tono configurativo o procedurale (`is set up to`, `has been implemented`, `are implemented correctly`), non necessariamente centrato sul training.
- Le foglie `Result Analysis` usano molto la lingua dei trend (`best`, `better`, `worse`, `rivalled`, `do not transfer well`, `roughly equally effective`) piu' che target numerici puntuali.
- La separazione tra `report numbers` e `judge trends` e` netta: produrre la tabella e` execution, interpretarne il significato comparativo e` result analysis.
