import os, sys
# Helper: create migrations/__init__.py
path = r"c:\Final yr Project\sarcasm_detect\analyzer\migrations"
os.makedirs(path, exist_ok=True)
open(os.path.join(path, "__init__.py"), "w").close()
print("Created migrations/__init__.py")
