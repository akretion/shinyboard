import subprocess
import tomllib
from importlib import import_module

with open("config.toml", "rb") as CONFIG:
    parsed = tomllib.load(CONFIG)

    def install_packages():
        """
        ## Summary
        > *Warning : This function is **blocking** and generally implies sensible load time.*\n\n
        summary_ installs packages with PIP from ./optionnal_packages
        by parsing the config.toml's [APP_CONFIG].modules package list.

        TODO
        - add checks on module names to see whether these are within optionnal_packages
        (if an ill-intentionned user puts a wrong library in the TOML, the code will install the package directly in
        the project...)
        """
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

    def get_installed_modules():
        # pretty much useless if called before install_packages()

        modules = []

        for pckg in parsed["APP_CONFIG"]["modules"]:
            modules.append(import_module(pckg))

        return modules
