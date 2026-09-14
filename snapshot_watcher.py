from pathlib import Path
import time


PROJECT_DIR = Path(__file__).parent
OUTPUT_FILE = PROJECT_DIR / "codebase_snapshot.txt"

EXCLUDED_FILES = {
    "snapshot_watcher.py",
}


def get_python_files():
    return sorted(
        file
        for file in PROJECT_DIR.rglob("*.py")
        if file.name not in EXCLUDED_FILES
        and "__pycache__" not in file.parts
        and ".venv" not in file.parts
        and "venv" not in file.parts
    )


def build_snapshot():
    python_files = get_python_files()

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for file in python_files:
            relative_path = file.relative_to(PROJECT_DIR)

            output.write("=" * 80 + "\n")
            output.write(f"FILE: {relative_path}\n")
            output.write("=" * 80 + "\n\n")

            output.write(file.read_text(encoding="utf-8"))

            if not file.read_text(encoding="utf-8").endswith("\n"):
                output.write("\n")

            output.write("\n")

    print("Updated codebase_snapshot.txt")


def get_modification_state():
    return {
        file: file.stat().st_mtime_ns
        for file in get_python_files()
    }


def main():
    build_snapshot()
    previous_state = get_modification_state()

    print("Watching project for Python file changes...")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)

            current_state = get_modification_state()

            if current_state != previous_state:
                build_snapshot()
                previous_state = current_state

    except KeyboardInterrupt:
        print("\nSnapshot watcher stopped.")


if __name__ == "__main__":
    main()