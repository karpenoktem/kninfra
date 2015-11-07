phassa:
    host.present:
        - ip: {{ pillar['ip-phassa'] }}
sankhara:
    host.present:
        - ip: {{ pillar['ip-sankhara'] }}
