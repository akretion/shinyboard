source bin/activate &&
cd db-to-kpi &&
msgfmt -o i18n/locales/fr/LC_MESSAGES/base.mo i18n/locales/fr/LC_MESSAGES/base.po &&
echo "THINK TO RENAME .env_sample to .env" &&
shiny run app.py --reload --launch-browser