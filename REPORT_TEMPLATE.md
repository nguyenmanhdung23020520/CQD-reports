# CQD-SHAP Report Notes (Fill-In Template)

## 1) Run Identity (Reproducibility)

- Date/time (UTC): 
- Runtime: Google Colab
- GPU type (T4/A100/...): 
- Python: 
- PyTorch: 
- CUDA available (True/False):
- Repo URL: 
- Git commit (SHA): 
- Branch/tag (e.g. `main` or `v1.0`): 

Commands to capture:

```bash
python --version
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
git rev-parse HEAD
git status --porcelain
pip freeze | sed -n '1,200p'
```

## 2) Data + Model Used

- KG: `Freebase` / `NELL`
- Benchmark: `1` (FB15k-237) / `2` (FB15k-237+H)
- `data_dir` used (actual path):
- `model_path` used (actual path):

Sanity checks:

```bash
ls -la data
ls -la models
test -f evaluation.py && echo "evaluation.py OK"
```

## 3) Experiment Commands (Exact)

Parameters:

- `k`:
- `t_norm`:
- `t_conorm`:
- `split`: `test` / `valid`
- `normalize`: True/False

Main method:

```bash
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method shapley
```

Baselines:

```bash
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method score
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method random
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method first
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method last
```

Optional: restrict to a query type for quick iteration:

```bash
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method shapley --query_type 2p
```

If paths are not found:

```bash
python evaluation.py --kg <Freebase|NELL> --benchmark <1|2> --method shapley --data_dir <...> --model_path <...>
```

## 4) Output Artifacts (What to Collect)

Expected output folder pattern:

- `evaluation_benchmark<1|2>/<KG>/`

Files to attach / archive:

- `*.log`
- `*_necessary.csv`
- `*_sufficient.csv`

Quick list:

```bash
find evaluation_benchmark* -maxdepth 3 -type f | sort
```

## 5) Metrics to Report (Core)

Definitions:

- **MRR**: mean reciprocal rank over targets (filtered ranking).
- **Hits@1**: fraction of targets ranked at position 1 (filtered ranking).

What to summarize (for each method and query type, or `all`):

- Necessary: `mrr_before`, `mrr_after`, `delta_mrr`, `delta_hit_1`
- Sufficient: `mrr_before`, `mrr_after`, `delta_mrr`, `delta_hit_1`
- Runtime: `runtime` mean/median

## 6) Tables/Figures (Minimum Set)

Table A: overall results (per method)

- method | scenario (necessary/sufficient) | MRR before | MRR after | ΔMRR | Hits@1 before | Hits@1 after | ΔHits@1

Figure 1: ΔMRR by method (necessary vs sufficient)

Figure 2: runtime distribution by method

## 7) Notes / Observations

- Any deviations from README defaults:
- Any warnings/errors and fixes applied:
- Any non-determinism observed:

