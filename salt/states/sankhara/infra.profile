if [ -d "$HOME/bin" ] ; then
    export PATH="$HOME/bin:$PATH"
fi

if [ -d "$HOME/py" ] ; then
    export PYTHONPATH="$HOME/py:$PYTHONPATH"
fi

export DJANGO_SETTINGS_MODULE=kn.settings

{% if pillar['python3'] %}
export PYTHON=python3
{% endif %}
