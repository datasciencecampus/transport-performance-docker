"""src/run.py."""

import os

output_dir = os.path.join(os.getcwd(), "data", "outputs")

os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "test.txt"), "w") as f:
    pass
