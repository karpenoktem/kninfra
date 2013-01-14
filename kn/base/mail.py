import django.template
import django.core.mail

from kn import settings

def render_then_email(template, to, ctx={}, cc=[], bcc=[], from_email=None,
                        reply_to=None):
    """ Render an e-mail from a template and send it. """
    # Normalize arguments
    if isinstance(to, basestring):
        to = [to]
    if isinstance(cc, basestring):
        cc = [cc]
    if isinstance(bcc, basestring):
        bcc = [bcc]
    # Render template
    template = django.template.loader.get_template(template)
    rendered_nodes = {}
    ctx['BASE_URL'] = settings.BASE_URL
    context = django.template.Context(ctx)
    for node in template.nodelist:
        if node.__class__.__name__ != 'BlockNode':
            # XXX importing BlockNode from django.template.loader_tags fails.
            #     Hence this workaround.
            continue
        rendered_nodes[node.name] = node.render(context)
    if not 'subject' in rendered_nodes:
        raise KeyError, "Missing subject block"
    if not 'plain' in rendered_nodes:
        raise KeyError, "Missing plain block"
    # Set up e-mail
    headers = {}
    if cc:
        headers['CC': ' ,'.join(cc)]
    if reply_to:
        headers['Reply-To': reply_to]
    if not from_email:
        from_email = rendered_nodes.get('from',
                settings.DEFAULT_FROM_EMAIL).strip()
    email = django.core.mail.EmailMessage(rendered_nodes['subject'].strip(),
                                          rendered_nodes['plain'].strip(),
                                          from_email,
                                          to,
                                          headers=headers,
                                          bcc=(cc + bcc))
    # And send!
    email.send()

# vim: et:sta:bs=2:sw=4:
