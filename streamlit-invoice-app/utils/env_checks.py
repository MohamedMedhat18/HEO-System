def check_required_modules():
    required_modules = [
        "streamlit",
        "bcrypt",
        "plotly",
        "reportlab",
        "arabic_reshaper",
        "bidi",
        "pandas"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("The following required modules are missing:")
        for module in missing_modules:
            print(f"- {module}")
        print("\nPlease install the missing modules using the following command:")
        print("pip install " + " ".join(missing_modules))
    else:
        print("All required modules are installed.")

if __name__ == "__main__":
    check_required_modules()