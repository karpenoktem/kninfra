from html2text import HTML2Text

import django.template
import django.template.loader
import django.core.mail

from django.conf import settings

def render_then_email(template_name, to, ctx={}, cc=[], bcc=[], from_email=None,
                        reply_to=None, headers=None):
    """ Render an e-mail from a template and send it. """
    # Normalize arguments
    if isinstance(to, basestring):
        to = [to]
    if isinstance(cc, basestring):
        cc = [cc]
    if isinstance(bcc, basestring):
        bcc = [bcc]
    if headers is None:
        headers = {}
    # Render template
    template = django.template.loader.get_template(template_name)
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
    if not 'plain' in rendered_nodes and not 'html' in rendered_nodes:
        raise KeyError, "Missing plain or html block"

    # Set up e-mail
    if cc:
        headers['CC'] = ', '.join(cc)
    if reply_to:
        headers['Reply-To'] = reply_to
    if not from_email:
        from_email = rendered_nodes.get('from',
                settings.DEFAULT_FROM_EMAIL).strip()

    if 'plain' in rendered_nodes:
        plain = rendered_nodes['plain'].strip()
    else:
        h = HTML2Text()
        h.ignore_links = True
        plain = h.handle(rendered_nodes['html']).strip()

    email = django.core.mail.EmailMultiAlternatives(rendered_nodes['subject'].strip(),
                          plain,
                          from_email,
                          to,
                          headers=headers,
                          bcc=(cc + bcc))

    if 'html' in rendered_nodes:
        email.attach_alternative(rendered_nodes['html'].strip(), "text/html")

    # And send!
    email.send()

# vim: et:sta:bs=2:sw=4:
