

import platform


def aria2_install_hint() -> str:  # type: ignore[reportUnusedFunction]
    match platform.system():
        case "Linux":
            return "sudo apt install aria2  (Debian/Ubuntu)  |  sudo pacman -S aria2  (Arch)  |  sudo dnf install aria2  (Fedora)"
        case "Darwin":
            return "brew install aria2"
        case "Windows":
            return "winget install aria2.aria2  |  choco install aria2"
        case _:
            return "see https://aria2.github.io/ for install instructions"
