import re

from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist
from django.template.loader import (BaseLoader, find_template_loader,
                                    get_template_from_string, make_origin)


# Based on django.template.loader.cached.Loader.  A lot is boilerplate:
# the magic happens in SlashNewlineStrippingTemplateLoader._process


class SlashNewlineStrippingTemplateLoader(BaseLoader):
    is_usable = True

    def __init__(self, loaders):
        self._loaders = loaders
        self._cached_loaders = []
        self._the_re = re.compile('\\\\\\n\\s*', re.M)

    def _process(self, template):
        return self._the_re.sub('', template)

    @property
    def loaders(self):
        if not self._cached_loaders:
            for loader in self._loaders:
                self._cached_loaders.append(find_template_loader(loader))
        return self._cached_loaders

    def reset(self):
        self._cached_loaders = []

    def find_template(self, name, dirs=None):
        for loader in self.loaders:
            try:
                if hasattr(loader, 'load_template_source'):
                    template, display_name = loader.load_template_source(
                        name, dirs)
                else:
                    template, display_name = loader(name, dirs)
                return (template,
                        make_origin(
                            display_name,
                            loader.load_template_source, name, dirs))
            except TemplateDoesNotExist:
                pass
        raise TemplateDoesNotExist(name)

    def load_template(self, template_name, template_dirs=None):
        template, origin = self.find_template(template_name, template_dirs)
        if hasattr(template, 'render'):
            raise ImproperlyConfigured("Cannot handle loaders that prerender")
        template = self._process(template)
        try:
            template = get_template_from_string(template, origin,
                                                template_name)
        except TemplateDoesNotExist:
            # from django.template.loader.cached.Loader:
            # If compiling the template we found raises
            # TemplateDoesNotExist, back off to returning the source and
            # display name for the template we were asked to load. This
            # allows for correct identification (later) of the actual
            # template that does not exist.
            return template, origin
        return template, None

# vim: et:sta:bs=2:sw=4:
