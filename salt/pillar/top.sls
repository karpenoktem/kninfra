base:
    '*':
        {% if grains['vagrant'] %}
        - vagrant
        {% endif %}
