clean_cache:
	find . -type d \( -name "__pycache__" -o -name ".ipynb_checkpoints" -o -name "*_cache" \) -exec rm -rf {} +