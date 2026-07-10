import os
import sys
import tty
import termios
import json

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
    # Detect api-first root dir
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
    openapi_dir = os.path.join(root_dir, "openapi")
    
    if not os.path.exists(openapi_dir):
        print(f"Error: Could not find 'openapi' directory at {openapi_dir}", file=sys.stderr)
        sys.exit(1)

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
    if os.path.exists(v_openapi_path):
        existing_domains = [
            d for d in os.listdir(v_openapi_path)
            if os.path.isdir(os.path.join(v_openapi_path, d))
        ]
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

    result = {
        "version": version,
        "domain": domain,
        "endpoint_name": endpoint,
        "route_type": route_type
    }

    # Save to a scratch configuration file
    scratch_dir = os.path.join(script_dir, "..", "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    config_path = os.path.join(scratch_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(result, f, indent=2)

    # Print results to stdout
    print("\n--- SELECTIONS ---")
    print(f"Version:      {version}")
    print(f"Domain:       {domain}")
    print(f"Endpoint:     {endpoint}")
    print(f"Route Type:   {route_type}")
    print(f"Config Saved: {config_path}")
    print("------------------\n")

if __name__ == "__main__":
    main()
