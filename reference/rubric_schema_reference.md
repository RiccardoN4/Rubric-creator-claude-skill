# PaperBench Rubric Schema Reference

Questo documento riporta solo ciò che ho trovato nel codice del repository.

## File Ispezionati

### Rubric input

- `paperbench/rubric/tasks.py`
- `paperbench/rubric/utils.py`

### Judge / loading / scoring

- `paperbench/grade.py`
- `paperbench/judge/base.py`
- `paperbench/judge/simple.py`
- `paperbench/judge/graded_task_node.py`
- `paperbench/judge/create_judge.py`
- `paperbench/judge/constants.py`
- `paperbench/judge/token_usage.py`
- `paperbench/judge/utils.py`
- `paperbench/judge/dummyrandom.py`
- `paperbench/judge/judge_eval/evaluate.py`
- `paperbench/judge/judge_eval/registry.py`
- `paperbench/scripts/run_judge.py`
- `paperbench/scripts/run_judge_eval.py`

### Test / fixture / esempi serializzati

- `tests/unit/test_rubrics_load.py`
- `tests/integration/test_run_agent.py`
- `data/judge_eval/all-in-one/0/grading/expected_result.json`
- `data/judge_eval/pinn/0/grading/expected_result.json`
- `data/judge_eval/rice/0/grading/expected_result.json`
- `data/judge_eval/semantic-self-consistency/0/grading/expected_result.json`
- `data/judge_eval/stay-on-topic-with-classifier-free-guidance/0/grading/expected_result.json`

## 1. Struttura Dati Canonica Della Rubric

L’unica struttura dati che definisce il formato della rubric input è `TaskNode` in `paperbench/rubric/tasks.py`.

```python
@dataclass(frozen=True, kw_only=True)
class TaskNode:
    id: str
    requirements: str
    weight: int
    sub_tasks: Sequence[Self] = field(default_factory=list)
    task_category: str | None = None
    finegrained_task_category: str | None = None
```

### Campi

| Campo | Tipo annotato | Obbligatorio nel JSON? | Default dataclass | Note runtime |
| --- | --- | --- | --- | --- |
| `id` | `str` | Sì | nessuno | `from_dict` lo legge con `data["id"]`; non c’è type-check runtime esplicito. |
| `requirements` | `str` | Sì | nessuno | `from_dict` lo legge con `data["requirements"]`; non c’è type-check runtime esplicito. |
| `weight` | `int` | Sì | nessuno | `__post_init__` accetta in pratica `int` o `float`; rifiuta valori non numerici o negativi. |
| `sub_tasks` | `Sequence[TaskNode]` | Sì | `[]` se costruito a mano; nel JSON è comunque richiesto da `from_dict` | Ogni nodo deve avere `sub_tasks`; per le foglie deve essere `[]`. |
| `task_category` | `str \| None` | No in `from_dict`, ma di fatto sì per le foglie | `None` | Se il nodo è foglia, `__post_init__` richiede un valore non nullo e valido. Se il nodo è interno, deve essere `None`/assente. |
| `finegrained_task_category` | `str \| None` | No | `None` | Se presente, deve appartenere all’enum valido. Il judge normale non la usa direttamente, salvo il preprocessing `resources_provided`. |

### Campi richiesti da `TaskNode.from_dict`

`TaskNode.from_dict` legge obbligatoriamente:

- `id`
- `requirements`
- `weight`
- `sub_tasks`

e legge opzionalmente:

- `task_category` via `data.get("task_category")`
- `finegrained_task_category` via `data.get("finegrained_task_category")`

Se manca uno dei 4 campi obbligatori, l’errore è:

```text
ValueError("Missing required field in node '<node_id>'")
```

### Osservazione importante su chiavi extra

`TaskNode.from_dict` non rifiuta chiavi extra: semplicemente le ignora.

Quindi il codice **non impone** un vincolo `additionalProperties: false`.

### Osservazione importante su `to_dict()`

`TaskNode.to_dict()` serializza sempre anche:

- `task_category`
- `finegrained_task_category`

anche quando valgono `None`.

## 2. Naming Conventions Esatte

### `task_category`

Valori esatti definiti in `VALID_TASK_CATEGORIES`:

- `"Code Development"`
- `"Code Execution"`
- `"Result Analysis"`
- `"Subtree"`

Nota importante:

- Il commento nel codice dice che `"Subtree"` è “Used dynamically for experimental non-leaf grading”.
- Tuttavia, `TaskNode.__post_init__` vieta `task_category` sui nodi interni.
- Quindi `"Subtree"` è tecnicamente valido **solo su un nodo foglia**.
- Questo è esattamente come viene usato da `SimpleJudge.grade_subtree()`: crea un *leaf shim* con `task_category="Subtree"`.
- Nelle rubric JSON del dataset non ho visto `"Subtree"` come categoria della rubric input; è un valore speciale usato dal judge.

### `finegrained_task_category`

Valori esatti definiti in `VALID_FINEGRAINED_TASK_CATEGORIES`:

- `"Environment & Infrastructure Setup"`
- `"Dataset and Model Acquisition"`
- `"Data Processing & Preparation"`
- `"Method Implementation"`
- `"Experimental Setup"`
- `"Evaluation, Metrics & Benchmarking"`
- `"Logging, Analysis & Presentation"`

## 3. Logica Di Validazione Applicata Alla Rubric

La validazione principale è in `TaskNode.__post_init__`.

### Vincoli espliciti

1. `weight` deve essere numerico:

```python
if not isinstance(self.weight, (int, float)):
    raise ValueError("Weight must be a number.")
```

2. `weight` deve essere non negativo:

```python
if self.weight < 0:
    raise ValueError("Weight must be non-negative.")
```

3. Se `task_category` è presente, deve appartenere all’enum valido:

```python
if self.task_category and self.task_category not in VALID_TASK_CATEGORIES:
    raise ValueError(f"Invalid task category: {self.task_category}")
```

4. Se `finegrained_task_category` è presente, deve appartenere all’enum valido:

```python
if (
    self.finegrained_task_category
    and self.finegrained_task_category not in VALID_FINEGRAINED_TASK_CATEGORIES
):
    raise ValueError(f"Invalid finegrained task category: {self.finegrained_task_category}")
```

5. Un nodo interno non può avere `task_category`:

```python
if not self.is_leaf() and self.task_category:
    raise ValueError(f"Non-leaf node '{self.id}' cannot have a task category.")
```

6. Una foglia deve avere `task_category`:

```python
if self.is_leaf() and not self.task_category:
    raise ValueError(f"Leaf node '{self.id}' doesn't have a task category.")
```

### Cose che il codice non valida esplicitamente

Questi vincoli **non sono enforced** direttamente dal loader:

- unicità di `id`
- tipo runtime di `id` e `requirements`
- assenza di chiavi extra
- presenza/assenza di `finegrained_task_category` sui nodi interni

## 4. Vincoli Impliciti Scoperti Nel Codice

Questi non sono tutti enforced con `raise`, ma il codice li assume chiaramente.

### 4.1 `sub_tasks` è obbligatorio su ogni nodo

`TaskNode.from_dict` usa `data["sub_tasks"]`, quindi:

- un nodo foglia valido deve avere `"sub_tasks": []`
- omettere `sub_tasks` non è supportato

### 4.2 L’ordine dei figli è semanticamente significativo

`TaskNode.get_prior_nodes()` costruisce il contesto di grading usando:

- gli antenati
- i fratelli precedenti
- i fratelli precedenti degli antenati

`SimpleJudge._construct_grade_leaf_messages()` passa questo contesto al judge come `preceding_criteria`.

Quindi:

- l’ordine dei figli non è puramente cosmetico
- cambiare l’ordine cambia il contesto fornito al judge

### 4.3 Gli `id` dovrebbero essere unici, anche se il loader non lo enforce

Il codice non lancia errore sui duplicati, ma:

- esiste `TaskNode.get_descendants_with_duplicate_ids()`
- `find(node_id)` restituisce il primo match DFS
- il judge usa `task.id` per file di log e lookup
- `judge_eval` usa `expected_result.find(task.id)`

Quindi i duplicati non sono formalmente vietati dal loader, ma rendono il comportamento ambiguo. Il codebase assume di fatto che gli `id` identificano nodi singoli.

### 4.4 `finegrained_task_category` è quasi solo metadata di preprocessing

Nel flusso di grading normale:

- `SimpleJudge` non usa `finegrained_task_category` nelle decisioni di grading foglia per foglia
- l’unico uso operativo trovato è `TaskNode.resources_provided()`, che azzera il peso delle foglie con
  `"Dataset and Model Acquisition"`

### 4.5 La serializzazione del tree graded perde `finegrained_task_category`

`GradedTaskNode.to_dict()` **non** serializza `finegrained_task_category`.

Quindi:

- la rubric input può contenere `finegrained_task_category`
- `grade.json` / `grader_output.json` / `expected_result.json` non la preservano

Questo è importante se vuoi confrontare rubric input vs rubric graded.

### 4.6 `TaskNode.from_dict()` non è polimorfico

Anche se è definito come `@classmethod`, dentro costruisce esplicitamente `TaskNode(...)` e non `cls(...)`.

Quindi il parsing della rubric input produce sempre `TaskNode`, non sottoclassi.

### 4.7 `prune_to_depth()` sembra fragile sui nodi interni

Il metodo `prune_to_depth()` dichiara di creare una foglia quando tronca un sottoalbero, ma se tronca un nodo interno con `task_category=None`, costruisce:

```python
TaskNode(..., sub_tasks=[], task_category=None, ...)
```

che poi viola la regola “leaf node must have task_category”.

Non ho trovato test o chiamate rilevanti a questo metodo nel flusso standard di grading. Quindi segnalo l’ambiguità, ma non posso dire dal codice se sia un bug latente o codice non usato.

## 5. Come PaperBench Carica E Parsa La Rubric JSON

Il flusso principale è in `paperbench/grade.py`.

### Loading

```python
with open(rubric_path, "r") as f:
    task_tree = TaskNode.from_dict(json.load(f))
```

Quindi il formato canonico atteso dal codebase per la rubric input è esattamente quello di `TaskNode.from_dict`.

### Trasformazioni opzionali applicate prima del judge

#### `code_only=True`

```python
task_tree = task_tree.code_only() or task_tree.set_task_category(
    "Code Development"
).set_sub_tasks([])
```

`TaskNode.code_only()` usa:

```python
reduce_to_category(self, "Code Development")
```

Effetto:

- rimuove tutte le foglie che non hanno `task_category == "Code Development"`
- mantiene i nodi interni solo se hanno ancora almeno un figlio dopo il pruning
- se il pruning elimina tutto, `run_judge()` trasforma il root in una foglia `"Code Development"`

#### `resources_provided=True`

```python
task_tree = task_tree.resources_provided()
```

`TaskNode.resources_provided()` usa:

```python
zero_weight_by_category(self, finegrained_task_category="Dataset and Model Acquisition")
```

Effetto:

- le foglie con `finegrained_task_category == "Dataset and Model Acquisition"` ricevono `weight = 0`
- la struttura del tree non cambia

## 6. Quali Campi Della Rubric Il Judge Usa Davvero

### Campi usati direttamente dal grading

`SimpleJudge` usa direttamente:

- `id`
- `requirements`
- `weight`
- `sub_tasks`
- `task_category`

### Campo usato solo nel preprocessing

- `finegrained_task_category`
  - usato solo da `resources_provided()` / `zero_weight_by_category()`
  - non usato da `SimpleJudge.grade_leaf()` per decidere il voto

### Dove `task_category` conta nel judge

`task_category` controlla:

1. La domanda di grading mostrata nel prompt, via `TASK_CATEGORY_QUESTIONS`
2. La finestra di contesto disponibile (`_get_available_context`)
3. Il tipo di file considerati rilevanti (`_get_whitelisted_files`)
4. Se includere `reproduce.log` nel prompt
5. Il fallback speciale dei nodi `Result Analysis` quando `reproduce.sh` non ha toccato file
6. Il path di grading continuo per i nodi `"Subtree"`

### Assunzioni implicite del `SimpleJudge` sul contenuto dei file

In `SimpleJudge._get_whitelisted_files()` il judge assume queste famiglie di file rilevanti:

- Documentazione: `.md`, `.txt`, `.rst`
- Codice/config: `.py`, `.R`, `.Rmd`, `.m`, `.jl`, `.c`, `.h`, `.cpp`, `.hpp`, `.cc`, `.cxx`, `.hxx`, `.java`, `.js`, `.ts`, `.scala`, `.go`, `.rs`, `.sh`, `.config`, `.cfg`, `.json`, `.yaml`, `.yml`, `.toml`, `.ini`
- Tabelle / risultati: `.csv`, `.tsv`, `.psv`, `.json`, `.jsonl`, `.html`, `.xml`, `.yaml`, `.yml`, `.toml`, `.arff`, `.tex`, `.svm`, `.libsvm`

Per categoria:

- `Code Development` e `Code Execution`: docs + code/config
- `Result Analysis`: docs + tabelle; inoltre i file non-doc vengono tenuti solo se il loro `mtime` è successivo all’avvio della riproduzione
- `Subtree`: docs + code/config + tabelle

Questo non cambia lo schema JSON della rubric, ma è una forte assunzione operativa del judge su cosa costituisce “evidenza” per ciascun `task_category`.

### Mapping esatto usato nei prompt

`TASK_CATEGORY_QUESTIONS`:

- `"Code Development"` ->
  `"Does the code in the submission contain a correct implementation of this? ..."`
- `"Code Execution"` ->
  `"Does running the reproduce.sh script lead to this being successfully executed?"`
- `"Result Analysis"` ->
  `"Did the reproduce.sh script execution produce evidence that agrees with these results?"`
- `"Subtree"` ->
  `"What is the weighted score of all the criteria in the subtree?"`

## 7. Come Il Judge Filtra I Nodi Per Tipo

### 7.1 Filtro `Code Development` per PaperBench-CodeOnly

Funzione: `reduce_to_category(node, "Code Development")`

Regole:

- se il nodo è foglia:
  - viene mantenuto solo se `node.task_category == "Code Development"`
- se il nodo è interno:
  - i figli vengono filtrati ricorsivamente
  - il nodo viene mantenuto solo se rimane almeno un figlio

### 7.2 Nessun filtro simmetrico built-in per `Code Execution` o `Result Analysis`

Nel codebase non ho trovato helper equivalenti a `code_only()` per:

- solo `"Code Execution"`
- solo `"Result Analysis"`

Esiste solo `code_only()`.

### 7.3 Stratificazione delle metriche judge_eval

In `paperbench/judge/judge_eval/evaluate.py`, le metriche per categoria usano:

```python
cat = task.task_category
```

Quindi la stratificazione judge_eval dipende esattamente dai valori stringa di `task_category`.

## 8. Formula Esatta Di Calcolo Dello Score

### Score delle foglie

Per il judge standard:

- `SimpleJudge.grade_leaf()` usa un parser Pydantic con `score: int`
- `_parse_model_response()` rifiuta score fuori da `[0, 1]`

Quindi, per le foglie normali:

- score effettivamente atteso: `0` oppure `1`

Per il caso speciale `"Subtree"`:

- `SimpleJudge.grade_subtree()` crea una foglia sintetica con `task_category="Subtree"`
- il parser usato è `ParsedJudgeResponseFloat`
- `_parse_model_response()` accetta qualunque float in `[0, 1]`

Quindi, per `"Subtree"`:

- score effettivamente atteso: qualsiasi numero reale tra `0` e `1`

### Propagazione bottom-up

La funzione canonica è `score_from_children()` in `paperbench/judge/graded_task_node.py`:

```python
total_weight = sum(child.weight for child in children)
if total_weight == 0:
    return 0.0
weighted_score = sum(child.score * child.weight for child in children) / total_weight
return weighted_score
```

### Pseudocodice esatto del grading

```text
load rubric JSON
task_tree = TaskNode.from_dict(json)

if code_only:
    task_tree = task_tree.code_only()
    if task_tree is None:
        task_tree = original_root
        task_tree = task_tree.set_task_category("Code Development").set_sub_tasks([])

if resources_provided:
    task_tree = task_tree.resources_provided()

async grade(task, current_depth):
    if current_depth >= max_depth and task is not leaf:
        return grade_subtree(task)   # continuous score in [0, 1]

    if task is leaf:
        return grade_leaf(task)      # normal leaves: 0 or 1

    graded_children = [grade(child, current_depth + 1) for child in task.sub_tasks]
    score = weighted_average(graded_children, child.weight)

    return GradedTaskNode(
        id=task.id,
        requirements=task.requirements,
        weight=task.weight,
        sub_tasks=graded_children,
        score=score,
        valid_score=True,
        explanation="Aggregated score from sub-tasks.",
        judge_metadata=None,
    )

weighted_average(children):
    total_weight = sum(child.weight for child in children)
    if total_weight == 0:
        return 0.0
    return sum(child.score * child.weight for child in children) / total_weight
```

### Nota importante sulla semantica del peso

Il `weight` di un nodo:

- **non** contribuisce al proprio score interno
- contribuisce solo a come il parent media i figli

Quindi i pesi sono locali tra fratelli.

## 9. Esempi Concreti Di Nodi Validi E Invalidi

### Esempio valido: foglia

```json
{
  "id": "leaf-1",
  "requirements": "The optimizer has been implemented.",
  "weight": 1,
  "sub_tasks": [],
  "task_category": "Code Development",
  "finegrained_task_category": "Method Implementation"
}
```

Perché è valido:

- ha tutti i campi richiesti da `from_dict`
- `sub_tasks` è vuoto
- quindi è una foglia
- ha `task_category` non nullo e valido
- `weight >= 0`

### Esempio valido: nodo interno

```json
{
  "id": "internal-1",
  "requirements": "The training pipeline has been implemented.",
  "weight": 2,
  "sub_tasks": [
    {
      "id": "leaf-1",
      "requirements": "The optimizer has been implemented.",
      "weight": 1,
      "sub_tasks": [],
      "task_category": "Code Development"
    }
  ]
}
```

Perché è valido:

- ha `sub_tasks` non vuoto
- essendo interno, `task_category` è assente/null
- il figlio foglia ha `task_category` valido

### Esempio invalido: foglia senza `task_category`

```json
{
  "id": "bad-leaf",
  "requirements": "Missing task category.",
  "weight": 1,
  "sub_tasks": []
}
```

Errore atteso:

```text
ValueError("Leaf node 'bad-leaf' doesn't have a task category.")
```

### Esempio invalido: nodo interno con `task_category`

```json
{
  "id": "bad-internal",
  "requirements": "This node has children.",
  "weight": 1,
  "sub_tasks": [
    {
      "id": "leaf-1",
      "requirements": "Child",
      "weight": 1,
      "sub_tasks": [],
      "task_category": "Code Development"
    }
  ],
  "task_category": "Code Development"
}
```

Errore atteso:

```text
ValueError("Non-leaf node 'bad-internal' cannot have a task category.")
```

### Esempio invalido: peso negativo

```json
{
  "id": "bad-weight",
  "requirements": "Negative weight.",
  "weight": -1,
  "sub_tasks": [],
  "task_category": "Code Development"
}
```

Errore atteso:

```text
ValueError("Weight must be non-negative.")
```

### Esempio invalido: `finegrained_task_category` sconosciuto

```json
{
  "id": "bad-fine",
  "requirements": "Bad finegrained category.",
  "weight": 1,
  "sub_tasks": [],
  "task_category": "Code Development",
  "finegrained_task_category": "Unknown"
}
```

Errore atteso:

```text
ValueError("Invalid finegrained task category: Unknown")
```

## 10. Strutture Derivate Trovate Nel Judge

Queste non definiscono la rubric input, ma sono rilevanti per capire fixture e output.

### `GradedTaskNode`

Definita in `paperbench/judge/graded_task_node.py`.

Estende `TaskNode` aggiungendo:

- `score: float = 0.0`
- `valid_score: bool = False`
- `explanation: str = "not yet graded"`
- `judge_metadata: dict[str, Any] | None = None`

`GradedTaskNode.to_dict()` serializza:

- `id`
- `requirements`
- `weight`
- `score`
- `valid_score`
- `task_category`
- `explanation`
- `judge_metadata`
- `sub_tasks`

e **non** serializza `finegrained_task_category`.

### `ParsedJudgeResponseFloat` / `ParsedJudgeResponseInt`

Definite in `paperbench/judge/simple.py`.

Servono solo a parsare la risposta del modello judge:

```python
class ParsedJudgeResponseFloat(BaseModel):
    valid_score: bool
    score: float
    explanation: str

class ParsedJudgeResponseInt(BaseModel):
    valid_score: bool
    score: int
    explanation: str
```

Non definiscono la rubric JSON input.

## 11. Test, Fixture E “Schema” Trovati Nel Repo

### Test diretti sul parsing rubric

`tests/unit/test_rubrics_load.py`:

- carica ogni `data/papers/*/rubric.json`
- esegue `TaskNode.from_dict(data)`
- verifica che il risultato sia un `TaskNode`

### Test sull’output graded

`tests/integration/test_run_agent.py`:

- legge `grade.json`
- estrae `paperbench_result.judge_output.graded_task_tree`
- verifica che `GradedTaskNode.from_dict(graded_task_tree)` non fallisca

### Fixture judge_eval

Le fixture sotto `data/judge_eval/*/grading/expected_result.json` sono serializzazioni di `GradedTaskNode`, non della rubric input originale.

Quindi:

- sono utili per capire il formato dell’albero graded
- non descrivono completamente lo schema della rubric input, perché manca `finegrained_task_category`

### Schema JSON formale nel repo

Non ho trovato:

- file `*.schema.json`
- JSON Schema formale della rubric
- Pydantic model dedicato al parsing della rubric input

Lo schema input è definito di fatto dalla combinazione di:

- `TaskNode` dataclass
- `TaskNode.from_dict`
- `TaskNode.__post_init__`
