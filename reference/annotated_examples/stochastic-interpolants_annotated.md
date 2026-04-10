# stochastic-interpolants

Nota terminologica: nel JSON PaperBench il terzo tipo foglia canonico e` `Result Analysis`; nelle analisi globali precedenti era stato spesso abbreviato come RM / "Result Match". In questo file uso i nomi esatti del codice (`Code Development`, `Code Execution`, `Result Analysis`) e richiamo RM solo come abbreviazione descrittiva.

## A) Header

`stochastic-interpolants` e` il caso piccolo dello split ufficiale: la rubric ha 94 nodi totali, 69 foglie, 25 nodi interni, profondita` massima 5, profondita` media delle foglie 4.01, branching factor medio 3.72 e 4 figli al root. La distribuzione dei tipi foglia e` fortemente sbilanciata verso `Code Development` (58 foglie, 84.1%), con poche foglie `Code Execution` (7, 10.1%) e `Result Analysis` (4, 5.8%).

Questo paper descrive un framework di stochastic interpolants con couplings dipendenti dai dati e lo istanzia in due task ImageNet ben delimitati: in-painting (Section 4.1) e super-resolution (Section 4.2). E` stato scelto come esempio perche' mostra una rubric compatta, molto implementation-heavy, dove la struttura resta leggibile quasi tutta "a colpo d'occhio" e quindi e` utile come caso base per un generatore automatico.

Confronto con i pattern globali di [report.md](../report.md) e [structural_principles.md](../structural_principles.md):

- 94 nodi contro una media `official-20` di 560.90.
- 4 figli al root contro una media ufficiale di 6.85.
- profondita` massima 5 contro una media ufficiale di 5.80.
- profondita` media delle foglie 4.01 contro una media ufficiale di 4.47.
- quota `Code Development` molto sopra la media ufficiale (84.1% vs 53.1%) e anche sopra la media del topic `Diffusion / generative modeling` (57.1%).
- quote `Code Execution` e `Result Analysis` molto sotto le medie ufficiali (10.1% vs 32.9%; 5.8% vs 14.0%).

Snippet del primo livello:

```json
{
  "requirements": "The core contributions of the paper \"Stochastic Interpolants with Data-Dependent Couplings\" have been replicated",
  "sub_tasks": [
    {
      "requirements": "U-Net and ImageNet are available",
      "weight": 2
    },
    {
      "requirements": "The models introduced in the paper have been implemented",
      "weight": 10
    },
    {
      "requirements": "The Frechet Inception Distance (FID) metric has been implemented",
      "weight": 1,
      "task_category": "Code Development"
    },
    {
      "requirements": "The results from Section 4 have been replicated",
      "weight": 10
    }
  ]
}
```

## B) Annotazioni al primo livello

### 1. `U-Net and ImageNet are available` (peso 2)

Questo nodo rappresenta i prerequisiti condivisi: l'implementazione base del backbone U-Net presa da `lucidrains/denoising-diffusion-pytorch` e l'accesso a ImageNet train/validation. La separazione al primo livello e` coerente con il fatto che questi asset servono sia ai modelli del paper sia alla replica dei risultati, quindi non appartengono solo a un singolo esperimento.

Il peso 2, molto inferiore ai due blocchi da 10, suggerisce che la rubric tratti questi prerequisiti come necessari ma non come il cuore della replica. Questa scelta e` coerente con una semantica "gating infrastructure": se mancano, il resto non parte; ma una volta presenti, il contributo valutativo principale si sposta sull'implementazione e sui risultati.

I discendenti sono volutamente poco profondi: due foglie `Code Development`, una per il backbone e una per il dataset. Qui non c'e` ulteriore decomposizione, segnale che il compilatore della rubric considera questi elementi come componenti riusabili e non come mini-pipeline autonome.

### 2. `The models introduced in the paper have been implemented` (peso 10)

Questo e` il blocco metodologico principale. Riflette direttamente il fatto che il paper presenta due famiglie operative per in-painting e super-resolution: un modello con dependent coupling per entrambi i task e un baseline uncoupled solo per l'in-painting, coerente con Section 4.1 e 4.2 del paper.

La scelta di tenerlo come figlio diretto del root e` naturale: qui non si stanno ancora validando numeri o eseguendo run, ma si sta codificando la sostanza metodologica del paper. Il peso 10 lo mette sullo stesso piano del blocco risultati: nella semantica locale dei pesi, "costruire correttamente gli oggetti del paper" e "replicare gli outcome sperimentali" valgono quanto i due macro-obiettivi principali.

La struttura sottostante e` organizzata per combinazione `task x variante`:

- Dependent Coupling for in-painting
- Uncoupled Interpolant for in-painting
- Dependent Coupling for super-resolution

All'interno di ciascuno, la decomposizione segue spesso `training -> sampling`, e dentro `training` i figli scendono fino ai dettagli di preparazione input, interpolant, loss, masking e ottimizzazione.

### 3. `The Frechet Inception Distance (FID) metric has been implemented` (peso 1)

Questo nodo isola l'infrastruttura di valutazione usata nelle Section 4.1 e 4.2. Separarlo al root e` coerente con il fatto che FID sia una dipendenza comune ai due blocchi risultati e non un dettaglio di un solo task.

Detto questo, qui la scelta strutturale non e` forzata dal paper in modo univoco: lo stesso contenuto avrebbe potuto essere annidato sotto il blocco risultati. La rubric preferisce invece promuoverlo a foglia indipendente di primo livello, probabilmente per trattarlo come capability trasversale riusabile.

Il peso 1 e` il minimo tra i fratelli: indica chiaramente che la metrica, pur necessaria, non e` considerata un contributo centrale comparabile alla corretta implementazione dei modelli o alla replica dei claim.

### 4. `The results from Section 4 have been replicated` (peso 10)

Questo nodo rappresenta l'intero blocco sperimentale del paper. La dicitura richiama esplicitamente "Section 4", quindi la decomposizione a valle e` guidata piu' dalla struttura del paper che da una tassonomia astratta della pipeline.

Il peso 10 lo mette sullo stesso livello del blocco `The models introduced in the paper have been implemented`. Questa simmetria e` coerente con una rubric che assegna meta' del valore principale al "costruire bene" e meta' al "far vedere che il sistema riproduce i risultati".

I tre figli mostrano una preview molto chiara della struttura sottostante:

- `The correct hyperparameters have been implemented` raccoglie i dettagli sperimentali trasversali.
- `The results from Section 4.1 have been implemented` e` il blocco in-painting.
- `The results from Section 4.2 have been implemented` e` il blocco super-resolution.

Questa organizzazione e` particolarmente utile come esempio per un generatore automatico: prima si separano setup condiviso e sottosezioni sperimentali, poi dentro ogni sottosezione si segue il pattern `Execution -> Result Analysis`.

## C) Annotazioni ai livelli intermedi

### Sottoalbero 1: dependent coupling per in-painting

Snippet:

```json
{
  "requirements": "The Dependent Coupling model for the in-painting experiment has been implemented",
  "weight": 2,
  "sub_tasks": [
    {
      "requirements": "Training the Dependent Coupling model for in-painting has been implemented, following Algorithm 1",
      "weight": 1
    },
    {
      "requirements": "Sampling with the Dependent Coupling model for in-painting has been implemented, following Algorithm 2",
      "weight": 1
    }
  ]
}
```

La logica di decomposizione e` algoritmica: il paper fornisce esplicitamente `Algorithm 1` per training e `Algorithm 2` per sampling, quindi la rubric riprende questa stessa partizione. Questo e` un pattern importante: quando il paper ha pseudocodice o procedure nominate, la rubric tende a ricalcare quella segmentazione.

Il branching factor qui e` basso e pulito: 2 figli al nodo del modello, poi 8 foglie nel training e 3 nel sampling. Questo riflette il fatto che l'implementazione del training richiede piu' micro-decisioni del sampling forward Euler.

I pesi sono quasi uniformi ai livelli profondi, con piccoli aumenti su step piu' composizionali come "masked image is constructed" e sull'update iterativo di sampling. E` coerente con una rubric che premia leggermente di piu' le foglie che fungono da macro-step rispetto a dettagli secondari come l'optimizer.

### Sottoalbero 2: dependent coupling per super-resolution

Questo sottoalbero ha la stessa dorsale `training -> sampling`, ma il training e` piu' ramificato rispetto all'in-painting perche' la preparazione dell'input corrotto richiede una mini-pipeline di trasformazioni: crop/downsample, nearest-neighbor upsample, aggiunta di rumore, concatenazione lungo i canali.

In altre parole, il branching factor maggiore non rappresenta "piu' scienza" rispetto all'in-painting, ma piu' passaggi osservabili nella costruzione del dato d'ingresso. Questa corrispondenza tra branching e numero di trasformazioni concrete del paper e` uno dei segnali strutturali piu' utili da imitare.

Anche qui i pesi sono localmente quasi uniformi, ma le foglie che definiscono l'interpolant, il time derivative, il masking della velocity field e la loss hanno peso 2, mentre alcuni dettagli di preprocessing o optimizer hanno peso 1. La distribuzione e` coerente con una gerarchia "equation-level mechanics > supporting setup".

### Sottoalbero 3: risultati di Section 4.1

Snippet:

```json
{
  "requirements": "The results from Section 4.1 have been implemented",
  "weight": 4,
  "sub_tasks": [
    {
      "requirements": "The experiments required to replicate results in Section 4.1 have been executed",
      "weight": 1,
      "sub_tasks": [
        {
          "requirements": "The Uncoupled Interpolant model is trained on ImageNet",
          "task_category": "Code Execution"
        },
        {
          "requirements": "Using the Uncoupled Interpolant model that has been trained on ImageNet, FID-50k is computed on the ImageNet validation set",
          "task_category": "Code Execution"
        },
        {
          "requirements": "The Dependent Coupling model is trained on ImageNet",
          "task_category": "Code Execution"
        },
        {
          "requirements": "Using the Dependent Coupling model that has been trained on ImageNet, FID-50k is computed on the ImageNet validation set",
          "task_category": "Code Execution"
        }
      ]
    },
    {
      "requirements": "The recorded metrics show that the results from Section 4.1 have been replicated",
      "weight": 2
    }
  ]
}
```

La decomposizione qui e` per fase sperimentale: prima si eseguono i run, poi si giudicano i numeri ottenuti. E` esattamente il pattern globale trovato in [structural_principles.md](../structural_principles.md): quando nello stesso sottoalbero compaiono piu' tipi, l'ordine preferito e` `Code Development -> Code Execution -> Result Analysis`.

Il peso 2 assegnato al nodo di `Result Analysis` rispetto al peso 1 del nodo `Code Execution` e` interessante: localmente, una volta che i run sono stati eseguiti, la rubric attribuisce piu' importanza al fatto che i numeri finali stiano davvero vicino al claim del paper. Questo non implica che le singole foglie `Result Analysis` pesino piu' delle foglie `Code Development` in assoluto; e` una priorita` locale all'interno di questo blocco.

## D) Annotazioni alle foglie

### Foglie `Code Development`

#### CD-1

```json
{
  "requirements": "Code for accessing the train and validation sets from the ImageNet dataset has been implemented",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questa formulazione e` tipica dello stile PaperBench: apertura operativa (`Code for ...`) e chiusura prescrittiva (`has been implemented`). E` classificata come `Code Development` perche' richiede di costruire una capability software, non di eseguirla o di verificarne un output numerico.

La relazione col parent `U-Net and ImageNet are available` e` chiara: e` una delle due dipendenze di base del progetto. L'ordinamento rispetto al fratello U-Net non sembra codificare una dipendenza forte; entrambe sono prerequisiti, e l'ordine appare piu' enumerativo che causale.

#### CD-2

```json
{
  "requirements": "During training the Dependent Coupling model for in-painting, for each $i$-th sample in each mini-batch, the mask is drawn randomly by tiling the image into 64 tiles of equal sizes; each tile is selected to enter the mask with probability $p = 0.3$",
  "weight": 2,
  "task_category": "Code Development"
}
```

Questa foglia e` un buon esempio del registro lessicale delle rubric implementation-heavy: descrive una micro-operazione concreta, localizzata nel tempo (`During training`) e nella granularita` del dato (`for each i-th sample in each mini-batch`). E` `Code Development` perche' prescrive logica da implementare.

Rispetto ai fratelli, sta dentro il nodo intermedio `the masked image is constructed`, insieme al vincolo "same value for all channels" e alla formula di applicazione della maschera. L'ordine dei tre fratelli e` coerente con una dipendenza morbida: prima si genera la maschera, poi si specifica la sua forma canale-wise, infine la si applica all'immagine con rumore.

#### CD-3

```json
{
  "requirements": "During training the Dependent Coupling model for in-painting, the approximate velocity field $b_t(x, \\xi)$ is defined such that $b_t(x, \\xi) = 0$ except in the masked regions of the image; the output of the approximate velocity field is masked to enforce that the unmasked pixels remain fixed...",
  "weight": 2,
  "task_category": "Code Development"
}
```

Questa foglia cattura un vincolo strutturale del metodo, non solo un dettaglio implementativo. E` comunque `Code Development` perche' il giudizio riguarda la presenza della giusta logica nel codice del modello.

Nel contesto del parent `Training ... following Algorithm 1`, questa foglia e` complementare a quelle su interpolant, derivative e loss: i fratelli definiscono gli oggetti matematici usati dal training, mentre questa foglia impone la forma del campo di velocita` nel caso specifico di in-painting. L'ordine rispetto ai fratelli sembra quasi curricolare: dati di input -> tempo -> interpolant -> derivative -> velocity field -> loss -> optimizer.

### Foglie `Code Execution`

#### EX-1

```json
{
  "requirements": "The Uncoupled Interpolant model is trained on ImageNet",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` il prototipo perfetto di `Code Execution`: non chiede di implementare un componente, ma di effettuare effettivamente un run. Sta sotto `The experiments required to replicate results in Section 4.1 have been executed`, quindi il tipo e` determinato dalla fase della pipeline, non dal contenuto teorico.

L'ordinamento rispetto ai fratelli e` significativo: compare prima del calcolo FID del medesimo modello, il che e` coerente con una dipendenza concreta train-then-evaluate.

#### EX-2

```json
{
  "requirements": "Using the Uncoupled Interpolant model that has been trained on ImageNet, FID-50k is computed on the ImageNet validation set",
  "weight": 1,
  "task_category": "Code Execution"
}
```

E` ancora `Code Execution`, non `Result Analysis`, perche' la foglia riguarda l'atto di produrre la metrica, non l'interpretazione del suo valore. Questa distinzione e` importante per un generatore automatico: "compute X" resta esecuzione; "X is around Y" diventa analisi del risultato.

La relazione col fratello precedente e` esplicitamente dipendente nel testo: `Using the ... model that has been trained`. Qui la dipendenza e` codificata sia semanticamente sia nell'ordine dei figli.

#### EX-3

```json
{
  "requirements": "Using the Dependent Coupling model that has been trained on ImageNet, FID-50k is computed on the ImageNet train set by comparing against 50k random samples from the training set",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia viene dalla Section 4.2 e mostra come la rubric vari il requirement quando il paper riporta piu' di una misura. La formulazione esplicita il dataset di confronto e il protocollo `50k random samples`, quindi non chiede un generico "valuta il modello", ma uno specifico step eseguibile.

Nel parent di Section 4.2 l'ordine e` di nuovo train -> metriche, con train set FID prima di validation FID. La scelta sembra coerente con l'ordine in cui vengono elencati i numeri finali; non e` possibile inferire dal solo codice della rubric se questo ordine abbia una semantica piu' forte di quella narrativa.

### Foglie `Result Analysis`

#### RM-1

```json
{
  "requirements": "The Uncoupled Interpolant model achieves FID-50k around 1.35",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

La formulazione tipica di `Result Analysis` qui e` molto netta: soggetto del modello + verbo di risultato (`achieves`) + target numerico approssimato (`around 1.35`). Non chiede di calcolare FID, ma di verificare che il valore osservato sia vicino al claim del paper.

La relazione con il parent `The recorded metrics show that the results from Section 4.1 have been replicated` e` diretta: il parent aggrega interpretazione, i figli fissano i singoli numeri attesi. Compare prima del modello dependent, coerentemente con l'ordine con cui nella Section 4.1 si confrontano baseline e metodo proposto.

#### RM-2

```json
{
  "requirements": "The Dependent Coupling model achieves FID-50k around 1.15",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia e` complementare alla precedente: insieme formano la coppia minima necessaria per valutare il claim comparativo di Section 4.1. Il testo e` quasi isomorfo, e questa simmetria lessicale e` un pattern utile da imitare quando due varianti devono essere confrontate sulle stesse metriche.

L'ordine dopo la baseline e` coerente con una lettura "prima il riferimento, poi il metodo con coupling". E` una dipendenza narrativa debole ma plausibile.

#### RM-3

```json
{
  "requirements": "The Dependent Coupling model achieves validation FID-50k around 2.05 for the super-resolution task",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia mostra l'altra forma ricorrente dei result nodes nel benchmark: stessa struttura verbale, ma con qualificatore del contesto sperimentale (`validation`, `for the super-resolution task`). E` sempre `Result Analysis` perche' il criterio e` la vicinanza del numero riportato, non la procedura che lo genera.

Sta accanto al fratello `train FID-50k around 2.15`, con cui divide parent e peso. La coppia illustra bene come la rubric scomponga un claim sperimentale multivalore in foglie parallele anziche' in un'unica foglia composita.

## E) Pattern chiave da replicare

- In un paper piccolo e ben focalizzato, il root puo' avere pochi figli se ciascuno corrisponde a una macro-funzione distinta: prerequisiti, modelli, infrastruttura metrica, risultati.
- Quando il paper e` organizzato per task sperimentali chiaramente nominati, la rubric tende a riflettere direttamente quelle sezioni (`4.1`, `4.2`) invece di introdurre categorie nuove.
- Se il paper contiene procedure nominate o pseudocodice (`Algorithm 1`, `Algorithm 2`), la rubric spesso le riusa come nodi intermedi espliciti.
- In questo caso il blocco modelli e` puramente `Code Development`, mentre `Code Execution` e `Result Analysis` vengono confinati quasi interamente al blocco risultati.
- L'ordine locale dei nodi segue bene il pattern globale `Code Development -> Code Execution -> Result Analysis`, pur in una rubric molto piu' CD-dominante della media.
- I pesi al primo livello non sono uniformi: i prerequisiti e la metrica condivisa pesano meno dei due blocchi centrali (`models`, `results`).
- Ai livelli profondi, i pesi sono quasi sempre piccoli interi locali (1 o 2) e distinguono soprattutto tra macro-step composizionali e dettagli di supporto.
- Le foglie `Code Development` usano uno stile molto prescrittivo e proceduralizzato: `During training...`, `When sampling...`, `Code for ... has been implemented`.
- Le foglie `Code Execution` descrivono run osservabili e metriche da produrre, spesso con dipendenza lessicale esplicita dal training gia` avvenuto (`Using the model that has been trained...`).
- Le foglie `Result Analysis` usano una sintassi regolare orientata al claim numerico: `The [model] achieves [metric] around [value]`.
- La separazione del nodo FID al primo livello e` coerente con un'infrastruttura di valutazione condivisa, ma non e` una conseguenza obbligata del paper; e` quindi un buon esempio di scelta strutturale plausibile ma non unica.
