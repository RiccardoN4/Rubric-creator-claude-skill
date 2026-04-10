# lbcs

Nota terminologica: nel JSON PaperBench il terzo tipo foglia canonico e` `Result Analysis`; nelle analisi aggregate era spesso abbreviato come RM / "Result Match". In questo file uso i nomi esatti del codice.

Nota sul testo della rubric: in vari requirement compaiono piccoli refusi (`SVHM` invece di `SVHN`, `succesfully`, ecc.). Qui mantengo le stringhe del JSON quando cito nodi, ma li segnalo come rumore redazionale e non come pattern da imitare.

## A) Header

`lbcs` ("Lexicographic Bilevel Coreset Selection") affronta il problema della refined coreset selection: trovare il coreset piu' piccolo possibile mantenendo prestazioni comparabili al training full-data. Il paper costruisce questa idea attorno a una formulazione bilevel con preferenze lessicografiche, un algoritmo black-box di outer-loop search e una lunga sezione sperimentale che confronta LBCS con numerose baseline sotto piu' protocolli.

Questa e` la rubric piu' grande tra gli esempi richiesti: 1471 nodi, 916 foglie, 555 nodi interni, profondita` massima 7, profondita` media delle foglie 6.44, branching factor medio 2.65, 7 figli al root. La distribuzione dei tipi foglia e` `Code Development` 485 (52.9%), `Code Execution` 410 (44.8%), `Result Analysis` 21 (2.3%).

Confrontata con la media `official-20` di [report.md](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/report.md), questa rubric ha:

- un numero di figli al root quasi identico alla media (7 contro 6.85);
- una profondita` foglia molto piu' alta (6.44 contro 4.47);
- un branching factor medio molto piu' basso (2.65 contro 3.98), perche' gran parte della crescita avviene come concatenazione di piccoli template ripetuti;
- una quota di `Result Analysis` eccezionalmente bassa (2.3% contro 14.0%), con gran parte dell'albero dedicata a costruire ed eseguire protocolli sperimentali.

`lbcs` e` stato scelto per mostrare come una rubric PaperBench scala quando un paper combina un metodo centrale con molte tabelle/protocolli sperimentali ripetuti. E` anche un caso interessante perche' il primo livello e` piu' section-oriented del benchmark medio, quindi costituisce una deviazione utile rispetto alle regole statistiche sintetizzate in [structural_principles.md](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/structural_principles.md).

Snippet del root:

```json
{
  "requirements": "The paper \"Refined Coreset Selection: Towards Minimal Coreset Size under Model Performance Constraints\" has been replicated",
  "sub_tasks": [
    {
      "requirements": "The relevant datasets necessary for the experiments in the paper have been setup such that they can be accessed and used",
      "weight": 1
    },
    {
      "requirements": "The results of Figure 1 have been reproduced",
      "weight": 1
    },
    {
      "requirements": "The relevant coreset selection methods have been implemented",
      "weight": 4
    },
    {
      "requirements": "The results of Section 5.1 have been reproduced",
      "weight": 1
    },
    {
      "requirements": "The results of Section 5.2 have been reproduced",
      "weight": 2
    },
    {
      "requirements": "The results of Section 5.3 have been reproduced",
      "weight": 2
    },
    {
      "requirements": "The results of Section 6 have been reproduced",
      "weight": 3
    }
  ]
}
```

I pesi del primo livello sono `[1, 1, 4, 1, 2, 2, 3]`: piu' che separare brutalmente un singolo blocco dominante, costruiscono una gerarchia locale in cui implementazione dei metodi e analisi aggiuntive pesano piu' dei prerequisiti e del toy setup preliminare.

## B) Primi 3 Livelli Completi e Annotati

Questa sezione riporta `root -> figli -> nipoti` completi. Per ciascun figlio del root spiego cosa rappresenta e perche' e` tenuto a quel livello.

### [1] `The relevant datasets necessary for the experiments in the paper have been setup such that they can be accessed and used` (peso 1)

Questo nodo raccoglie i prerequisiti dati. E` coerente tenerlo al root perche' tutti i protocolli sperimentali del paper dipendono da questo setup, ma il peso 1 segnala che la rubric lo considera solo come fondazione.

Strutturalmente e` un piccolo inventario di benchmark, ordinato per dataset piuttosto che per sezione:

- `[1.1]` `F-MNIST has been setup such that it can be accessed and used`
- `[1.2]` `SVHN has been setup such that it can be accessed and used`
- `[1.3]` `CIFAR-10 has been setup such that it can be accessed and used`
- `[1.4]` `MNIST-S has been setup such that it can be accessed and used`

La scelta di assegnare pesi diversi ai nipoti (`6, 4, 3, 1`) non e` spiegata esplicitamente dal paper. Una lettura prudente e` che il dataset piu' ricorrente nelle tabelle principali, `F-MNIST`, riceva maggior enfasi, mentre `MNIST-S` resta confinato al caso preliminare di Section 5.1.

### [2] `The results of Figure 1 have been reproduced` (peso 1)

Questo blocco e` dedicato alla dimostrazione preliminare che le soluzioni banali non bastano. Tenerlo al root e` coerente con la struttura argomentativa del paper: Figure 1 sta tra la formulazione del problema e il metodo, e serve da giustificazione concettuale del bisogno di LBCS.

I nipoti separano chiaramente esecuzione e verifica:

- `[2.1]` `Equations (3) and (4) have been individually optimized in a bilevel coreset selection loop ...`
- `[2.2]` `The results of Figure 1 have been reproduced`

Questa micro-struttura `setup/experiment -> result claims` anticipa un motivo che ricompare nel resto della rubric.

### [3] `The relevant coreset selection methods have been implemented` (peso 4)

Questo e` il blocco implementativo principale del paper. A differenza di molti altri benchmark, `lbcs` non ha un singolo nodo top-level per "the method" e un altro per "the baselines" dentro un grande blocco risultati; qui l'implementazione dei metodi e` esplicitamente elevata al root.

I nipoti sono:

- `[3.1]` `LBCS has been implemented as outlined in Algorithm 1 and Algorithm 2, with Algorithm 2 called at step 4 of algorithm 1`
- `[3.2]` `The baseline methods have been implemented`
- `[3.3]` `LBCS+Moderate coreset selection has been implemented ...`

Questa scelta e` coerente con il paper, che ha una forte componente algoritmica e confronta molte baseline. Il peso 4, il piu' alto del root dopo il 3 di Section 6, riflette che la rubric considera la disponibilita' dei metodi come un blocco portante.

### [4] `The results of Section 5.1 have been reproduced` (peso 1)

Questo figlio raccoglie il primo esperimento dimostrativo su `MNIST-S`, usato per mostrare che LBCS abbassa insieme `f_1(m)` e `f_2(m)` e come il compromesso `epsilon` influenzi la dimensione del coreset. E` giusto al root perche' Section 5.1 e` una mini-sezione sperimentale autosufficiente e concettualmente distinta dal benchmark comparison di Section 5.2.

I nipoti sono:

- `[4.1]` `LBCS has been run for finding the optimal refined coreset for training a CNN on MNIST-S at different initial predefined coreset sizes k and different performance compromises epsilon`
- `[4.2]` `The results of Section 5.1 have been reproduced`

La decomposizione e` minima e lineare: prima si esegue il protocollo, poi si verificano i claim sul comportamento di `f_1` e `f_2`.

### [5] `The results of Section 5.2 have been reproduced` (peso 2)

Questo e` il cuore dimensionale della rubric: 680 nodi totali e 412 foglie, piu' di qualsiasi altro figlio del root. E` la sezione in cui il paper confronta LBCS con sette baseline su `F-MNIST`, `SVHN` e `CIFAR-10`, prima alle stesse dimensioni iniziali del coreset, poi alle dimensioni trovate da LBCS.

I nipoti sono:

- `[5.1]` `Code that is agnostic to the predefined coreset size and benchmark has been implemented`
- `[5.2]` `The results shown in Table 2 and Figure 3 have been reproduced`
- `[5.3]` `The results shown in Table 3 have been reproduced`

Questa organizzazione e` molto informativa: un piccolo blocco di setup trasversale, poi due giganteschi blocchi gemelli che differiscono solo nella metrica di confronto. E` una struttura piu' section/table-oriented della media del benchmark, ma coerente con un paper che vive di benchmark matrices.

### [6] `The results of Section 5.3 have been reproduced` (peso 2)

Questo blocco raccoglie la robustezza sotto imperfect supervision. E` tenuto al root perche' la sezione sperimentale e` autonoma e cambia esplicitamente il regime dati: rumore di label e class imbalance.

I nipoti sono:

- `[6.1]` `The results shown in Figure 2a and Figure 4 have been reproduced`
- `[6.2]` `The results shown in Figure 2b have been reproduced`

La separazione segue fedelmente il paper: da una parte label noise (`30%` e `50%`), dall'altra class imbalance. Rispetto al benchmark medio, questa e` ancora una volta una scelta molto section/figure-driven.

### [7] `The results of Section 6 have been reproduced` (peso 3)

Questo nodo raccoglie le analisi complementari: ablation sul numero di search steps, inizializzazione con `Moderate`, confronto cross-architecture su `SVHN`. Il fatto che questo blocco abbia peso 3, maggiore dei blocchi Section 5.2 e 5.3 presi singolarmente, e` una scelta non ovvia; la lettura piu' prudente e` che la rubric lo interpreti come macro-verifica della robustezza e trasferibilita' del metodo.

I nipoti sono:

- `[7.1]` `The results of Table 9 have been reproduced`
- `[7.2]` `The results of Table 5 have been reproduced`
- `[7.3]` `The results of Table 6 have been reproduced`

Qui l'organizzazione e` praticamente un indice delle tabelle di Section 6. E` una deviazione utile rispetto alla regola generale "non decomporre il root per sezioni": in questo paper la sezione analitica finale e` abbastanza autonoma da diventare un blocco top-level.

## C) Sottoalbero Scelto: Espansione Completa Fino Alle Foglie

Ho scelto di espandere il sottoalbero:

`[5.2].[1].[2] LBCS has been evaluated on the F-MNIST, SVHM and CIFAR-10 benchmarks at various predefined coreset sizes`

Motivo della scelta:

- appartiene al blocco piu' grande dell'intera rubric (`Section 5.2`);
- ha una struttura abbastanza ricca da mostrare come il paper scala per ripetizione;
- e` piu' leggibile di espandere tutto `[5.2]`, che conterrebbe 201 foglie;
- i suoi fratelli sono quasi copie strutturali per `Uniform`, `EL2N`, `Influential`, `Moderate`, `CCS`, `Probabilistic`, `GraNd`, quindi capendo questo sottoalbero si capisce il meccanismo di crescita della rubric.

Statistiche del sottoalbero scelto: 43 nodi totali, 27 foglie, di cui 15 `Code Development` e 12 `Code Execution`. Non contiene `Result Analysis`: in questa parte della rubric i claim di risultato sono spostati nel nodo fratello `[5.2].[2]`, che riassume la matrice di misure.

Snippet del top del sottoalbero:

```json
{
  "requirements": "LBCS has been evaluated on the F-MNIST, SVHM and CIFAR-10 benchmarks at various predefined coreset sizes",
  "weight": 1,
  "sub_tasks": [
    {
      "requirements": "Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the final coreset size at the end of LBCS can be measured",
      "task_category": "Code Development"
    },
    {
      "requirements": "Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the outer loop can run for 500 iterations (i.e. T=500)",
      "task_category": "Code Development"
    },
    {
      "requirements": "Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the voluntary performance compromise can be set to epsilon=0.2",
      "task_category": "Code Development"
    }
  ]
}
```

Espansione completa:

```text
- [5.2].[1].[2] w=1 :: LBCS has been evaluated on the F-MNIST, SVHM and CIFAR-10 benchmarks at various predefined coreset sizes
  - w=1 [Code Development] :: Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the final coreset size at the end of LBCS can be measured
  - w=1 [Code Development] :: Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the outer loop can run for 500 iterations (i.e. T=500)
  - w=1 [Code Development] :: Code has been implemented such that to evaluate LBCS on the F-MNIST, SVHM and CIFAR-10 benchmarks at a given predefined coreset size, the voluntary performance compromise can be set to epsilon=0.2
  - w=1 :: LBCS has been evaluated on the F-MNIST benchmark at various predefined coreset sizes
    - w=1 :: LBCS has been evaluated on the F-MNIST benchmark with a predefined coreset size of k=1000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the F-MNIST benchmark with a predefined coreset size of k=1000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=1000 for constructing the optimal coreset for training a LeNet on F-MNIST. A LeNet was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the LeNet trained on the constructed coreset on the F-MNIST test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the F-MNIST benchmark with a predefined coreset size of k=2000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the F-MNIST benchmark with a predefined coreset size of k=2000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=2000 for constructing the optimal coreset for training a LeNet on F-MNIST. A LeNet was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the LeNet trained on the constructed coreset on the F-MNIST test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the F-MNIST benchmark with a predefined coreset size of k=3000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the F-MNIST benchmark with a predefined coreset size of k=3000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=3000 for constructing the optimal coreset for training a LeNet on F-MNIST. A LeNet was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the LeNet trained on the constructed coreset on the F-MNIST test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the F-MNIST benchmark with a predefined coreset size of k=4000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the F-MNIST benchmark with a predefined coreset size of k=4000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=4000 for constructing the optimal coreset for training a LeNet on F-MNIST. A LeNet was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the LeNet trained on the constructed coreset on the F-MNIST test set and the constructed coreset size have been recorded.
  - w=1 :: LBCS has been evaluated on the SVHM benchmark at various predefined coreset sizes
    - w=1 :: LBCS has been evaluated on the SVHM benchmark with a predefined coreset size of k=1000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the SVHM benchmark with a predefined coreset size of k=1000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=1000 for constructing the optimal coreset for training a CNN (Table 7, center column) on SVHM. The CNN from Table 7, left column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the CNN (Table 7, center column) trained on the constructed coreset on the SVHM test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the SVHM benchmark with a predefined coreset size of k=2000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the SVHM benchmark with a predefined coreset size of k=2000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=2000 for constructing the optimal coreset for training a CNN (Table 7, center column) on SVHM. The CNN from Table 7, left column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the CNN (Table 7, center column) trained on the constructed coreset on the SVHM test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the SVHM benchmark with a predefined coreset size of k=3000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the SVHM benchmark with a predefined coreset size of k=3000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=3000 for constructing the optimal coreset for training a CNN (Table 7, center column) on SVHM. The CNN from Table 7, left column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the CNN (Table 7, center column) trained on the constructed coreset on the SVHM test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the SVHM benchmark with a predefined coreset size of k=4000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the SVHM benchmark with a predefined coreset size of k=4000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=4000 for constructing the optimal coreset for training a CNN (Table 7, center column) on SVHM. The CNN from Table 7, left column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the CNN (Table 7, center column) trained on the constructed coreset on the SVHM test set and the constructed coreset size have been recorded.
  - w=1 :: LBCS has been evaluated on the CIFAR-10 benchmark at various predefined coreset sizes
    - w=1 :: LBCS has been evaluated on the CIFAR-10 benchmark with a predefined coreset size of k=1000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the CIFAR-10 benchmark with a predefined coreset size of k=1000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=1000 for constructing the optimal coreset for training a ResNet18 on CIFAR-10. The CNN from Table 7, right column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the ResNet-18 trained on the constructed coreset on the CIFAR-10 test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the CIFAR-10 benchmark with a predefined coreset size of k=2000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the CIFAR-10 benchmark with a predefined coreset size of k=2000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=2000 for constructing the optimal coreset for training a ResNet18 on CIFAR-10. The CNN from Table 7, right column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the ResNet-18 trained on the constructed coreset on the CIFAR-10 test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the CIFAR-10 benchmark with a predefined coreset size of k=3000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the CIFAR-10 benchmark with a predefined coreset size of k=3000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=3000 for constructing the optimal coreset for training a ResNet18 on CIFAR-10. The CNN from Table 7, right column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the ResNet-18 trained on the constructed coreset on the CIFAR-10 test set and the constructed coreset size have been recorded.
    - w=1 :: LBCS has been evaluated on the CIFAR-10 benchmark with a predefined coreset size of k=4000
      - w=1 [Code Development] :: Code has been implemented such that LBCS can be evaluated for coreset selection on the CIFAR-10 benchmark with a predefined coreset size of k=4000
      - w=1 [Code Execution] :: LBCS has been evaluated with a predefined coreset size of k=4000 for constructing the optimal coreset for training a ResNet18 on CIFAR-10. The CNN from Table 7, right column was used as the proxy model during coreset selection. The test accuracy and test accuracy per coreset data point of the ResNet-18 trained on the constructed coreset on the CIFAR-10 test set and the constructed coreset size have been recorded.
```

## D) Cosa Insegna Questo Sottoalbero

Questo sottoalbero mostra molto bene il meccanismo con cui `lbcs` raggiunge 1471 nodi senza avere un branching medio alto. La crescita non avviene tramite enormi fan-out locali; avviene tramite replicazione sistematica di un template piccolo:

`global LBCS settings -> benchmark -> predefined k -> {implementability leaf, execution leaf}`

Le tre foglie iniziali di `Code Development` fissano i parametri condivisi a tutti gli esperimenti del sottoalbero: misurazione della dimensione finale del coreset, `T=500`, `epsilon=0.2`. Poi arrivano tre blocchi benchmark (`F-MNIST`, `SVHM`, `CIFAR-10`), e ciascuno replica quattro valori di `k`. Infine, ogni valore di `k` si chiude con la stessa coppia di foglie:

- una foglia `Code Development` che assicura che quel caso sperimentale sia implementabile;
- una foglia `Code Execution` che registra l'effettiva esecuzione e le misure raccolte.

Questa e` una lezione strutturale importante: la rubric non collassa tutti i casi sperimentali in un'unica foglia "run Table 2". Li rende atomici fino a livello `benchmark x k`, ma usa un template minimo per non far esplodere troppo il branching locale. La scarsita' di `Result Analysis` in `lbcs` nasce proprio da qui: i claim comparativi vengono compressi in pochi nodi fratelli, dopo una grande matrice di implementazioni ed esecuzioni.

## E) Pattern Chiave da Replicare

- `lbcs` e` un caso di decomposition ibrida ma piu' section-oriented del benchmark medio. Un generatore automatico dovrebbe accettare questa deviazione quando il paper ha molti blocchi sperimentali autonomi e tabelle molto distinte.
- Il root separa bene quattro famiglie: prerequisiti dati, giustificazione preliminare (Figure 1), implementazione dei metodi, e poi tre grandi blocchi empirici (`Section 5.2`, `Section 5.3`, `Section 6`).
- La crescita della rubric avviene per replicazione di template piccoli. Nel sottoalbero scelto, lo stesso motivo `benchmark -> k -> {CD, EX}` si ripete 12 volte; lo stesso motivo e` poi replicato anche per sette baseline sorelle.
- I pesi non sono usati per creare salti estremi: anche in una rubric enorme, i valori restano piccoli e locali. La dimensione effettiva dell'importanza viene soprattutto dalla posizione del nodo e dal numero di blocchi che eredita.
- `Result Analysis` e` rarissimo in questa rubric (solo 2.3% delle foglie). Quando compare, e` quasi sempre spostato in piccoli nodi di sintesi che riassumono intere matrici di run. Questa e` una deviazione forte dalla media globale e va imitata solo per paper fortemente benchmark-driven.
- Il branching factor medio basso (2.65) non significa albero semplice; significa che la complessita' e` distribuita in profondita'. Questo e` un pattern molto utile per generatori automatici: per paper grandi, spesso conviene scalare con piu' livelli e template ripetuti, non con nodi singoli da 20-30 figli.
- La rubric contiene vari refusi (`SVHM`, `succesfully`, ecc.). La struttura e` istruttiva, ma queste imperfezioni lessicali non vanno trattate come invarianti stilistici da imitare.
