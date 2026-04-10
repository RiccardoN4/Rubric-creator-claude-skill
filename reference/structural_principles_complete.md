# Structural Principles for PaperBench Rubric Generation (Complete)

Questo documento sostituisce la versione precedente di `structural_principles.md` e integra, in un unico riferimento operativo, le regole prescrittive originali, tutte le statistiche quantitative rilevanti del report, i vincoli di compatibilita` ricavati dal codice PaperBench e i pattern qualitativi emersi dagli esempi annotati.

Correzione di nomenclatura. In `report.md` e in alcuni CSV compaiono talvolta le etichette abbreviate o non canoniche `Execution` e `Result Match`. In questo documento tali etichette sono state normalizzate in modo sistematico ai valori canonici del codice PaperBench definiti in [`paperbench/rubric/tasks.py`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/paperbench/rubric/tasks.py): `Code Development`, `Code Execution`, `Result Analysis`. Quando viene discusso lo schema, viene anche menzionato il valore speciale `Subtree`, che il codice considera valido ma usa dinamicamente nel judge; non e` una categoria da generare nelle rubriche JSON del dataset.

Base empirica. Le regole prescrittive sono calibrate soprattutto sui 20 paper ufficiali dello split `official-20`, perche' sono quelli che definiscono il benchmark PaperBench. Le statistiche `all-23` sono usate come controllo di robustezza e per le sezioni cross-rubric. Le fonti utilizzate sono:

- [`structural_principles.md`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/structural_principles.md)
- [`report.md`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/report.md)
- tutte le tabelle CSV in [`tables/`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/tables)
- [`rubric_schema_reference.md`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/rubric_schema_reference.md)
- tutti i file in [`annotated_examples/`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/analysis/rubric_structure_analysis/annotated_examples)

## Prescriptive Rules With Full Quantitative Support

### Tree Skeleton

1. Usa sempre un nodo radice unico con `id: root`, `weight: 1`, requirement riassuntivo dell'intera riproduzione e senza `task_category`.

   Supporto quantitativo e di compatibilita`. In tutte le rubriche osservate il nodo radice ha `weight: 1`; nel codice di PaperBench la normalizzazione dei pesi e` sempre locale, quindi fissare il root a `1` evita una scala inutile. Lo schema applicato da `TaskNode.__post_init__` impone inoltre che ogni nodo interno abbia `task_category=None`, quindi il root non puo` essere tipizzato. La serializzazione attesa del root richiede sempre `sub_tasks`, anche se per il root questo significa semplicemente una lista non vuota di figli.

2. Fai si' che il nodo radice abbia tipicamente tra 2 e 13 figli; il range interquartile osservato e` 5-8.

   Supporto quantitativo. Nei 20 paper ufficiali `root_children` ha media `6.85`, mediana `6.50`, deviazione standard `2.62`, IQR `5.00-8.00`, minimo `2` in `ftrl` e massimo `13` in `lca-on-the-line`. Sui 23 paper la distribuzione e` quasi identica: media `6.78`, mediana `6.00`, IQR `5.5-8.0`. La distribuzione discreta per-paper sul benchmark ufficiale e` `2:1`, `4:2`, `5:3`, `6:4`, `7:3`, `8:3`, `9:2`, `12:1`, `13:1`. In altre parole, il regime dominante non e` un root con decine di figli ma un root con pochi macro-blocchi.

3. Costruisci alberi con profondita` massima tipica tra 4 e 9; la profondita` foglia media per-paper osservata e` 4.47.

   Supporto quantitativo. Nei 20 paper ufficiali `max_depth` ha media `5.80`, mediana `5.00`, deviazione standard `1.32`, IQR `5.00-7.00`, minimo `4` in `bridging-data-gaps` e massimo `9` in `bam`. La metrica per-paper `avg_leaf_depth` ha media `4.466`, mediana `4.155`, deviazione standard `1.200`, IQR `3.686-4.889`, minimo `2.625` in `mechanistic-understanding` e massimo `6.962` in `pinn`. La profondita` massima, quindi, cresce soprattutto nei paper che scalano per ripetizione di template, non in quelli che allargano solo il primo livello.

4. Mantieni la maggior parte delle foglie a profondita` intermedia: il benchmark non premia foglie tutte schiacciate al livello 2-3, ma nemmeno alberi in cui quasi tutto scende sotto livello 8.

   Supporto quantitativo. Se si guarda alla distribuzione globale delle 8,316 foglie ufficiali, la profondita` delle foglie ha media `5.335`, mediana `5`, deviazione standard `1.708`, IQR `4-7`, percentile 10 `3` e percentile 90 `7`, con range `1-9`. L'istogramma completo e` `depth 1: 3`, `2: 212`, `3: 1150`, `4: 1809`, `5: 1396`, `6: 751`, `7: 2231`, `8: 724`, `9: 40`. Questo significa che la fascia dominante e` `4-7`, con un picco sorprendentemente forte a profondita` `7` dovuto a rubriche grandi come `lbcs`, `bam` e `pinn`.

5. Usa nodi interni con branching factor contenuto: nelle rubriche ufficiali la mediana del numero di figli per nodo interno e` 3.0.

   Supporto quantitativo. Sul benchmark ufficiale, la distribuzione globale del numero di figli dei 2,902 nodi interni ha media `3.859`, mediana `3`, deviazione standard `2.521`, IQR `2-5`, minimo `2` e massimo `30`. L'istogramma e` fortemente concentrato su valori piccoli: `2 figli` nel `38.7%` dei nodi interni, `3` nel `17.8%`, `4` nel `15.6%`, `5` nel `7.5%`, `6` nel `10.6%`; oltre `10` figli si entra in una coda rara. A livello per-paper, `avg_branching_factor` ha media `3.983`, mediana `3.848`, deviazione standard `0.912`, IQR `3.422-4.352`, minimo `2.649` in `lbcs` e massimo `6.077` in `sample-specific-masks`. La combinazione `lbcs` vs `sample-specific-masks` mostra i due modi canonici di scalare: profondita` alta e branching basso, oppure matrici larghe ma relativamente piatte.

### First Level Decomposition

6. Decomponi il nodo radice per contributi principali o blocchi sperimentali, non per sezioni del paper: i figli del primo livello sono classificati come blocchi method/result o ibridi nel 71.5% dei casi ufficiali.

   Supporto quantitativo. Sui 137 figli di primo livello del benchmark ufficiale, `Experiment/result block` vale `36.5%`, `Method/contribution block` `27.0%`, `Hybrid contribution/result block` `8.0%`, per un totale del `71.5%` di blocchi non puramente sezionali. I blocchi `Experiment/result` sono anche quelli piu` capienti: media `96.26` foglie discendenti, mediana `24`, IQR `10-56.75`, massimo `1866`. I blocchi `Method/contribution` hanno invece media `15.24` foglie discendenti, mediana `11`, IQR `6-26`, massimo `46`. La norma strutturale, quindi, e` che il root distingua tra grandi famiglie di implementazione e grandi famiglie di verifica, non che ricopi l'indice del paper.

7. Evita una decomposizione esplicitamente sezionale al primo livello: i blocchi puramente section-oriented sono minoritari.

   Supporto quantitativo. Nel benchmark ufficiale `Section-oriented block` pesa `24.1%` dei figli di primo livello, contro il `75.9%` di classi alternative. Anche quando compare, il suo peso locale e` tipicamente moderato: media `0.115`, mediana `0.111`, IQR `0.077-0.154`, range `0.056-0.222`. Gli esempi annotati mostrano bene quando questa eccezione e` accettabile: `robust-clip` e `lbcs` hanno sezioni sperimentali molto autonome, quindi una lettura piu` section-oriented resta coerente col contenuto del paper. In assenza di quella struttura, il benchmark preferisce organizzazioni semantiche piu` astratte.

8. Assegna a ciascun figlio di primo livello un sottoproblema semanticamente coeso, di solito un metodo, una famiglia di task/dataset o un blocco di risultati completi.

   Supporto quantitativo. I blocchi `Method/contribution` al primo livello hanno media `15.24` foglie discendenti ma massimo solo `46`, quindi catturano sottoproblemi relativamente compatti; i blocchi `Experiment/result` hanno media `96.26` foglie discendenti e arrivano a `1866`, cioe` intere famiglie di benchmark; i blocchi `Hybrid contribution/result` stanno nel mezzo con media `54.55` e mediana `23`. Gli esempi annotati mostrano tre forme canoniche di coesione: `stochastic-interpolants` separa prerequisiti, modelli, metrica FID e risultati; `all-in-one` separa metodo, baseline, task preparation e macro-blocco risultati; `sample-specific-masks` usa un root ibrido con blocchi infrastrutturali leggeri e un blocco risultati molto pesante.

### Leaf Typing and Ordering

9. Etichetta tutte le foglie con uno dei tre tipi canonici `Code Development`, `Code Execution`, `Result Analysis`; nessun nodo interno deve avere `task_category`.

   Supporto quantitativo e di compatibilita`. Questo vincolo non e` solo stilistico: `TaskNode.__post_init__` lancia un errore se un nodo interno ha `task_category` e se una foglia non lo ha. I tre valori canonici da usare nelle rubriche input sono `Code Development`, `Code Execution`, `Result Analysis`. Il codice contiene anche `Subtree` in `VALID_TASK_CATEGORIES`, ma `rubric_schema_reference.md` mostra che viene usato dal judge per creare foglie sintetiche durante il grading di sottoalberi; non e` una categoria da emettere in una rubric JSON del dataset.

10. Mantieni `Code Development` come tipo dominante: la quota media sulle rubriche ufficiali e` 53.1% delle foglie.

   Supporto quantitativo. Nei 20 paper ufficiali `Code Development` ha media `53.1%`, mediana `52.8%`, deviazione standard `21.0` punti percentuali, IQR `37.5%-68.0%`, minimo `6.4%` in `pinn` e massimo `94.7%` in `what-will-my-model-forget`. Per topic, il valore medio piu` alto si osserva in `Continual learning / efficient fine-tuning` con `64.1%`, seguito da `Diffusion / generative modeling` con `57.1%`; il valore piu` basso e` l'outlier `Scientific ML / physics-informed learning` con `6.4%`, interamente trainato da `pinn`.

11. Inserisci `Code Execution` quando la riproduzione richiede run verificabili: la quota media ufficiale e` 32.9%.

   Supporto quantitativo. Nei 20 paper ufficiali `Code Execution` ha media `32.9%`, mediana `29.0%`, deviazione standard `23.6` punti percentuali, IQR `11.0%-45.3%`, minimo `3.0%` in `what-will-my-model-forget` e massimo `92.5%` in `pinn`. Per topic, il valore piu` alto e` `Scientific ML / physics-informed learning` con `92.5%`; tra i topic con piu` di un paper spiccano `Data selection / optimization` con `44.8%`, `Simulation-based inference` con `35.6%` e `Vision / OOD / robustness` con `35.5%`. Gli esempi `sample-specific-masks` (`67.4%`) e `lbcs` (`44.8%`) mostrano due versioni diverse dello stesso pattern: molti benchmark implicano molte foglie `Code Execution`, ma possono farlo con albero largo o profondo.

12. Inserisci `Result Analysis` per ancorare i claim sperimentali: la quota media ufficiale e` 14.0%.

   Supporto quantitativo. Nei 20 paper ufficiali `Result Analysis` ha media `14.0%`, mediana `12.4%`, deviazione standard `11.7` punti percentuali, IQR `3.3%-21.8%`, minimo `1.1%` in `pinn` e massimo `41.3%` in `bridging-data-gaps`. Per topic, il picco medio e` `Diffusion / generative modeling` con `23.5%`, seguito da `Vision / OOD / robustness` con `15.9%` e `LLMs / prompting / adaptation` con `14.2%`. L'esempio `robust-clip` chiarisce il caso in cui la quota cresce: non perche' aumentino le metriche da calcolare, ma perche' la rubric esplicita numerosi trend comparativi e claim interpretativi.

13. Rispetta un ordinamento di fase non decrescente quando un sottoalbero contiene piu` tipi: nei nodi interni ufficiali la sequenza di blocchi e` monotona nel 83.8% dei casi.

   Supporto quantitativo. Nel benchmark ufficiale `phase_monotonic_share = 83.77%` e `single_block_per_type_share = 83.80%` su `2902` nodi interni; sui 23 paper si sale leggermente a `84.47%` e `84.54%`. L'ordine di prima occorrenza piu` comune e` `Code Development > Code Execution` (`36.6%`), seguito da alberi con un solo blocco `Code Execution` (`25.5%`) o un solo blocco `Code Development` (`24.6%`). La matrice di transizione mostra che, quando si passa da un blocco `Code Development`, nel `99.22%` dei casi il blocco successivo e` `Code Execution`, non `Result Analysis`. Il dato supporta una regola forte: implementazione prima, run dopo.

14. Quando compaiono tutti e tre i tipi nello stesso sottoalbero, usa preferibilmente l'ordine `Code Development -> Code Execution -> Result Analysis`; condizionato ai sottoalberi che contengono tutti e tre i tipi, questo ordine appare nel 95.5% dei casi ufficiali.

   Supporto quantitativo. Nei nodi interni ufficiali, i sottoalberi che contengono tutti e tre i tipi sono solo il `4.62%`, ma tra questi l'ordine esatto `Code Development -> Code Execution -> Result Analysis` compare nel `95.52%` dei casi. Al livello dei figli del root il pattern resta fortissimo: `contains_all_three_share = 44.87%` e `exact_cd_ex_rm_given_all_three_share = 92.86%`. Gli esempi annotati `all-in-one` e soprattutto `sample-specific-masks` mostrano il caso canonico: un blocco di metodo genera foglie `Code Development`, un blocco di run produce `Code Execution`, e solo dopo arrivano poche foglie `Result Analysis` ad alta densita` semantica.

### Weights

15. Interpreta i pesi come locali tra fratelli, non come pesi globali assoluti: la score aggregation nel codice e` una media pesata tra figli.

   Supporto quantitativo e di compatibilita`. La formula implementata nel codebase e`:

   ```text
   total_weight = sum(child.weight for child in node.sub_tasks)
   if total_weight == 0:
       score(node) = 0.0
   else:
       score(node) = sum(score(child) * child.weight for child in node.sub_tasks) / total_weight
   ```

   Di conseguenza il peso realmente importante di una foglia e` il prodotto delle quote locali lungo il cammino root->leaf, non il suo `weight` grezzo isolato. Questo spiega perche' pesi grezzi quasi sempre pari a `1` possano comunque produrre differenze sostanziali nel peso effettivo.

16. Usa pesi grezzi piccoli e interi; nella pratica i pesi sono quasi sempre valori bassi riutilizzabili tra fratelli.

   Supporto quantitativo. Nel benchmark ufficiale, al livello `depth 1` il peso grezzo ha media `2.693`, mediana `1`, deviazione standard `3.470`, IQR `1-3`, range `1-20`, con frequenze `1` in `72` nodi, `2` in `29`, `4` in `12`, `3` in `10`, `10` in `9`, `20` in `3`. Gia` a `depth 2` la distribuzione collassa: media `1.380`, mediana `1`, IQR `1-1`, massimo `8`. Tra `depth 3` e `depth 6` quasi tutto e` `1` o `2`; a `depth 8` e `depth 9` il peso grezzo e` sempre `1`. La regola operativa corretta, quindi, non e` inventare scale numeriche elaborate ma usare pochi interi piccoli e lasciare che sia la struttura a fare il lavoro.

17. Al primo livello distribuisci i pesi in modo non perfettamente uniforme, ma senza estremi: la varianza serve a separare contributi principali, non a creare code molto lunghe.

   Supporto quantitativo. Sempre sul benchmark ufficiale, a `depth 1` la quota locale media e` `0.146`, mediana `0.118`, IQR `0.077-0.167`, minimo `0.011`, massimo `0.667`. Questo indica che il root discrimina tra blocchi importanti e blocchi di supporto, ma in modo moderato. Per classe strutturale, i blocchi `Experiment/result` hanno `mean_local_share = 0.164`, `median = 0.143`, IQR `0.068-0.202`; i blocchi `Method/contribution` hanno `mean = 0.155`, `median = 0.115`, IQR `0.080-0.220`; i blocchi `Section-oriented` hanno valori piu` compressi, `mean = 0.115`, `median = 0.111`, IQR `0.077-0.154`. Gli esempi annotati chiariscono la logica: in `sample-specific-masks` la scala `[1,2,4,10,10]` separa prerequisiti, dipendenze condivise, baseline e blocchi centrali; in `stochastic-interpolants` il nodo FID condiviso e` promosso al primo livello ma resta a peso basso.

18. Se devi dare piu` impatto a un tipo di foglia, fallo soprattutto via posizione nell'albero e local share del parent: il peso effettivo medio osservato e` maggiore per `Result Analysis`.

   Supporto quantitativo. Sul benchmark ufficiale, il peso effettivo medio delle foglie `Result Analysis` e` `0.0121923`, contro `0.0027292` per `Code Development` e `0.0007551` per `Code Execution`; le mediane sono rispettivamente `0.0074074`, `0.0004960` e `0.0000687`. Anche allargando ai 23 paper il pattern resta stabile: `Result Analysis = 0.011941`, `Code Development = 0.003079`, `Code Execution = 0.000783`. Il dato non va interpretato come "assegna sempre pesi grezzi piu` alti a `Result Analysis`": i pesi grezzi medi sono solo `1.322` per `Result Analysis`, `1.045` per `Code Development`, `1.143` per `Code Execution`. La differenza nasce perche' `Result Analysis` e` tipicamente collocato in rami piu` pesanti e con meno sibling concorrenti. Quindi, se vuoi enfatizzare il recupero dei claim, devi farlo architetturalmente.

### Requirement Style

19. Per i nodi interni usa requirement relativamente brevi e astratti; la lunghezza media osservata e` 22.2 parole.

   Supporto quantitativo. Sui `2902` nodi interni ufficiali, la lunghezza dei requirement ha media `22.23` parole, mediana `21`, deviazione standard `10.88`, IQR `14-30`, minimo `2`, massimo `67`; in caratteri la media e` `141.58`, mediana `136`, IQR `89-187`. I pattern di apertura piu` frequenti sono `code has`, `the results`, `for the`, `the correct`. Questo conferma che i nodi interni non sono micro-task atomici ma etichette sintetiche di sottoproblemi: metodo, blocco di esperimenti, famiglia di risultati, componente condivisa.

20. Per le foglie `Code Development`, usa formulazioni operative che iniziano spesso con `The ...` o `Code for ...` e che includono la formula `has been implemented` quando stai descrivendo capacita` o componenti da costruire.

   Supporto quantitativo. Su `3671` foglie `Code Development` ufficiali, il requirement ha media `27.79` parole, mediana `26`, deviazione standard `12.39`, IQR `19-35`, minimo `3`, massimo `106`; in caratteri la media e` `181.76`, IQR `126-222`. Il `36.6%` contiene la stringa `has been implemented`; il `14.6%` inizia con `The`; solo lo `0.8%` inizia con `Code for`. Le aperture 2-gram piu` frequenti sono `code has (2041)`, `for the (190)`, `code to (131)`, `for each (129)`, `is randomly (89)`; le aperture 3-gram piu` frequenti sono `code has been (2041)`, `is randomly split (89)`, `for each pair (88)`, `code to compute (83)`. Gli esempi annotati confermano il registro: `stochastic-interpolants` e `all-in-one` usano spesso formulazioni procedurali; `robust-clip` aggiunge uno stile configurativo come `is set up to`.

21. Per le foglie `Code Execution`, usa formulazioni verificabili e run-oriented, spesso con aperture tipo `When ...` o `The ... has been run/trained/evaluated`.

   Supporto quantitativo. Su `4079` foglie `Code Execution` ufficiali, il requirement ha media `42.87` parole, mediana `41`, deviazione standard `21.83`, IQR `28-55`, minimo `5`, massimo `106`; in caratteri la media e` `257.57`, IQR `175-326`. E` il tipo di foglia piu` lungo del benchmark. Il `7.0%` inizia con `When`, il `16.3%` con `The`; quasi nessuna contiene `has been implemented`, il che la distingue lessicalmente da `Code Development`. Le aperture piu` frequenti sono `code has (1864)`, `when using (305)`, `using the (242)`, `for the (159)`, `10 seeded (78)`. Il tratto rilevante emerso dagli esempi annotati e` che `Code Execution` non significa solo training: in `robust-clip` significa anche produrre score e tabelle; in `lbcs` e `sample-specific-masks` significa enumerare combinazioni sistematiche di metodo, dataset, backbone, seeds e protocollo.

22. Per le foglie `Result Analysis`, usa formulazioni comparative o osservative, spesso con aperture come `The results ...`, `The measured ...`, `The recorded ...`, oppure con riferimenti a metriche, tabelle e figure.

   Supporto quantitativo. Su `566` foglie `Result Analysis` ufficiali, il requirement ha media `25.45` parole, mediana `21`, deviazione standard `13.35`, IQR `16-33`, minimo `6`, massimo `85`; in caratteri la media e` `163.68`, IQR `97.25-209`. Il `79.0%` inizia con `The`; il `30.8%` contiene esplicitamente frasi evidenziali del tipo `results show`, `measured`, `recorded`. Le aperture piu` frequenti sono `the recorded (154)`, `the intra-lpips (42)`, `the average (27)`, `the slope (22)`, `the mean (19)`; i 3-gram dominanti sono `the recorded metrics (126)` e `the results show (15)`. Gli esempi annotati `sample-specific-masks` e `robust-clip` mostrano la regola operativa piu` importante per un generatore: `compute/report X` e` `Code Execution`; `X is around Y`, `X is better than Y`, `the recorded metrics show that ...` e` `Result Analysis`.

23. Mantieni coerenza stilistica all'interno di ogni sottoalbero: i requirement delle foglie dovrebbero condividere struttura sintattica e livello di specificita`.

   Supporto quantitativo e qualitativo. Il benchmark mostra forte riuso di template lessicali. Le sequenze di blocchi piu` frequenti non sono solo `Code Development > Code Execution`, ma anche ripetizioni seriali come `Code Development > Code Execution > Code Development > Code Execution` e sue estensioni lunghe, segno che interi sottoalberi sono generati tramite template locali ripetuti. Gli esempi annotati sono espliciti: `sample-specific-masks` usa serie quasi seriali di foglie `Code Execution` con variazioni minime in backbone, metodo, dataset e seeds; `lbcs` replica ripetutamente il motivo `benchmark -> k -> {Code Development, Code Execution}`; `all-in-one` usa griglie sistematiche `task x model x budget`. Un generatore automatico non deve forzare varieta` stilistica artificiale: deve preservare la regolarita` locale.

### Scope Management

24. Ogni foglia dovrebbe rappresentare un'unita` atomica verificabile: un componente implementato, un esperimento eseguito, oppure un claim di risultato confrontabile.

   Supporto quantitativo e qualitativo. L'intero schema PaperBench funziona cosi` per design: le foglie sono l'unico punto in cui compare `task_category`, quindi sono l'unita` minima giudicabile dal judge. La triade osservata nei requirement lo conferma: `Code Development` valuta esistenza/correttezza del codice, `Code Execution` valuta l'avvenuta esecuzione, `Result Analysis` valuta l'evidenza prodotta. Gli esempi annotati mostrano il criterio di atomizzazione: un dataset preparato, un backbone addestrato, una tabella prodotta, un trend verificato. Quando una foglia fa contemporaneamente implementazione, run e interpretazione, il benchmark tende a spezzarla.

25. Usa nodi interni per raggruppare famiglie naturali di foglie: stesso modulo, stesso dataset/task, stessa tabella/figura, stessa parte di algoritmo o stesso blocco sperimentale.

   Supporto quantitativo. Le classi strutturali del primo livello e i valori medi di foglie discendenti quantificano questi raggruppamenti: `Method/contribution` media `15.24` foglie, `Section-oriented` media `66.03`, `Experiment/result` media `96.26`. Ai livelli intermedi gli esempi annotati mostrano logiche ricorrenti: decomposizione per componente algoritmica quando il paper ha procedure nominate, decomposizione per benchmark o famiglia di risultati quando il paper ha molte tabelle, decomposizione per dataset o protocollo quando i run si moltiplicano. Il principio da imitare e` sempre lo stesso: il nodo interno deve corrispondere a una famiglia naturale leggibile anche senza guardare i fratelli.

26. Quando un paper ha molti benchmark o ambienti, usa prima un raggruppamento per famiglia di esperimenti e solo dopo scendi a singoli requirement atomici.

   Supporto quantitativo e qualitativo. Le correlazioni cross-rubric mostrano che `total_nodes` cresce con `avg_leaf_depth` (`r = 0.708`) e con `ex_share` (`r = 0.595`), ma quasi non cresce con `root_children` (`r = 0.108`) o con `avg_branching_factor` (`r = 0.070`). Questo significa che i paper grandi non vengono scalati aggiungendo molti figli al root, ma stratificando template sperimentali su piu` livelli. `lbcs` e` il caso estremo: `1471` nodi, `avg_branching_factor = 2.65`, `avg_leaf_depth = 6.44`. `sample-specific-masks` mostra la variante opposta ma compatibile: `396` nodi, branching alto `6.08`, molte griglie sperimentali seriali. La regola generale e` che per molti benchmark si organizza prima la famiglia di esperimenti, poi il dataset/ambiente, poi il metodo o il protocollo, e solo infine il requisito atomico.

### Caveat

27. Le rubriche presenti su disco sono 23: i 20 paper ufficiali dello split `all` piu` 3 rubriche `dev`. Le regole sopra sono calibrate sul set ufficiale da 20 per aderire al benchmark descritto nel README.

   Supporto quantitativo. `official-20` ha media `560.9` nodi contro `273.3` per `dev-3`, ma i pattern principali restano stabili: `avg_branching_factor` `3.983` vs `3.979`, `avg_leaf_depth` `4.466` vs `4.142`, mix di foglie `53.1/32.9/14.0` contro `49.2/41.7/9.2`. La scelta corretta per una skill che voglia generare rubriche benchmark-conformi e` usare `official-20` come prior strutturale e leggere `dev-3` solo come controllo di robustezza.

28. Usa il nome della cartella come identificatore canonico del paper quando il dataset contiene mismatch tra path e `config.yaml` (caso osservato: `stochastic-interpolants` vs `stochastic-interpolant`).

   Supporto quantitativo e di compatibilita`. Nei file di analisi aggregata la canonizzazione per nome cartella e` necessaria per evitare mismatch tra `paper_id`, `config_id` e percorso su disco. Questo e` un caveat di dataset hygiene, non una regola strutturale della rubric; ma per una pipeline di generazione o validazione automatica e` importante usare l'identificatore che compare nel path dei dati.

## Benchmark-Level Summary Tables

### Summary Statistics Calibrated On `official-20`

| metric               |     mean |   median |     std |       q1 |       q3 |      min | min_paper                 |      max | max_paper                  |
|:---------------------|---------:|---------:|--------:|---------:|---------:|---------:|:--------------------------|---------:|:---------------------------|
| total_nodes          |  560.9   |  257.5   | 616.575 |  182.5   |  732.25  |   94     | stochastic-interpolants   | 2551     | pinn                       |
| leaf_nodes           |  415.8   |  192     | 465.032 |  122.5   |  525     |   69     | stochastic-interpolants   | 1963     | pinn                       |
| internal_nodes       |  145.1   |   69     | 162.154 |   46.75  |  205.5   |   25     | stochastic-interpolants   |  588     | pinn                       |
| max_depth            |    5.8   |    5     |   1.322 |    5     |    7     |    4     | bridging-data-gaps        |    9     | bam                        |
| avg_leaf_depth       |    4.466 |    4.155 |   1.2   |    3.686 |    4.889 |    2.625 | mechanistic-understanding |    6.962 | pinn                       |
| root_children        |    6.85  |    6.5   |   2.621 |    5     |    8     |    2     | ftrl                      |   13     | lca-on-the-line            |
| avg_branching_factor |    3.983 |    3.848 |   0.912 |    3.422 |    4.352 |    2.649 | lbcs                      |    6.077 | sample-specific-masks      |
| paper_word_count     | 6142     | 6132     | 756.802 | 5793.5   | 6640.5   | 4259     | robust-clip               | 7782     | test-time-model-adaptation |
| paper_page_count     |   24.9   |   23     |   8.908 |   17.75  |   32.25  |   14     | sapg                      |   40     | bam                        |
| cd_share             |    0.531 |    0.528 |   0.21  |    0.375 |    0.68  |    0.064 | pinn                      |    0.947 | what-will-my-model-forget  |
| ex_share             |    0.329 |    0.29  |   0.236 |    0.11  |    0.453 |    0.03  | what-will-my-model-forget |    0.925 | pinn                       |
| rm_share             |    0.14  |    0.124 |   0.117 |    0.033 |    0.218 |    0.011 | pinn                      |    0.413 | bridging-data-gaps         |

### Cross-Check Summary On `all-23`

| metric               |     mean |   median |     std |       q1 |       q3 |      min | min_paper                 |      max | max_paper                  |
|:---------------------|---------:|---------:|--------:|---------:|---------:|---------:|:--------------------------|---------:|:---------------------------|
| total_nodes          |  523.391 |  279     | 583.248 |  179     |  562.5   |   94     | stochastic-interpolants   | 2551     | pinn                       |
| leaf_nodes           |  387.87  |  206     | 439.629 |  122     |  399     |   69     | stochastic-interpolants   | 1963     | pinn                       |
| internal_nodes       |  135.522 |   73     | 153.385 |   44.5   |  171     |   23     | semantic-self-consistency |  588     | pinn                       |
| max_depth            |    5.696 |    5     |   1.295 |    5     |    6.5   |    4     | bridging-data-gaps        |    9     | bam                        |
| avg_leaf_depth       |    4.424 |    4.247 |   1.16  |    3.671 |    4.921 |    2.625 | mechanistic-understanding |    6.962 | pinn                       |
| root_children        |    6.783 |    6     |   2.449 |    5.5   |    8     |    2     | ftrl                      |   13     | lca-on-the-line            |
| avg_branching_factor |    3.983 |    3.883 |   0.866 |    3.39  |    4.339 |    2.649 | lbcs                      |    6.077 | sample-specific-masks      |
| paper_word_count     | 5986.7   | 6080     | 962.201 | 5737     | 6568     | 3003     | semantic-self-consistency | 7782     | test-time-model-adaptation |
| paper_page_count     |   25.087 |   24     |   8.344 |   18     |   30.5   |   14     | sapg                      |   40     | bam                        |
| cd_share             |    0.526 |    0.529 |   0.204 |    0.374 |    0.667 |    0.064 | pinn                      |    0.947 | what-will-my-model-forget  |
| ex_share             |    0.34  |    0.29  |   0.228 |    0.167 |    0.455 |    0.03  | what-will-my-model-forget |    0.925 | pinn                       |
| rm_share             |    0.134 |    0.102 |   0.11  |    0.046 |    0.215 |    0.011 | pinn                      |    0.413 | bridging-data-gaps         |

## Complete Per-Paper Structural Table

La tabella seguente riporta, per tutti i 23 paper disponibili su disco, le metriche strutturali centrali che un generatore deve saper controllare: dimensione, profondita`, branching, ampiezza del root e mix dei tipi foglia.

| paper_id                                    | split_group   | topic_group                                |   paper_word_count |   paper_page_count |   total_nodes |   leaf_nodes |   internal_nodes |   max_depth |   avg_leaf_depth |   root_children |   avg_branching_factor | cd_share   | ex_share   | rm_share   |
|:--------------------------------------------|:--------------|:-------------------------------------------|-------------------:|-------------------:|--------------:|-------------:|-----------------:|------------:|-----------------:|----------------:|-----------------------:|:-----------|:-----------|:-----------|
| adaptive-pruning                            | official-20   | Continual learning / efficient fine-tuning |               6808 |                 20 |           172 |          123 |               49 |           5 |             3.9  |               5 |                   3.49 | 69.9%      | 8.1%       | 22.0%      |
| all-in-one                                  | official-20   | Simulation-based inference                 |               6018 |                 32 |           234 |          174 |               60 |           6 |             4.25 |               5 |                   3.88 | 52.9%      | 35.6%      | 11.5%      |
| bam                                         | official-20   | Simulation-based inference                 |               6631 |                 40 |          1021 |          789 |              232 |           9 |             6.86 |               4 |                   4.4  | 32.3%      | 65.7%      | 2.0%       |
| bbox                                        | official-20   | LLMs / prompting / adaptation              |               5304 |                 25 |           422 |          279 |              143 |           7 |             4.62 |               9 |                   2.94 | 52.0%      | 29.0%      | 19.0%      |
| bridging-data-gaps                          | official-20   | Diffusion / generative modeling            |               6184 |                 16 |           207 |          172 |               35 |           4 |             2.88 |               8 |                   5.89 | 30.2%      | 28.5%      | 41.3%      |
| fre                                         | official-20   | Reinforcement learning                     |               5543 |                 16 |           636 |          437 |              199 |           6 |             5.37 |               6 |                   3.19 | 70.0%      | 28.4%      | 1.6%       |
| ftrl                                        | official-20   | Reinforcement learning                     |               5765 |                 40 |           233 |          178 |               55 |           7 |             4.79 |               2 |                   4.22 | 67.4%      | 11.2%      | 21.3%      |
| lbcs                                        | official-20   | Data selection / optimization              |               6669 |                 22 |          1471 |          916 |              555 |           7 |             6.44 |               7 |                   2.65 | 52.9%      | 44.8%      | 2.3%       |
| lca-on-the-line                             | official-20   | Vision / OOD / robustness                  |               7161 |                 24 |          1048 |          819 |              229 |           5 |             3.7  |              13 |                   4.57 | 49.2%      | 45.2%      | 5.6%       |
| mechanistic-understanding                   | official-20   | LLMs / prompting / adaptation              |               6185 |                 18 |           128 |           96 |               32 |           4 |             2.62 |              12 |                   3.97 | 37.5%      | 45.8%      | 16.7%      |
| pinn                                        | official-20   | Scientific ML / physics-informed learning  |               5803 |                 33 |          2551 |         1963 |              588 |           8 |             6.96 |               7 |                   4.34 | 6.4%       | 92.5%      | 1.1%       |
| rice                                        | official-20   | Reinforcement learning                     |               6712 |                 26 |           489 |          361 |              128 |           5 |             4.47 |               9 |                   3.81 | 49.3%      | 47.1%      | 3.6%       |
| robust-clip                                 | official-20   | Vision / OOD / robustness                  |               4259 |                 20 |           146 |          106 |               40 |           5 |             3.52 |               6 |                   3.62 | 66.0%      | 7.5%       | 26.4%      |
| sample-specific-masks                       | official-20   | Vision / OOD / robustness                  |               5845 |                 26 |           396 |          331 |               65 |           6 |             4.86 |               5 |                   6.08 | 26.3%      | 67.4%      | 6.3%       |
| sapg                                        | official-20   | Reinforcement learning                     |               5811 |                 14 |           279 |          206 |               73 |           5 |             3.44 |               8 |                   3.81 | 37.4%      | 31.1%      | 31.6%      |
| sequential-neural-score-estimation          | official-20   | Simulation-based inference                 |               6505 |                 38 |           123 |           92 |               31 |           5 |             3.64 |               7 |                   3.94 | 72.8%      | 5.4%       | 21.7%      |
| stay-on-topic-with-classifier-free-guidance | official-20   | LLMs / prompting / adaptation              |               6080 |                 38 |           186 |          121 |               65 |           7 |             4.98 |               6 |                   2.85 | 57.9%      | 28.9%      | 13.2%      |
| stochastic-interpolants                     | official-20   | Diffusion / generative modeling            |               5376 |                 17 |            94 |           69 |               25 |           5 |             4.01 |               4 |                   3.72 | 84.1%      | 10.1%      | 5.8%       |
| test-time-model-adaptation                  | official-20   | Vision / OOD / robustness                  |               7782 |                 18 |           236 |          163 |               73 |           5 |             3.94 |               8 |                   3.22 | 52.8%      | 22.1%      | 25.2%      |
| what-will-my-model-forget                   | official-20   | Continual learning / efficient fine-tuning |               6399 |                 15 |          1146 |          921 |              225 |           5 |             4.06 |               6 |                   5.09 | 94.7%      | 3.0%       | 2.3%       |
| self-composing-policies                     | dev-3         | Reinforcement learning                     |               6142 |                 29 |           357 |          275 |               82 |           5 |             4.35 |               6 |                   4.34 | 54.9%      | 34.9%      | 10.2%      |
| self-expansion                              | dev-3         | Continual learning / efficient fine-tuning |               5709 |                 23 |           363 |          253 |              110 |           6 |             5.01 |               7 |                   3.29 | 27.7%      | 62.8%      | 9.5%       |
| semantic-self-consistency                   | dev-3         | LLMs / prompting / adaptation              |               3003 |                 27 |           100 |           77 |               23 |           4 |             3.06 |               6 |                   4.3  | 64.9%      | 27.3%      | 7.8%       |

## Topic-Level Variation

La variazione per topic non deve essere trattata come uno schema rigido, ma e` un prior utile per scegliere il mix dei tipi foglia in modo plausibile.

| topic_group                                |   n_papers |   avg_total_nodes |   avg_leaf_nodes |   avg_max_depth | avg_cd_share   | avg_ex_share   | avg_rm_share   |   avg_root_children |
|:-------------------------------------------|-----------:|------------------:|-----------------:|----------------:|:---------------|:---------------|:---------------|--------------------:|
| Continual learning / efficient fine-tuning |          3 |            560.33 |           432.33 |            5.33 | 64.1%          | 24.7%          | 11.2%          |                6    |
| Data selection / optimization              |          1 |           1471    |           916    |            7    | 52.9%          | 44.8%          | 2.3%           |                7    |
| Diffusion / generative modeling            |          2 |            150.5  |           120.5  |            4.5  | 57.1%          | 19.3%          | 23.5%          |                6    |
| LLMs / prompting / adaptation              |          4 |            209    |           143.25 |            5.5  | 53.1%          | 32.8%          | 14.2%          |                8.25 |
| Reinforcement learning                     |          5 |            398.8  |           291.4  |            5.6  | 55.8%          | 30.5%          | 13.7%          |                6.2  |
| Scientific ML / physics-informed learning  |          1 |           2551    |          1963    |            8    | 6.4%           | 92.5%          | 1.1%           |                7    |
| Simulation-based inference                 |          3 |            459.33 |           351.67 |            6.67 | 52.7%          | 35.6%          | 11.8%          |                5.33 |
| Vision / OOD / robustness                  |          4 |            456.5  |           354.75 |            5.25 | 48.6%          | 35.5%          | 15.9%          |                8    |

Interpretazione. I topic non determinano la struttura da soli, ma spostano in modo netto il prior sui tipi foglia. I paper di `Scientific ML / physics-informed learning` e `Data selection / optimization` tendono a usare piu` `Code Execution` perche' replicano molte griglie di esperimenti. I paper di `Diffusion / generative modeling` e alcuni `Vision / OOD / robustness` usano piu` `Result Analysis` quando il paper insiste su claim numerici e comparativi collegati a metriche come FID, robustness score o transfer trend.

## Aggregate Depth And Branching Distributions

### Global Leaf Depth Histogram On `official-20`

|   leaf_depth |   count |      share |
|-------------:|--------:|-----------:|
|            1 |       3 | 0.00036075 |
|            2 |     212 | 0.025493   |
|            3 |    1150 | 0.138288   |
|            4 |    1809 | 0.217532   |
|            5 |    1396 | 0.167869   |
|            6 |     751 | 0.0903078  |
|            7 |    2231 | 0.268278   |
|            8 |     724 | 0.0870611  |
|            9 |      40 | 0.00481    |

### Internal-Node Branching Histogram On `official-20`

|   children_per_internal_node |   count |      share |
|-----------------------------:|--------:|-----------:|
|                            2 |    1122 | 0.38663    |
|                            3 |     517 | 0.178153   |
|                            4 |     454 | 0.156444   |
|                            5 |     217 | 0.074776   |
|                            6 |     307 | 0.105789   |
|                            7 |      76 | 0.0261888  |
|                            8 |      82 | 0.0282564  |
|                            9 |      37 | 0.0127498  |
|                           10 |      31 | 0.0106823  |
|                           11 |      33 | 0.0113715  |
|                           12 |       7 | 0.00241213 |
|                           13 |       5 | 0.00172295 |
|                           14 |       2 | 0.00068918 |
|                           16 |       4 | 0.00137836 |
|                           19 |       1 | 0.00034459 |
|                           26 |       1 | 0.00034459 |
|                           30 |       6 | 0.00206754 |

### Root-Child Distribution Across Official Papers

|   root_children |   n_papers |   share |
|----------------:|-----------:|--------:|
|               2 |          1 |    0.05 |
|               4 |          2 |    0.1  |
|               5 |          3 |    0.15 |
|               6 |          4 |    0.2  |
|               7 |          3 |    0.15 |
|               8 |          3 |    0.15 |
|               9 |          2 |    0.1  |
|              12 |          1 |    0.05 |
|              13 |          1 |    0.05 |

## First-Level Structure: Quantitative Typology And Qualitative Patterns

### Root-Child Structural Classes

#### `official-20`

| class                            |   count | share   |   mean_local_share |   median_local_share |   std_local_share |   q1_local_share |   q3_local_share |   min_local_share |   max_local_share |   mean_desc_leaves |   median_desc_leaves |   q1_desc_leaves |   q3_desc_leaves |   min_desc_leaves |   max_desc_leaves |
|:---------------------------------|--------:|:--------|-------------------:|---------------------:|------------------:|-----------------:|-----------------:|------------------:|------------------:|-------------------:|---------------------:|-----------------:|-----------------:|------------------:|------------------:|
| Experiment/result block          |      50 | 36.5%   |              0.164 |                0.143 |             0.129 |            0.068 |            0.202 |             0.056 |             0.667 |              96.26 |                   24 |             10   |            56.75 |                 1 |              1866 |
| Hybrid contribution/result block |      11 | 8.0%    |              0.136 |                0.125 |             0.061 |            0.094 |            0.172 |             0.04  |             0.25  |              54.55 |                   23 |              6.5 |            33.5  |                 2 |               388 |
| Method/contribution block        |      37 | 27.0%   |              0.155 |                0.115 |             0.103 |            0.08  |            0.22  |             0.011 |             0.435 |              15.24 |                   11 |              6   |            26    |                 1 |                46 |
| Other                            |       6 | 4.4%    |              0.128 |                0.082 |             0.111 |            0.061 |            0.154 |             0.038 |             0.333 |              26.67 |                   10 |              3.5 |            13.5  |                 2 |               122 |
| Section-oriented block           |      33 | 24.1%   |              0.115 |                0.111 |             0.04  |            0.077 |            0.154 |             0.056 |             0.222 |              66.03 |                   35 |             14   |            63    |                 5 |               363 |

#### `all-23`

| class                            |   count | share   |   mean_local_share |   median_local_share |   std_local_share |   q1_local_share |   q3_local_share |   min_local_share |   max_local_share |   mean_desc_leaves |   median_desc_leaves |   q1_desc_leaves |   q3_desc_leaves |   min_desc_leaves |   max_desc_leaves |
|:---------------------------------|--------:|:--------|-------------------:|---------------------:|------------------:|-----------------:|-----------------:|------------------:|------------------:|-------------------:|---------------------:|-----------------:|-----------------:|------------------:|------------------:|
| Experiment/result block          |      53 | 34.0%   |              0.172 |                0.143 |             0.135 |            0.071 |            0.22  |             0.056 |             0.667 |              95.49 |                   25 |            10    |            57    |                 1 |              1866 |
| Hybrid contribution/result block |      12 | 7.7%    |              0.141 |                0.143 |             0.061 |            0.103 |            0.182 |             0.04  |             0.25  |              57.75 |                   26 |             6.75 |            40.25 |                 2 |               388 |
| Method/contribution block        |      45 | 28.8%   |              0.155 |                0.115 |             0.106 |            0.08  |            0.22  |             0.011 |             0.435 |              14.62 |                    9 |             5    |            23    |                 1 |                46 |
| Other                            |       7 | 4.5%    |              0.122 |                0.083 |             0.103 |            0.066 |            0.132 |             0.038 |             0.333 |              23.29 |                    8 |             2.5  |            13    |                 2 |               122 |
| Section-oriented block           |      39 | 25.0%   |              0.112 |                0.111 |             0.038 |            0.077 |            0.125 |             0.056 |             0.222 |              60.15 |                   30 |            12.5  |            63.5  |                 2 |               363 |

Pattern strutturali chiave emersi dalle annotazioni.

Nei paper piccoli e focalizzati, come `stochastic-interpolants`, il root puo` avere pochi figli se ciascun figlio rappresenta una macro-funzione distinta: prerequisiti, modelli, infrastruttura di valutazione condivisa, risultati. Questo e` il caso canonico in cui una componente infrastrutturale condivisa va promossa al primo livello con peso basso: il blocco FID non e` un contributo centrale del paper, ma e` riusato trasversalmente, quindi la promozione a primo livello rende esplicita la dipendenza senza gonfiare troppo il peso.

Quando il paper contiene pseudocodice o procedure nominate, la rubric tende a riusarle come nodi intermedi. `stochastic-interpolants` e` l'esempio piu` pulito: gli algoritmi nominati nel paper vengono riassorbiti nella gerarchia come sottounita` metodologiche. Questo pattern e` importante per la generazione automatica perche' evita nomi inventati: se il paper ha gia` una tassonomia procedurale, la rubric la eredita.

Quando il paper e` fortemente benchmark-driven, il root puo` diventare piu` section-oriented, ma quasi sempre solo per sezioni sperimentali pesanti. `robust-clip` separa blocchi che corrispondono quasi uno-a-uno alle principali sezioni di evaluation; `lbcs` porta questa logica piu` lontano, ma lo fa solo perche' il paper stesso e` organizzato come una sequenza di blocchi empirici relativamente autonomi.

Quando il paper ha molti benchmark ripetuti, la struttura scala per template locali. `sample-specific-masks` usa matrici larghe `backbone x metodo x dataset x seed`; `lbcs` usa template profondi e stretti del tipo `benchmark -> k -> {Code Development, Code Execution}`. La differenza importante e` che il benchmark accetta entrambe le soluzioni, purché il template sia leggibile e coerente.

## Requirement Text: Length And Lexical Patterns

### Requirement Length By Node Type On `official-20`

| group            |   n_nodes |   mean_words |   median_words |   std_words |   q1_words |   q3_words |   min_words |   max_words |   mean_chars |   median_chars |   std_chars |   q1_chars |   q3_chars |   min_chars |   max_chars |
|:-----------------|----------:|-------------:|---------------:|------------:|-----------:|-----------:|------------:|------------:|-------------:|---------------:|------------:|-----------:|-----------:|------------:|------------:|
| Internal         |      2902 |        22.23 |             21 |       10.88 |         14 |         30 |           2 |          67 |       141.58 |            136 |       66.49 |      89    |        187 |          16 |         483 |
| Code Development |      3671 |        27.79 |             26 |       12.39 |         19 |         35 |           3 |         106 |       181.76 |            174 |       83.74 |     126    |        222 |          21 |         716 |
| Code Execution   |      4079 |        42.87 |             41 |       21.83 |         28 |         55 |           5 |         106 |       257.57 |            236 |      130.71 |     175    |        326 |          40 |         660 |
| Result Analysis  |       566 |        25.45 |             21 |       13.35 |         16 |         33 |           6 |          85 |       163.68 |            140 |       89.36 |      97.25 |        209 |          33 |         568 |

L'ordine di lunghezza e` stabile e utile per la generazione: `Code Execution` e` di gran lunga il tipo piu` lungo; `Code Development` e` intermedio ma piu` procedurale; `Result Analysis` e` relativamente corto ma semanticamente denso; i nodi interni sono i piu` brevi e astratti.

Le due tabelle lessicali che seguono sono entrambe calcolate sullo stesso scope, cioe` `official-20`. Questo allineamento e` intenzionale: in una versione precedente la tabella degli opening era stata ereditata da un'aggregazione `all-23`, creando un'inconsistenza di confronto con i pattern di supporto.

### Text Pattern Support

| group            | pattern                           |   count |       share |
|:-----------------|:----------------------------------|--------:|------------:|
| Internal         | starts with `The`                 |     969 | 0.310876    |
| Internal         | starts with `When`                |      67 | 0.021495    |
| Internal         | starts with `Code for`            |       5 | 0.00160411  |
| Internal         | contains `has been implemented`   |     246 | 0.078922    |
| Internal         | contains `is reported`            |       0 | 0           |
| Internal         | contains result-evidence phrasing |      32 | 0.0102663   |
| Code Development | starts with `The`                 |     574 | 0.145611    |
| Code Development | starts with `When`                |      81 | 0.0205479   |
| Code Development | starts with `Code for`            |      30 | 0.00761035  |
| Code Development | contains `has been implemented`   |    1443 | 0.366058    |
| Code Development | contains `is reported`            |       2 | 0.000507357 |
| Code Development | contains result-evidence phrasing |       6 | 0.00152207  |
| Code Execution   | starts with `The`                 |     709 | 0.162801    |
| Code Execution   | starts with `When`                |     306 | 0.0702641   |
| Code Execution   | starts with `Code for`            |       0 | 0           |
| Code Execution   | contains `has been implemented`   |       0 | 0           |
| Code Execution   | contains `is reported`            |       5 | 0.00114811  |
| Code Execution   | contains result-evidence phrasing |       0 | 0           |
| Result Analysis  | starts with `The`                 |     493 | 0.790064    |
| Result Analysis  | starts with `When`                |       6 | 0.00961538  |
| Result Analysis  | starts with `Code for`            |       0 | 0           |
| Result Analysis  | contains `has been implemented`   |       0 | 0           |
| Result Analysis  | contains `is reported`            |       0 | 0           |
| Result Analysis  | contains result-evidence phrasing |     192 | 0.307692    |

### Most Frequent Openings

| group            |   n_nodes | top_opening_2                                                                             | top_opening_3                                                                                                        |
|:-----------------|----------:|:------------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------|
| Internal         |      2902 | code has (723); the results (146); for the (95); the correct (93); lbcs has (82)          | code has been (723); the correct dataset (89); lbcs has been (82); a fre agent (63); uniform sampling coreset (57)   |
| Code Development |      3671 | code has (2040); for the (188); code to (128); for each (126); dr is (89)                 | code has been (2040); dr is randomly (89); for each pair (88); code to compute (80); the original validation (65)    |
| Code Execution   |      4079 | code has (1864); when using (305); using the (218); for the (159); 10 seeded (78)         | code has been (1864); when using advi (141); when using bam (113); 10 seeded runs (78); lbcs has been (68)           |
| Result Analysis  |       566 | the recorded (127); the intra-lpips (42); the average (27); the slope (22); the measured (16) | the recorded metrics (105); the intra-lpips score (42); the slope of (22); the fid score (16); the results show (15) |

Interpretazione lessicale. La distinzione tra `Code Execution` e `Result Analysis` e` determinata soprattutto dalla formulazione verbale. Se il requirement chiede di produrre una tabella, calcolare una metrica o eseguire un protocollo, la formulazione e` run-oriented e il nodo deve essere `Code Execution`. Se il requirement giudica se la metrica ottenuta supporta un claim del paper, la formulazione diventa evidenziale o comparativa e il nodo deve essere `Result Analysis`. Questa regola, emersa chiaramente in `robust-clip` e `sample-specific-masks`, e` una delle piu` importanti da codificare in una skill generativa.

## Weights By Depth And By Leaf Type

### Weight Distribution By Depth On `official-20`

|   depth |   n_nodes |   mean_raw_weight |   median_raw_weight |   std_raw_weight |   q1_raw_weight |   q3_raw_weight |   min_raw_weight |   max_raw_weight |   mean_local_share |   median_local_share |   q1_local_share |   q3_local_share |   min_local_share |   max_local_share |
|--------:|----------:|------------------:|--------------------:|-----------------:|----------------:|----------------:|-----------------:|-----------------:|-------------------:|---------------------:|-----------------:|-----------------:|------------------:|------------------:|
|       0 |        20 |             1     |                   1 |            0     |               1 |               1 |                1 |                1 |              1     |                1     |            1     |            1     |             1     |             1     |
|       1 |       137 |             2.693 |                   1 |            3.47  |               1 |               3 |                1 |               20 |              0.146 |                0.118 |            0.077 |            0.167 |             0.011 |             0.667 |
|       2 |       603 |             1.38  |                   1 |            0.857 |               1 |               1 |                1 |                8 |              0.222 |                0.182 |            0.111 |            0.264 |             0.05  |             0.8   |
|       3 |      1686 |             1.134 |                   1 |            0.47  |               1 |               1 |                1 |                6 |              0.232 |                0.2   |            0.125 |            0.333 |             0.033 |             0.857 |
|       4 |      2315 |             1.12  |                   1 |            0.52  |               1 |               1 |                1 |                7 |              0.232 |                0.2   |            0.125 |            0.333 |             0.056 |             0.8   |
|       5 |      1792 |             1.069 |                   1 |            0.264 |               1 |               1 |                1 |                4 |              0.282 |                0.25  |            0.167 |            0.333 |             0.038 |             0.8   |
|       6 |      1408 |             1.017 |                   1 |            0.184 |               1 |               1 |                1 |                3 |              0.281 |                0.25  |            0.2   |            0.5   |             0.091 |             0.5   |
|       7 |      2473 |             1.196 |                   1 |            0.593 |               1 |               1 |                1 |                3 |              0.266 |                0.167 |            0.125 |            0.5   |             0.125 |             0.5   |
|       8 |       744 |             1     |                   1 |            0     |               1 |               1 |                1 |                1 |              0.325 |                0.333 |            0.333 |            0.333 |             0.167 |             0.5   |
|       9 |        40 |             1     |                   1 |            0     |               1 |               1 |                1 |                1 |              0.5   |                0.5   |            0.5   |            0.5   |             0.5   |             0.5   |

### Weight Distribution By Leaf Type On `official-20`

| leaf_type        |   n_leaves |   mean_raw_weight |   median_raw_weight |   std_raw_weight |   q1_raw_weight |   q3_raw_weight |   min_raw_weight |   max_raw_weight |   mean_local_share |   median_local_share |   q1_local_share |   q3_local_share |   mean_effective_weight |   median_effective_weight |   q1_effective_weight |   q3_effective_weight |   min_effective_weight |   max_effective_weight |   total_effective_weight |
|:-----------------|-----------:|------------------:|--------------------:|-----------------:|----------------:|----------------:|-----------------:|-----------------:|-------------------:|---------------------:|-----------------:|-----------------:|------------------------:|--------------------------:|----------------------:|----------------------:|-----------------------:|-----------------------:|-------------------------:|
| Code Development |       3671 |            1.0447 |                   1 |           0.2645 |               1 |               1 |                1 |                8 |             0.2682 |                 0.25 |           0.125  |           0.5    |               0.0027292 |                 0.000496  |             0.0002588 |             0.0021368 |              2.06e-05  |              0.163265  |                 10.0189  |
| Code Execution   |       4079 |            1.1434 |                   1 |           0.4979 |               1 |               1 |                1 |                3 |             0.2629 |                 0.25 |           0.125  |           0.375  |               0.0007551 |                 6.87e-05  |             2.29e-05  |             0.0002849 |              7.6e-06   |              0.0555556 |                  3.08022 |
| Result Analysis  |        566 |            1.3216 |                   1 |           0.5004 |               1 |               2 |                1 |                3 |             0.2867 |                 0.25 |           0.1667 |           0.3333 |               0.0121923 |                 0.0074074 |             0.0037037 |             0.0148148 |              0.0012821 |              0.177778  |                  6.90084 |

Interpretazione. Il risultato importante non e` che `Result Analysis` abbia sempre un peso grezzo piu` alto, ma che il benchmark le assegna sistematicamente piu` peso effettivo tramite la gerarchia. Per una skill generativa questo si traduce in una regola pratica: se un claim finale e` davvero importante, non basta aggiungere una foglia `Result Analysis`; bisogna metterla in un sottoalbero che eredita abbastanza massa di peso dal root.

## Ordering, Dependencies, And Transition Structure

### Summary Statistics

| scope             |   n_nodes |   phase_monotonic_share |   single_block_per_type_share |   contains_all_three_share |   exact_cd_ex_rm_share |   exact_cd_ex_rm_given_all_three_share |
|:------------------|----------:|------------------------:|------------------------------:|---------------------------:|-----------------------:|---------------------------------------:|
| all_internal      |      3117 |                0.844722 |                      0.845364 |                  0.0481232 |              0.0461983 |                               0.96     |
| official_internal |      2902 |                0.837698 |                      0.838043 |                  0.0461751 |              0.0441075 |                               0.955224 |
| root_children     |       156 |                0.49359  |                      0.49359  |                  0.448718  |              0.416667  |                               0.928571 |

### First Occurrence Order

| leaf_first_occurrence_order                         |   count |       share |
|:----------------------------------------------------|--------:|------------:|
| Code Development > Code Execution                   |    1142 | 0.366378    |
| Code Execution                                      |     794 | 0.254732    |
| Code Development                                    |     766 | 0.245749    |
| Code Development > Code Execution > Result Analysis |     144 | 0.0461983   |
| Result Analysis                                     |     124 | 0.0397818   |
| Code Execution > Result Analysis                    |      93 | 0.0298364   |
| Code Execution > Code Development                   |      31 | 0.00994546  |
| Code Development > Result Analysis                  |      17 | 0.00545396  |
| Code Execution > Code Development > Result Analysis |       4 | 0.00128329  |
| Code Development > Result Analysis > Code Execution |       2 | 0.000641643 |

### Most Frequent Full Block Sequences

| leaf_sequence_blocks                                                                                                                                                                                                                                                                                                                                                                                                                          |   count |      share |
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------:|-----------:|
| Code Development > Code Execution                                                                                                                                                                                                                                                                                                                                                                                                             |     810 | 0.259865   |
| Code Execution                                                                                                                                                                                                                                                                                                                                                                                                                                |     794 | 0.254732   |
| Code Development                                                                                                                                                                                                                                                                                                                                                                                                                              |     766 | 0.245749   |
| Result Analysis                                                                                                                                                                                                                                                                                                                                                                                                                               |     124 | 0.0397818  |
| Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution                                                                                                                                                                                                                                                                                                 |     113 | 0.0362528  |
| Code Execution > Result Analysis                                                                                                                                                                                                                                                                                                                                                                                                              |      82 | 0.0263073  |
| Code Development > Code Execution > Code Development > Code Execution                                                                                                                                                                                                                                                                                                                                                                         |      74 | 0.0237408  |
| Code Development > Code Execution > Result Analysis                                                                                                                                                                                                                                                                                                                                                                                           |      43 | 0.0137953  |
| Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution                                                                                                                                                                                                                                                             |      24 | 0.00769971 |
| Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution > Code Development > Code Execution |      19 | 0.0060956  |
| Code Execution > Code Development > Code Execution                                                                                                                                                                                                                                                                                                                                                                                            |      18 | 0.00577478 |
| Code Development > Result Analysis                                                                                                                                                                                                                                                                                                                                                                                                            |      14 | 0.0044915  |

### Transition Matrix

| from             | to               |   count | row_share   |
|:-----------------|:-----------------|--------:|:------------|
| Code Development | Code Development |       0 | 0.00%       |
| Code Development | Code Execution   |    6119 | 99.22%      |
| Code Development | Result Analysis  |      48 | 0.78%       |
| Code Execution   | Code Development |    4725 | 90.02%      |
| Code Execution   | Code Execution   |       0 | 0.00%       |
| Code Execution   | Result Analysis  |     524 | 9.98%       |
| Result Analysis  | Code Development |     157 | 50.00%      |
| Result Analysis  | Code Execution   |     157 | 50.00%      |
| Result Analysis  | Result Analysis  |       0 | 0.00%       |

Interpretazione. L'ordine dei figli e` semanticamente significativo perche' il judge costruisce il contesto con `get_prior_nodes`, quindi antenati e fratelli precedenti influenzano il grading della foglia corrente. La matrice di transizione mostra che il passaggio diretto `Code Development -> Result Analysis` e` eccezionale (`0.78%`), mentre `Code Development -> Code Execution` e` praticamente la norma. Per una skill generativa questo implica che l'ordinamento non e` un dettaglio cosmetico ma un canale di dipendenza semantica.

## Schema E Compatibilita`

### JSON Fields And Types

La struttura canonica della rubric input e` il dataclass `TaskNode` definito in [`paperbench/rubric/tasks.py`](/Users/riccardoneumarker/Desktop/ETH/TESI/esperimenti/frontier-evals/project/paperbench/paperbench/rubric/tasks.py).

| field | annotated type | obbligatorio nel JSON | default dataclass | comportamento runtime |
|:------|:---------------|:----------------------|:------------------|:----------------------|
| `id` | `str` | si` | nessuno | letto con `data["id"]`; il loader non type-checka esplicitamente la stringa |
| `requirements` | `str` | si` | nessuno | letto con `data["requirements"]`; il loader non type-checka esplicitamente la stringa |
| `weight` | `int` | si` | nessuno | `__post_init__` accetta in pratica `int` o `float`; rifiuta valori non numerici o negativi |
| `sub_tasks` | `Sequence[TaskNode]` | si` | `[]` nel costruttore manuale | nel JSON deve sempre essere presente; per le foglie deve essere `[]` |
| `task_category` | `str \| None` | opzionale in parsing, ma obbligatorio di fatto per le foglie | `None` | deve essere assente o `None` per i nodi interni; deve essere valorizzato sulle foglie |
| `finegrained_task_category` | `str \| None` | opzionale | `None` | se presente deve appartenere all'enum valido; nel flusso standard del judge e` metadata quasi solo di preprocessing |

### Exact Enum Values

`task_category` ammessi dal codice:

| value | uso corretto in una rubric JSON |
|:------|:--------------------------------|
| `Code Development` | si`, categoria foglia canonica |
| `Code Execution` | si`, categoria foglia canonica |
| `Result Analysis` | si`, categoria foglia canonica |
| `Subtree` | no per la rubric dataset; valore speciale usato dal judge per foglie sintetiche di grading |

`finegrained_task_category` ammessi dal codice:

| value |
|:------|
| `Environment & Infrastructure Setup` |
| `Dataset and Model Acquisition` |
| `Data Processing & Preparation` |
| `Method Implementation` |
| `Experimental Setup` |
| `Evaluation, Metrics & Benchmarking` |
| `Logging, Analysis & Presentation` |

Distribuzione osservata sul benchmark ufficiale. Tutte le `8316` foglie ufficiali hanno `finegrained_task_category` non nullo; nessun nodo interno lo ha.

| finegrained_task_category          |   count | share   |
|:-----------------------------------|--------:|:--------|
| Evaluation, Metrics & Benchmarking |    3497 | 42.05%  |
| Experimental Setup                 |    2737 | 32.91%  |
| Method Implementation              |    1250 | 15.03%  |
| Data Processing & Preparation      |     452 | 5.44%   |
| Dataset and Model Acquisition      |     177 | 2.13%   |
| Logging, Analysis & Presentation   |     172 | 2.07%   |
| Environment & Infrastructure Setup |      31 | 0.37%   |

### Validation Constraints Imposed By Code

I vincoli espliciti trovati nel codebase sono i seguenti:

1. `weight` deve essere numerico.
2. `weight` deve essere non negativo.
3. Se `task_category` e` presente, deve appartenere a `VALID_TASK_CATEGORIES`.
4. Se `finegrained_task_category` e` presente, deve appartenere a `VALID_FINEGRAINED_TASK_CATEGORIES`.
5. Un nodo interno non puo` avere `task_category`.
6. Una foglia deve avere `task_category`.
7. `sub_tasks` e` obbligatorio in input anche per le foglie; quindi una foglia valida deve avere `"sub_tasks": []`.

### Implicit Constraints Needed For A Generator

L'ordine dei figli e` semanticamente significativo. `TaskNode.get_prior_nodes()` costruisce il contesto di grading usando antenati, fratelli precedenti del nodo e fratelli precedenti degli antenati. `SimpleJudge` passa quel contesto come `preceding_criteria`. Cambiare l'ordine dei figli cambia quindi l'informazione disponibile al judge.

Gli `id` dovrebbero essere unici. Il loader non lo enforce, ma il codice assume di fatto unicita`: `find(node_id)` restituisce il primo match depth-first, `judge_eval` usa lookup per `task.id`, e il comportamento con duplicati diventa ambiguo. Il benchmark ufficiale non e` perfettamente pulito: in `bbox` compaiono duplicati per `gt-acc-gsm8k`, `gt-acc-scienceqa`, `gt-acc-truthfulqa`; in `bridging-data-gaps` compaiono tre UUID duplicati. Regola prescrittiva per una skill generativa: genera sempre `id` unici, anche se il loader non lo impone.

Le chiavi extra vengono ignorate dal loader. `TaskNode.from_dict()` legge i campi attesi e non rifiuta `additionalProperties`. Questo significa che lo schema implementativo e` piu` permissivo di uno strict JSON Schema. Tuttavia, per compatibilita` reale col benchmark conviene non introdurre campi extra.

`finegrained_task_category` viene usato operativamente quasi solo nel preprocessing `resources_provided()`, che azzera il peso delle foglie con `Dataset and Model Acquisition`. Il judge foglia-per-foglia non la usa direttamente per decidere lo score.

### Score Formula In Pseudocode

```text
function score(node):
    if node is a leaf:
        return node.leaf_score

    total_weight = sum(child.weight for child in node.sub_tasks)
    if total_weight == 0:
        return 0.0

    return sum(score(child) * child.weight for child in node.sub_tasks) / total_weight
```

Conseguenze operative. I pesi si propagano come quote locali. Una foglia con `weight = 1` puo` contare molto se si trova in un ramo con pochi sibling e genitori molto pesanti; una foglia con `weight = 2` puo` contare pochissimo se e` immersa in un ramo largo e leggero. Per la generazione non ha senso ottimizzare il peso grezzo in isolamento.

## Cross-Rubric Correlations

| x           | y                    |   pearson_r |   n_papers |
|:------------|:---------------------|------------:|-----------:|
| total_nodes | paper_word_count     |   0.209769  |         23 |
| total_nodes | paper_page_count     |   0.122781  |         23 |
| total_nodes | max_depth            |   0.552686  |         23 |
| total_nodes | avg_leaf_depth       |   0.708112  |         23 |
| total_nodes | root_children        |   0.108337  |         23 |
| total_nodes | avg_branching_factor |   0.0698995 |         23 |
| total_nodes | ex_share             |   0.594553  |         23 |
| total_nodes | rm_share             |  -0.545175  |         23 |

Interpretazione. La dimensione della rubric correla molto piu` con la struttura sperimentale che con la lunghezza del paper. Il correlato piu` forte e` `avg_leaf_depth` (`r = 0.708`), seguito da `ex_share` (`r = 0.595`) e `max_depth` (`r = 0.553`). `paper_word_count` (`r = 0.210`) e `paper_page_count` (`r = 0.123`) sono deboli. Questo e` il dato piu` importante per calibrare la dimensione di una rubric generata automaticamente.

## Calibrazione Della Dimensione

La regola operativa corretta e` che il numero di nodi dipende soprattutto dal prodotto tra:

1. numero di famiglie di esperimenti distinte;
2. numero di dataset, ambienti o benchmark per famiglia;
3. numero di baseline, varianti o protocolli per benchmark.

Non dipende in modo sostanziale dalla lunghezza del paper. Il fatto che `total_nodes` abbia correlazione molto debole con `paper_word_count` (`r = 0.210`) e con `paper_page_count` (`r = 0.123`) ma forte con `avg_leaf_depth` (`r = 0.708`) mostra che la complessita` della rubric riflette l'ampiezza e la fattorizzazione del piano sperimentale, non il volume di testo del manoscritto.

Gli esempi annotati coprono bene lo spettro:

- `stochastic-interpolants`: `94` nodi. Paper piccolo, con due task principali ben separati e pochi blocchi infrastrutturali. Struttura compatta, `Code Development` dominante (`84.1%`), root con `4` figli.
- `robust-clip`: `146` nodi. Quattro sezioni sperimentali principali, forte componente di claim comparativi, quota `Result Analysis` elevata per il benchmark (`26.4%`), ma profondita` contenuta (`max_depth = 5`).
- `all-in-one`: `234` nodi. Caso tipico, vicino alle medie globali di composizione, con un grosso blocco risultati e sottosezioni sperimentali che ricalcano il paper quasi uno-a-uno.
- `sample-specific-masks`: `396` nodi. Molti benchmark ripetuti e molte combinazioni di backbone, metodi e dataset; quota `Code Execution` molto alta (`67.4%`) e branching medio massimo (`6.08`).
- `lbcs`: `1471` nodi. Sette macro-sezioni, molte famiglie di benchmark, molte baseline e molti valori di `k`; la struttura scala via template ripetuti, con branching basso (`2.65`) e profondita` alta (`avg_leaf_depth = 6.44`).

La formula mentale corretta per stimare la dimensione non e` "paper lungo -> rubric grande", ma qualcosa di piu` vicino a:

```text
rubric_size ~= experiment_families
             x datasets_or_environments_per_family
             x baselines_or_variants_per_dataset
             x phases_per_requirement_bundle
```

dove `phases_per_requirement_bundle` dipende dal fatto che il generatore espliciti solo `Code Development`, oppure anche `Code Execution`, oppure l'intera catena `Code Development -> Code Execution -> Result Analysis`.

Linee guida operative derivate dai dati:

Se il paper ha pochi contributi centrali e pochi blocchi empirici, il root puo` restare sotto i `5` figli e l'albero puo` restare sotto i `150` nodi. Se il paper ha molte sezioni sperimentali ma ogni sezione produce pochi benchmark, il regime tipico e` `150-300` nodi. Se il paper ha molte griglie ripetute ma ancora leggibili come poche famiglie di benchmark, si entra facilmente nel regime `300-700` nodi. Oltre `1000` nodi si entra quasi sempre in paper che combinano molte famiglie di esperimenti con molte varianti per famiglia e molta esplicitazione di `Code Execution`; `pinn` e `lbcs` sono i due archetipi.

## Final Structural Takeaways For A Generator

La struttura PaperBench non e` un semplice albero "metodo poi esperimenti". E` una gerarchia locale di dipendenze che deve contemporaneamente:

1. rispettare i vincoli del codice PaperBench;
2. riflettere la decomposizione semantica del paper;
3. usare il tipo di foglia corretto in funzione della formulazione verbale del requirement;
4. usare i pesi come strumento locale di organizzazione, non come scala globale;
5. scalare con template ripetuti quando la superficie sperimentale del paper cresce.

I pattern piu` invarianti emersi da dati, codice e annotazioni sono quindi questi:

Un root con pochi macro-blocchi e` la norma. I figli del root sono di solito contributi metodologici, blocchi di benchmark o ibridi dei due; le decomposizioni puramente sezionali sono accettate solo quando il paper stesso ha sezioni sperimentali davvero autonome.

Le foglie devono essere tipizzate esclusivamente con `Code Development`, `Code Execution` e `Result Analysis`, e l'ordine locale corretto e` quasi sempre `Code Development -> Code Execution -> Result Analysis` quando il sottoalbero contiene tutte e tre le fasi.

Le componenti infrastrutturali condivise possono essere promosse al primo livello, ma con peso basso. Le procedure nominate e il pseudocodice del paper vanno riusati come nodi intermedi quando esistono. Nei paper con molti benchmark, la struttura scala via template ripetuti con branching basso e profondita` alta oppure tramite matrici piu` larghe ma sempre localmente regolari.

Infine, la discriminazione tra `Code Execution` e `Result Analysis` non e` semantica in astratto ma lessicale e valutativa: "calcola / esegui / produci X" e` `Code Execution`; "X mostra / e` intorno a / e` migliore di Y" e` `Result Analysis`. Questa distinzione, insieme alla gerarchia dei pesi locali e all'ordine dei figli, e` il cuore strutturale che una skill per Claude Code deve replicare per generare rubric conformi al benchmark.
