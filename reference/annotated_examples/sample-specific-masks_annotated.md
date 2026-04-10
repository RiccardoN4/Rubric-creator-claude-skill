# sample-specific-masks

Nota terminologica: nel JSON PaperBench il terzo tipo foglia canonico e` `Result Analysis`; nelle analisi aggregate era spesso abbreviato come RM / "Result Match". In questo file uso i nomi esatti del codice.

Nota sul naming: il paper usa sistematicamente `SMM` ("sample-specific multi-channel masks"), ma nella rubric compaiono anche `SSM` e `SNS`. Quando cito nodi o requirement mantengo la stringa esatta del JSON invece di normalizzarla.

## A) Header

`sample-specific-masks` propone una variante di visual reprogramming in cui la maschera non e` piu' condivisa da tutti i campioni: un piccolo CNN genera maschere sample-specific e un modulo di patch-wise interpolation le riallinea alla dimensione del pattern. Il paper combina una parte metodologica relativamente compatta con una batteria sperimentale molto ampia su ResNet, ViT, ablation e visualizzazioni di feature space.

Dal punto di vista strutturale questa rubric e` un caso volutamente atipico e molto utile: 396 nodi totali, 331 foglie, 65 nodi interni, profondita` massima 6, profondita` media delle foglie 4.86, branching factor medio 6.08, 5 figli al root. La distribuzione dei tipi foglia e` `Code Development` 87 (26.3%), `Code Execution` 223 (67.4%), `Result Analysis` 21 (6.3%).

E` stata scelta come esempio perche' mostra il lato "execution-heavy" del benchmark: rispetto alla media `official-20` di [report.md](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/report.md), ha meno figli al root (5 contro 6.85), foglie piu' profonde (4.86 contro 4.47) e soprattutto una quota di `Code Execution` enormemente superiore sia alla media globale (67.4% contro 32.9%) sia alla media del topic `Vision / OOD / robustness` (67.4% contro 35.5%). Questa deviazione e` coerente con il fatto che il paper verifica molte combinazioni metodo x backbone x dataset x seed, e la rubric sceglie di espandere esplicitamente quella matrice.

Snippet del primo livello:

```json
{
  "requirements": "The paper \"Sample-specific Masks for Visual Reprogramming-based Prompting\" has been replicated",
  "sub_tasks": [
    {
      "requirements": "Code for making the required models and datasets available has been implemented",
      "weight": 1
    },
    {
      "requirements": "Iterative label mapping is implemented, following Chen et al. (2023)",
      "weight": 2
    },
    {
      "requirements": "The baselines have been implemented",
      "weight": 4
    },
    {
      "requirements": "SSM has been implemented",
      "weight": 10
    },
    {
      "requirements": "The results from section 5 have been replicated",
      "weight": 10
    }
  ]
}
```

Questa decomposizione e` coerente con il principio globale di [structural_principles.md](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/structural_principles.md): il root non e` spezzato semplicemente per sezioni, ma per blocchi semantici maggiori. I primi quattro figli sono infrastruttura/metodo; solo l'ultimo figlio raccoglie il grosso delle verifiche empiriche di Section 5.

## B) Annotazioni al primo livello

### 1. `Code for making the required models and datasets available has been implemented` (peso 1)

Questo nodo rappresenta l'infrastruttura minima condivisa: modelli pre-trained e accesso ai dataset. E` coerente tenerlo al primo livello perche' questi elementi servono trasversalmente a tutte le parti successive della rubric, non a una sola sezione del paper.

Il peso 1 e` il piu' basso possibile tra i fratelli, il che e` coerente con un ruolo di prerequisito. I discendenti sono organizzati in due inventari paralleli: un piccolo inventario di backbone (`ResNet-18`, `ResNet-50`, `ViT-B32`) e un inventario piu' largo dei dataset usati negli esperimenti.

### 2. `Iterative label mapping is implemented, following Chen et al. (2023)` (peso 2)

Questo figlio isola il meccanismo di output mapping che il paper eredita da Chen et al. (2023) e usa sistematicamente nei risultati principali. Tenerlo al primo livello, separato da `SSM has been implemented`, e` coerente con il fatto che il label mapping non e` una proprieta' interna del solo mask generator, ma una dipendenza concettuale riutilizzata da baseline e metodo proposto.

Il peso 2 lo colloca sopra la semplice disponibilita' di modelli e dataset ma sotto i blocchi centrali di metodo e risultati. I suoi discendenti sono pochi e ordinati: prima il calcolo delle frequenze di label assignment, poi il calcolo vero e proprio dell'output mapping.

### 3. `The baselines have been implemented` (peso 4)

Questo nodo rappresenta l'intera famiglia di metodi di confronto `Pad`, `Narrow`, `Medium`, `Full`. E` coerente tenerlo al primo livello perche' nel paper le baseline non sono dettagli accessori: definiscono il contesto competitivo dentro cui il contributo di SMM viene giudicato in Section 5.

Il peso 4 e` intermedio-alto: maggiore dei prerequisiti, ma ancora ben sotto i due blocchi da 10. La struttura sottostante e` molto regolare: quattro figli quasi simmetrici, uno per baseline, e dentro ciascuno una sequenza di foglie che elenca inizializzazione del pattern, costruzione/applicazione della maschera, forward nel backbone, label mapping, loss e aggiornamento tramite gradient descent.

### 4. `SSM has been implemented` (peso 10)

Questo e` il blocco del contributo metodologico principale. Al primo livello e` ben posizionato: Section 3 del paper introduce una nuova architettura e una nuova procedura di training, quindi trattarla come figlio diretto del root e` coerente con il fatto che la replica deve prima ricostruire l'oggetto tecnico centrale del paper.

Il peso 10, a pari merito con il macro-blocco risultati, segnala che la rubric considera metodo ed evidenza empirica come i due pilastri principali della replica. I discendenti sono organizzati per componente funzionale: resize iniziale, mask generator, patch-wise interpolation, learning strategy. Questa decomposizione e` molto aderente alla struttura di Section 3.

### 5. `The results from section 5 have been replicated` (peso 10)

Questo nodo raccoglie quasi tutto il carico empirico della rubric: 303 nodi e 257 foglie, di cui 222 `Code Execution`, 21 `Result Analysis` e 14 `Code Development`. Tenerlo al primo livello, invece di distribuire tutte le sottosezioni sperimentali direttamente tra i figli del root, e` coerente con un pattern "method/setup first, evidence second".

Il peso 10 uguale al blocco `SSM has been implemented` riflette una scelta strutturale molto chiara: la replica vale tanto per la ricostruzione del metodo quanto per la sua verifica sperimentale. I discendenti sono organizzati come un piccolo indice della sezione sperimentale: hyperparameters, `Results on ResNets`, `Results on ViT`, `Impact of Masking`, `Impact of Patch Size`, `Feature Space Visualization Results`.

## C) Annotazioni ai livelli intermedi

### Sottoalbero 1: `SSM has been implemented`

Snippet:

```json
{
  "requirements": "SSM has been implemented",
  "weight": 10,
  "sub_tasks": [
    {
      "requirements": "For SSM, each input image is resized using bilinear interpolation to match the expected size of the mask generator",
      "weight": 1
    },
    {
      "requirements": "The mask generator module is implemented, following Section 3.2",
      "weight": 6
    },
    {
      "requirements": "The Patch-wise Interpolation Module is implemented, following Section 3.3",
      "weight": 4
    },
    {
      "requirements": "The learning strategy is implemented, following Algorithm 1",
      "weight": 3
    }
  ]
}
```

La logica di decomposizione e` per componenti del metodo, non per esperimenti. Questo e` esattamente quello che ci si aspetta leggendo Section 3 del paper: prima si definisce la pipeline `resize -> mask generator -> interpolation -> training loop`, poi si discute il perche' teorico.

Il branching factor qui e` basso ma non uniforme, e questo e` informativo. Il nodo sul `mask generator` riceve peso 6, quindi piu' del `Patch-wise Interpolation Module` (4) e della `learning strategy` (3): questa scelta e` coerente con il fatto che il generatore di maschere e` la novita' architetturale piu' specifica del paper. In piu', questo sottoalbero e` quasi interamente `Code Development` (26 foglie su 27), con una sola foglia `Code Execution`; e` quindi un buon esempio di blocco metodologico puro.

### Sottoalbero 2: `The experiments and results for the "Results on ResNets" subsection have been replicated`

Snippet:

```json
{
  "requirements": "The experiments and results for the \"Results on ResNets\" subsection have been replicated",
  "weight": 6,
  "sub_tasks": [
    {
      "requirements": "The experiments under the \"Results on ResNets\" subsection have been executed",
      "weight": 1
    },
    {
      "requirements": "The results under the \"Results on ResNets\" subsection have been replicated",
      "weight": 6
    }
  ]
}
```

Questo sottoalbero mostra bene perche' la rubric e` execution-dominant. Ha 134 nodi totali e 119 foglie: 110 `Code Execution` e 9 `Result Analysis`, senza quasi nessun `Code Development`. La logica di decomposizione non e` per singolo dataset o per singolo backbone al primo step; prima si separano `experiments` e `results`, poi dentro `experiments` si enumerano i due backbone e dentro ciascun backbone i cinque metodi, e solo in fondo si scende ai dataset.

Il branching factor effettivo cresce man mano che si scende: 2 figli in alto, poi 2 backbone, poi 5 metodi, poi 11 dataset. Questo riflette molto fedelmente la tabella risultati del paper: la rubrica la "srotola" in una matrice eseguibile. Il peso 6 assegnato al nodo risultati, contro 1 assegnato all'esecuzione aggregata, suggerisce che l'esecuzione e` necessaria ma il claim da verificare resta comparativo.

### Sottoalbero 3: `The ablation-study experiments and results for the "Impact of Masking" subsection have been replicated`

Snippet:

```json
{
  "requirements": "The ablation-study experiments and results for the \"Impact of Masking\" subsection have been replicated",
  "weight": 6,
  "sub_tasks": [
    {
      "requirements": "The SMM variants for the \"Impact of Masking\" subsection have been implemented",
      "weight": 1
    },
    {
      "requirements": "The experiments under the \"Impact of Masking\" subsection have been executed",
      "weight": 1
    },
    {
      "requirements": "The results under the \"Impact of Masking\" subsection have been replicated",
      "weight": 4
    }
  ]
}
```

Questo e` uno dei sottoalberi piu' istruttivi dell'intera rubric perche' realizza esplicitamente il pattern di fase osservato globalmente: `Code Development -> Code Execution -> Result Analysis`. In [structural_principles.md](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/structural_principles.md) questo ordinamento appare nel 95.5% dei sottoalberi ufficiali che contengono tutti e tre i tipi; qui lo si vede in forma molto pulita.

La logica di decomposizione e` per variante di ablation e poi per fase. Prima si definiscono i tre variant (`only delta`, `only f_mask`, `single-channel`), poi si eseguono le run su ViT-B32, poi si verificano tre claim riassuntivi. Il peso 4 sul nodo risultati, contro 1 e 1 sui due blocchi precedenti, e` coerente con la funzione dell'ablation nel paper: non basta eseguire varianti, bisogna mostrare che supportano la lettura causale proposta dagli autori.

## D) Annotazioni alle foglie

Le foglie qui sotto sono scelte per coprire tre usi ricorrenti di ciascun tipo: infrastruttura/metodo/ablation per `Code Development`, training-run/procedura/analisi per `Code Execution`, claim aggregato/claim puntuale/claim visuale per `Result Analysis`.

### Foglie `Code Development`

#### CD-1

```json
{
  "requirements": "Code for accessing the train and test splits from the CIFAR10 dataset has been implemented",
  "weight": 1,
  "task_category": "Code Development"
}
```

Il requirement e` formulato in modo molto atomico: una sola capacita' verificabile, con sintassi inventariale ripetuta identica per tutti gli altri dataset. E` `Code Development` perche' descrive la disponibilita' di una capability nel codebase, non un run o un claim sui risultati.

La relazione con i fratelli e` puramente enumerativa: questa foglia e` una voce dell'inventario dataset sotto `Code for accessing the required datasets has been implemented`. L'ordinamento rispetto ai fratelli sembra riflettere soprattutto l'ordine con cui i dataset vengono elencati negli esperimenti, non una dipendenza forte.

#### CD-2

```json
{
  "requirements": "In the mask generator module in SSM, given a three-channel image as input with height H and width W, the mask generator outputs a three-channel mask with dimensions floor(H/2^l) x floor(W/2^l), where l denotes the number of pooling layers in the mask generator CNN",
  "weight": 1,
  "task_category": "Code Development"
}
```

Qui il requirement e` piu' tecnico e piu' vicino al testo del paper: fissa una proprieta' strutturale del modulo, non un comportamento osservato a valle di un esperimento. E` quindi correttamente classificato come `Code Development`.

Rispetto al parent `The mask generator module is implemented, following Section 3.2`, questa foglia serve a bloccare una delle specifiche architetturali piu' importanti. L'ordinamento tra fratelli non sembra codificare una dipendenza forte; e` piu' naturale leggerlo come "prima architetture specifiche per backbone, poi vincolo dimensionale generale".

#### CD-3

```json
{
  "requirements": "The Single-channel version of SMM variant (aka. \"Single-Channel f_mask^s\") is implemented by implementing VR as f_in(x_i)=r(x_i)+delta odot f_mask(r(x_i)), i.e., a single-channel version of SMM is used, averaging the penultimate-layer output of the mask generator",
  "weight": 1,
  "task_category": "Code Development"
}
```

Questo requirement mostra come la rubric tratta le varianti di ablation: come oggetti implementativi a tutti gli effetti, non come semplici flag. E` `Code Development` perche' descrive la costruzione di una variante metodologica ben definita.

La foglia e` sorella di altri due variant leaf nello stesso parent, e le tre foglie insieme coprono le tre assenze/manipolazioni principali discusse nel paper. L'ordine e` coerente con una progressione logica dalle versioni piu' semplici o piu' "ablated" verso quella single-channel, ma non e` evidente una dipendenza esecutiva stretta.

### Foglie `Code Execution`

#### EX-1

```json
{
  "requirements": "When training a model using the SSM method, the resized input image (with the masked pattern added) is fed into the pretrained model",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia e` interessante perche' vive dentro il blocco di implementazione del metodo, non nel macro-blocco risultati. E` comunque `Code Execution`, non `Code Development`, perche' descrive un passo dinamico del training loop di Algorithm 1.

La relazione col parent `The learning strategy is implemented, following Algorithm 1` e` quella di una checklist ordinata di step. Qui l'ordine rispetto ai fratelli e` chiaramente dipendente: generazione maschere, interpolazione, composizione con il pattern, forward nel backbone, label mapping, loss, aggiornamento.

#### EX-2

```json
{
  "requirements": "Using the \"Pad\" reprogramming method, ResNet-18 (pre-trained on ImageNet-1K) has been fine-tuned on the train split of the CIFAR10 dataset, then the accuracy at the end of training on the test split is recorded. This is repeated three times with three unique seeds, and the mean and standard deviation of the test accuracy is computed",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questo e` il template piu' tipico del lato execution-heavy della rubric: una run completamente specificata per metodo, backbone, dataset, split, seeds e metrica aggregata. E` `Code Execution` perche' la verifica passa dall'esecuzione effettiva della pipeline sperimentale.

La foglia e` una cella atomica della matrice sperimentale sotto `Results on ResNets`. L'ordinamento coi fratelli e` coerente con una decomposizione gerarchica `backbone -> method -> dataset`: non sembra arbitrario, ma costruito per permettere di scendere da una tabella del paper a run individuali.

#### EX-3

```json
{
  "requirements": "tSNE is applied to the embeddings to project the embeddings to 2 dimensions",
  "weight": 1,
  "task_category": "Code Execution"
}
```

Questa foglia mostra un uso diverso di `Code Execution`: non training o evaluation standard, ma pipeline di analisi/visualizzazione. E` classificata correttamente come `Code Execution` perche' richiede un'operazione concreta da eseguire sui dati intermedi, non una proprieta' del codice o una conclusione interpretativa.

Dentro il parent `The experiments under the "Feature Space Visualization Results" subsection have been executed`, e` l'ultimo passo naturale dopo selezione dei campioni e computazione degli embedding. Anche qui l'ordine tra fratelli riflette una dipendenza pratica molto plausibile.

### Foglie `Result Analysis`

#### RA-1

```json
{
  "requirements": "The recorded metrics show that SMM yields higher accuracy compared to all other input reprogramming methods for ResNet-18 on almost all datasets",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa e` una foglia `Result Analysis` molto tipica: inizia con `The recorded metrics show that ...` e riassume un claim comparativo aggregato direttamente leggibile dalla tabella risultati. Non richiede una nuova run atomica; richiede di interpretare correttamente le metriche gia' ottenute.

La relazione col parent `The results under the "Results on ResNets" subsection have been replicated` e` chiara: i fratelli sono altri claim sintetici che trasformano la matrice di run in conclusioni verificabili. L'ordinamento dopo il blocco di esecuzione e` coerente col pattern globale `... -> Code Execution -> Result Analysis`.

#### RA-2

```json
{
  "requirements": "The recorded metrics show that SMM achieves roughly a 22% (absolute) improvement over the next best input reprogramming method for ViT on the Flowers102 dataset",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Qui il requirement passa da un claim aggregato a un claim puntuale e numerico. La formulazione e` comunque della stessa famiglia lessicale di RA-1: apertura osservativa, confronto, riferimento implicito a una tabella.

La foglia e` sorella di altri improvement-claim specifici su `Food101`, `SUN397`, `EuroSAT`, `UCF101`, quindi non e` un caso isolato ma un pattern. L'ordine tra i fratelli sembra seguire l'ordine con cui il paper discute i casi salienti della tabella, ma questa parte non e` rigidamente deducibile dal solo testo.

#### RA-3

```json
{
  "requirements": "The recorded metrics show that the \"Ours\" method has the best class separation in output feature space compared to other baseline methods, across both datasets",
  "weight": 1,
  "task_category": "Result Analysis"
}
```

Questa foglia e` preziosa perche' mostra che `Result Analysis` non e` limitato a tabelle di accuracy. Qui il claim riguarda una visualizzazione tSNE e una proprieta' qualitativa della separazione in feature space; la rubric la tratta comunque come risultato da verificare.

La relazione col parent `The results under the the "Feature Space Visualization Results" subsection have been replicated` e` diversa rispetto ai blocchi tabellari: qui i fratelli sono pochissimi e molto sintetici. L'ordinamento resta coerente con la dipendenza implicita: prima si eseguono embedding e proiezione, poi si controllano i claim interpretativi sulla separazione delle classi.

## E) Pattern chiave da replicare

- Questa rubric e` un esempio forte di root "ibrido": quattro blocchi di setup/metodo e un solo macro-blocco risultati. Non e` una decomposizione puramente per sezioni, ma non e` nemmeno puramente per contributi astratti; il generatore automatico deve saper usare entrambi i registri quando il paper ha una Section esperimentale molto pesante.
- Il mix dei tipi foglia e` fortemente sbilanciato verso `Code Execution` (67.4%), molto sopra la media ufficiale del 32.9%. Questo e` coerente con paper che espandono molte combinazioni backbone x metodo x dataset x seed in run atomiche.
- Il branching factor medio 6.08, molto sopra la media ufficiale 3.98, nasce soprattutto da inventari larghi e matrici sperimentali: elenco dataset, elenco baseline, elenco metodi per backbone, elenco dataset per metodo.
- I pesi di primo livello `[1, 2, 4, 10, 10]` formano una scala quasi monotona dai prerequisiti generici ai due blocchi centrali. Un generatore dovrebbe imitare questa logica locale piu' che i valori assoluti: disponibilita' < dipendenze condivise < baseline < metodo core ~= verifica empirica complessiva.
- Il sottoalbero `Impact of Masking` e` un ottimo prototipo del pattern di fase PaperBench: `Code Development -> Code Execution -> Result Analysis`, esattamente in linea con il pattern globale osservato nel 95.5% dei casi ufficiali che contengono tutti e tre i tipi.
- I requirement `Code Execution` in questa rubric sono spesso molto lunghi e template-based. Un generatore automatico deve saper produrre sequenze quasi seriali di foglie che cambiano solo metodo, backbone, dataset, seeds e dettagli di training, senza cercare varieta' stilistica artificiale.
- I requirement `Result Analysis` sono pochi e ad alta densita' informativa: quasi tutti iniziano con `The recorded metrics show that ...` e servono da checkpoint semantici che condensano un intero blocco di run.
- Un caveat importante da non imitare ciecamente: il naming nel JSON non e` perfettamente pulito (`SMM` nel paper, ma `SSM` e `SNS` nella rubric). La struttura dell'albero e` molto istruttiva; le stringhe specifiche mostrano invece che i generatori dovrebbero mantenere consistenza terminologica migliore di questa rubric quando possibile.
