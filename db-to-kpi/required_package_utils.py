import subprocess
import tomllib
from importlib import import_module
from utils.logger import log
from utils.logger import RED, GREEN, WHITE

with open("config.toml", "rb") as CONFIG:
    parsed = tomllib.load(CONFIG)

    def install_packages():
        """
        ## Summary
        > *Warning : This function is **blocking** and generally implies sensible load time.*\n\n
        summary_ installs packages with PIP from ./optional_packages
        by parsing the config.toml's [APP_CONFIG].modules package list.

        TODO
        - add checks on module names to see whether these are within optional_packages
        (if an ill-intentionned user puts a wrong library in the TOML, the code will install the package directly in
        the project...)
        """
        method = parsed["APP_CONFIG"]["install"]["method"]
        print(f"method is equal to {method}")
        if method == "auto":
            installed_all = True
            total_requested = 3
            installed = 0
            install = True

            log("INPUT", "Do you wish to reinstall all modules (y/n) ?")
            res = input("> ")
            match res.lower():
                case "y" | "yes":
                    print()
                case "n" | "no":
                    install = False
                    log(
                        "INFO",
                        "✔  As you wish ! Old installations will be used for this session.",
                    )
            if install:
                for category in parsed["APP_CONFIG"]["layout"].keys():
                    for pckg in parsed["APP_CONFIG"]["layout"][f"{category}"][
                        "modules"
                    ]:
                        try:
                            subprocess.run(
                                args=["pip", "install", f"./optional_packages/{pckg}"],
                                capture_output=True,
                                check=True,
                            )
                            installed += 1
                            log(
                                "INFO",
                                f"{GREEN}+{WHITE} {pckg} Successfully installed.",
                            )

                        except Exception:
                            log("ERROR", f"{RED}+{WHITE}  Installing {pckg} failed")

                if installed_all:
                    log(
                        "INFO",
                        f"✔  Successfully installed all {installed} requested packages !",
                    )
                else:
                    log(
                        "INFO",
                        f"✔  Successfully installed {installed} requested packages (out of {total_requested})",
                    )
                    log(
                        "WARN",
                        f"❌  Failed {total_requested - installed} installations.",
                    )

    def get_installed_modules() -> dict[str, list]:
        main_modules = []
        other_modules = []
        for category in parsed["APP_CONFIG"]["layout"].keys():
            for pckg in parsed["APP_CONFIG"]["layout"][f"{category}"]["modules"]:
                match category:
                    case "highlighted":
                        main_modules.append(import_module(pckg))
                    case "hidden":
                        other_modules.append(import_module(pckg))
                    case _:
                        other_modules.append(import_module(pckg))
        return {"highlighted": main_modules, "hidden": other_modules}
