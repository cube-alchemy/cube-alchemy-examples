# Cube Alchemy Examples

A collection of examples and small datasets for demos and data projects.

## Contents

- `kaggle/` - Kaggle (https://www.kaggle.com/) sample datasets
  - `adventureworks/` - AdventureWorks sample data (CSV)
- `synthetic/` - Artificially generated datasets

## Usage

Easily download datasets directly from GitHub using Python:

```python
import pandas as pd

# Download a dataset directly from GitHub
url = "https://raw.githubusercontent.com/cube-alchemy/cube-alchemy-examples/main/kaggle/adventureworks/Source/Sales.csv"
df = pd.read_csv(url, sep='\t') 
```

## Licensing

- Code (scripts, utilities, and example notebooks in this repository) is licensed under the MIT License. See the root [LICENSE](./LICENSE).
- Data: Each dataset has its own license in its directory. For example, `kaggle/adventureworks` CSVs are under LGPL-3.0 (see that folder's `LICENSE`).
