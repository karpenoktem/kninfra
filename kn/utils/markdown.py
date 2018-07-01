from __future__ import absolute_import

from markdown import Extension, Markdown
from markdown.treeprocessors import Treeprocessor


""" KN markdown parser
This module depends on Markdown: http://pypi.python.org/pypi/Markdown """


class FixHeadingsExtension(Extension):

    """ FixHeadingsExtension wordt gebruikt als extension voor markdown.Markdown
        zodat header tags veranderd worden '<h2>' -> '<div class="md_h2">' """
    class FixHeadingsProcessor(Treeprocessor):

        """ FixHeadingsProcessor van Daan, zie FixHeadingsExtension voor het
            gebruik van de class.  """

        def run(self, root):
            for elem in (elem for elem in root if elem.tag in
                         ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')):
                # deze for-loop itereert over alleen de tags die in het lijstje
                # staan, door te itereren over de generator met de if-tag
                tag, elem.tag = elem.tag, 'div'
                if 'class' in elem.attrib:
                    elem.attrib['class'] = '%s md_%%s' % (elem.attrib['class'],
                                                          tag)
                else:
                    elem.attrib['class'] = 'md_%s' % tag
            return root

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add(
            'fixheading',
            FixHeadingsExtension.FixHeadingsProcessor(md),
            '_end'
        )


parser = Markdown(extensions=[FixHeadingsExtension()], safe_mode="escape")

# vim: et:sta:bs=2:sw=4:
