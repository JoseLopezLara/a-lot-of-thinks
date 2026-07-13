import os
import sys
import tty
import termios
import json

def is_interactive_tty():
    import os
    try:
        # Check if stdin is a tty and AGENT_MODE is not set
        return sys.stdin.isatty() and os.environ.get("AGENT_MODE") != "1"
    except Exception:
        return False

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def select_menu(title, options):
    if not is_interactive_tty():
        print(f"\n{title}")
        for idx, opt in enumerate(options):
            print(f"  {idx + 1}. {opt}")
        while True:
            sys.stdout.write("Selection: ")
            sys.stdout.flush()
            val = sys.stdin.readline().strip()
            if val.isdigit():
                selected = int(val) - 1
                if 0 <= selected < len(options):
                    return selected
            for idx, opt in enumerate(options):
                if opt.lower() == val.lower():
                    return idx
            print("Invalid selection. Please try again.")

    selected_index = 0
    num_options = len(options)
    
    # Hide cursor
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    
    try:
        while True:
            # Render menu
            sys.stdout.write(f"\033[1m{title}\033[0m\n")
            for idx, opt in enumerate(options):
                if idx == selected_index:
                    sys.stdout.write(f" \033[36m❯ {opt}\033[0m\n")
                else:
                    sys.stdout.write(f"   {opt}\n")
            sys.stdout.flush()
            
            # Read key
            key = get_key()
            
            # Move cursor back up (title + options lines)
            sys.stdout.write(f"\033[{num_options + 1}A")
            
            if key == '\x1b[A': # Up arrow
                selected_index = (selected_index - 1) % num_options
            elif key == '\x1b[B': # Down arrow
                selected_index = (selected_index + 1) % num_options
            elif key in ('\r', '\n'): # Enter
                # Clear menu lines before returning
                for _ in range(num_options + 1):
                    sys.stdout.write("\033[K\n")
                sys.stdout.write(f"\033[{num_options + 1}A")
                sys.stdout.flush()
                break
    finally:
        # Show cursor again
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
        
    return selected_index

def text_input(prompt):
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    val = input(prompt).strip()
    return val

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Configure selections for the openapi-generator.")
    parser.add_argument("--version", type=str, help="API version, e.g., v1")
    parser.add_argument("--domain", type=str, help="API domain, e.g., users")
    parser.add_argument("--endpoint", type=str, help="Endpoint filename, e.g., get-users")
    parser.add_argument("--route-type", type=str, choices=["simulated", "empty", "none"], help="Route generation option")
    parser.add_argument("--language", type=str, help="Language(s) for generated documentation (e.g., spanish,english or es,en)")
    
    args = parser.parse_args()

    # Detect api-first root dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", "..", ".."))
    openapi_dir = os.path.join(root_dir, "openapi")
    
    if not os.path.exists(openapi_dir):
        print(f"Error: Could not find 'openapi' directory at {openapi_dir}", file=sys.stderr)
        sys.exit(1)

    # Check if all core arguments are provided to bypass interaction
    if args.version and args.domain and args.endpoint and args.route_type:
        version = args.version.lower()
        if not version.startswith("v"):
            version = "v" + version
        domain = args.domain.lower()
        endpoint = args.endpoint.lower()
        if endpoint.endswith(".yaml") or endpoint.endswith(".yml"):
            endpoint = endpoint.split(".")[0]
        route_type = args.route_type.lower()
        
        # Process languages
        raw_langs = [l.strip().lower() for l in args.language.split(",")] if args.language else ["english"]
        lang_mapping = {
            "spanish": "es", "español": "es", "es": "es",
            "english": "en", "inglés": "en", "ingles": "en", "en": "en"
        }
        selected_langs = []
        for rl in raw_langs:
            mapped = lang_mapping.get(rl)
            if mapped and mapped not in selected_langs:
                selected_langs.append(mapped)
        if not selected_langs:
            selected_langs = ["en"]
            
        # Ensure version directories exist
        v_openapi_path = os.path.join(openapi_dir, version)
        os.makedirs(v_openapi_path, exist_ok=True)
    else:
        # 1. API Version selection
        existing_versions = []
        if os.path.exists(openapi_dir):
            existing_versions = [
                d for d in os.listdir(openapi_dir)
                if os.path.isdir(os.path.join(openapi_dir, d)) and d.startswith("v")
            ]
        existing_versions.sort()

        version_options = existing_versions + ["Create a new version..."]
        v_idx = select_menu("Select the target API version:", version_options)
        
        if version_options[v_idx] == "Create a new version...":
            version = text_input("Enter new version name (e.g. v2): ").strip().lower()
            if not version.startswith("v"):
                version = "v" + version
        else:
            version = version_options[v_idx]

        # Ensure version directories exist
        v_openapi_path = os.path.join(openapi_dir, version)
        os.makedirs(v_openapi_path, exist_ok=True)

        # 2. Domain selection
        existing_domains = []
        # Check subdirectories across language dirs or directly under v_openapi_path
        search_paths = [v_openapi_path]
        for l in ("es", "en"):
            lp = os.path.join(v_openapi_path, l)
            if os.path.exists(lp) and os.path.isdir(lp):
                search_paths.append(lp)
                
        for path in search_paths:
            if os.path.exists(path):
                for d in os.listdir(path):
                    if os.path.isdir(os.path.join(path, d)) and d not in ("es", "en", "welcome-example", "system") and d not in existing_domains:
                        existing_domains.append(d)
        existing_domains.sort()

        domain_options = existing_domains + ["Create a new domain..."]
        d_idx = select_menu(f"Select the target Domain (in {version}):", domain_options)
        
        if domain_options[d_idx] == "Create a new domain...":
            domain = text_input("Enter new domain name (e.g. users): ").strip().lower()
        else:
            domain = domain_options[d_idx]

        # 3. Endpoint name
        endpoint = text_input("Enter endpoint filename (e.g. get-users): ").strip().lower()
        if endpoint.endswith(".yaml") or endpoint.endswith(".yml"):
            endpoint = endpoint.split(".")[0]

        # 4. Route type
        route_options = [
            "Simulated (FastAPI route with mock data)",
            "Empty (FastAPI route skeleton)",
            "None (only OpenAPI YAML spec)"
        ]
        r_idx = select_menu("Select Route Code Generation option:", route_options)
        
        route_types = ["simulated", "empty", "none"]
        route_type = route_types[r_idx]

        # 5. Language
        language_options = [
            "Spanish (Español)",
            "English (Inglés)",
            "Both (Ambos)"
        ]
        lang_idx = select_menu("Select target language(s) for documentation:", language_options)
        if lang_idx == 0:
            selected_langs = ["es"]
        elif lang_idx == 1:
            selected_langs = ["en"]
        else:
            selected_langs = ["es", "en"]

    result = {
        "version": version,
        "domain": domain,
        "endpoint_name": endpoint,
        "route_type": route_type,
        "languages": selected_langs
    }

    # Save to a scratch configuration file
    scratch_dir = os.path.join(script_dir, "..", "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    config_path = os.path.join(scratch_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(result, f, indent=2)

    # Touch app/main.py to trigger Uvicorn hot-reload
    main_py_path = os.path.join(root_dir, "app", "main.py")
    if os.path.exists(main_py_path):
        try:
            os.utime(main_py_path, None)
        except Exception as e:
            print(f"Warning: Could not touch app/main.py: {e}", file=sys.stderr)

    # Print results to stdout
    print("\n--- SELECTIONS ---")
    print(f"Version:      {version}")
    print(f"Domain:       {domain}")
    print(f"Endpoint:     {endpoint}")
    print(f"Route Type:   {route_type}")
    print(f"Languages:    {', '.join(selected_langs)}")
    print(f"Config Saved: {config_path}")
    print("------------------\n")

if __name__ == "__main__":
    main()
