import importlib
import sys

# List of required modules
required_modules = [
    "streamlit",
    "bcrypt",
    "plotly",
    "reportlab",
    "arabic_reshaper",
    "bidi",
    "pandas"
]

def check_imports():
    missing_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("The following modules are missing:")
        for module in missing_modules:
            print(f"- {module}")
        print("\nPlease install the missing modules using the following command:")
        print("pip install " + " ".join(missing_modules))
        sys.exit(1)

if __name__ == "__main__":
    check_imports()