# vim: et:sta:bs=2:sw=4:

from markdown import Markdown, Extension
from markdown.treeprocessors import Treeprocessor

"""
KN markdown parser
This module is named markdown_parse (instead of markdown), because importing
markdown will import *this* module
"""

class FixHeadingsExtension(Extension):
    class FixHeadingsProcessor(Treeprocessor):
        """
            MarkdownProcessor van Daan, zie MarkdownExtension voor het gebruik
            van de class.
        """
        def run(self, root):
            tags = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
            for elem in (elem for elem in root if elem.tag in tags):
                tag = elem.tag
                elem.tag = 'div'
                if 'class' in elem.attrib:
                    elem.attrib['class'] = '%s md_%s' % (elem.attrib['class'],
                            tag)
                else:
                    elem.attrib['class'] = 'md_%s' % tag
            return root

    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('fixheading',
                FixHeadingsExtension.FixHeadingsProcessor(md), '_end')
