import subprocess
import tomllib

with open("config.toml", "rb") as CONFIG:
    parsed = tomllib.load(CONFIG)

    def install_packages():
        for pckg in parsed["APP_CONFIG"]["modules"]:
            try:
                RED = "\u001b[31m"
                GREEN = "\u001b[32m"
                CYAN = "\u001b[36m"
                WHITE = "\u001b[37m"

                print(f"{CYAN}INFO{WHITE} : installing {pckg}, delegating to PIP...")
                subprocess.run(
                    args=["pip", "install", f"./optionnal_packages/{pckg}"],
                    capture_output=True,
                    check=True,
                )
                print(f"{GREEN}Success !{WHITE}")

            except Exception:
                print(f"{RED}ERROR{WHITE} : importing {pckg} failed")
