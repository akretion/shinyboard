

# ShinyBoard

- [ShinyBoard](#shinyboard)
  - [Requirements](#requirements)
  - [Launching the app 🚀](#launching-the-app-)
  - [Installing Packages 📦](#installing-packages-)
    - [Tips 📌](#tips-)
    - [Manual Install ⚙️](#manual-install-️)
    - [Automatic Install ⚡](#automatic-install-)


## Requirements

## Launching the app 🚀
```bash
#
cd shinyboard
./db2kpi.sh --open # opens the browser automatically
```
> and the app is running !
use this command if you need help on the available options (look at them, they can be useful)

```bash
./db2kpi.sh --help
```


## Installing Packages 📦
- The app is supposed to be, when just installed, in its most barebone state : nothing is installed by default. You decide what's needed and install it whenever, which allows you to make **your** version of the app by installing what **you** want.
A module in our application is an unit of functionnality (represented by one or more dedicated pages).
There are 2 ways to install packages : manually and automatically. By default it set to manual, (set in `shinyboard/db-to-kpi/config.toml` at the top of the `[APP_CONFIG]` section by the install variable) Here are the two ways, explained

**IMPORTANT** : do **NOT** forget to activate your virtual environment while doing any of the commands listed later, using

```bash
cd shinyboard
source bin/activate
```

### Tips 📌
> They work no matter the install method !

1. If your app is running while installing packages, **changes won't take effect** unless you restart it completely

2. By opening `shinyboard/db-to-kpi/config.toml`, and looking under the `[APP.CONFIG]` section, you can see two sub-sections
- [APP_CONFIG.highlighted]
- [APP_CONFIG.hidden]

They then each contain an array named "modules".
These are the ways the app knows where to put each module's page in the UI.
- The module pages in the **highlighted** category are the **first things** you see in the UI, at the **very top of the navbar**
(the **first listed package** becomes the **landing page**)
- The ones in the **hidden** category will be at the top, **rightmost side of the UI**, under a dropdown list (called "Apps")

> It is important to note that **packages** listed in `config.toml` **are case sensitive** and should not be mispelled, else
> **errors will be thrown**

3. You can **list packages** simply by executing
```bash
 # you need to be at ./shinyboard/db-to-kpi/optional_packages/ for this to work
ls .
```

4. you can look at a **package's details** using PIP's `pip show`
```bash
pip show package_name
```

### Manual Install ⚙️

Since packages are local PIP packages all located in shinyboard/db-to-kpi/optional_packages/, you need to change directory to
`./shinyboard/db-to-kpi/optional_packages/` and to install them using PIP

```bash
cd ./shinyboard/db-to-kpi/optional_packages/
pip install ./(package_name)
```

you can also install multiple at once this way :

```bash
cd ./shinyboard/db-to-kpi/optional_packages/
pip install ./(package1) (package2) (package...) # space is the separator
```

And that's it ! Your packages are now installed and ready to use in your shiny app.

### Automatic Install ⚡

- You need to choose the packages you want install and write them in `config.toml` first (list them using the third bullet point in [###Tips])
- Then, still in `config.toml`, you need to change the install variable (under the [APP_CONFIG] section) to "auto"
- finally, you can run the app :

```bash
# change directory to be inside shinyboard/
db2kpi.sh --open
```
Done ! the app should be running.
