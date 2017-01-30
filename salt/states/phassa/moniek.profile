if [ -d "$HOME/bin" ] ; then
    export PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/py" ] ; then
    export PYTHONPATH="$HOME/py:$PYTHONPATH"
fi

{% if grains['vagrant'] %}
export DJANGO_SETTINGS_MODULE=vagrantSettingsHack.settings
{% else %}
export DJANGO_SETTINGS_MODULE=kn.settings
{% endif %}
