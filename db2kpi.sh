
launch="";
reload="";
install="";

while [ $# -gt 0 ];
do
    case $1 in 

    -h | --help)
    echo "-h | --help       - gives help about db2kpi's commands"
    echo "-r | --reload   - useful for devs. makes the app reload on source code changes"
    echo "-a | --activate - activates the virtual environment db-to-kpi is nested in before launching the app"
    echo "-o | --open     - opens the browser on app startup"
    exit 1;
    ;;

    -a | --activate)
        source bin/activate
        ;;

    -r | --reload)
        reload="--reload"
        ;;

    -o | --open)
        launch="--launch-browser"
        ;;
    esac
    shift
done;

$install &&
cd db-to-kpi &&
msgfmt -o i18n/locales/fr/LC_MESSAGES/base.mo i18n/locales/fr/LC_MESSAGES/base.po &&
echo "THINK TO RENAME .env_sample to .env" &&
shiny run app.py $launch $reload