base:
    '*':
        {% if grains['vagrant'] %}
        - vagrant
        {% endif %}
        - mysql
