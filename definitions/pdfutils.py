# -*- coding: utf-8 -*-
# pylint: disable=too-many-branches,bad-builtin,line-too-long,

"""
Utitlities for definitions app
"""

from io import StringIO
from lxml import etree
                                            # pylint: disable=no-name-in-module
from lxml.etree import XMLSyntaxError
                                            # pylint: enable=no-name-in-module
from tempfile import mkdtemp
from tempfile import mkstemp
import commands
import glob
import os

from django.conf import settings as st

class Latex2PdfException(Exception):
    """Raised whenever there's a problem compiling latex"""

class TmpDir(object):
    """context manager to use a temporary folder"""
    def __init__(self):
        self._tmp_dir = mkdtemp()

    def __enter__(self):
        return self._tmp_dir

    def __exit__(self, _type, value, traceback):
        """remove dir"""
        os.system('rm -r "{}"'.format(self._tmp_dir))

def card2latex(card):
    """..."""
    parser = etree.HTMLParser()

    html = card.definition
    try:
        # expects a file, use StringIO for string
        tree = etree.parse(StringIO(unicode(html)), parser)
        root = tree.getroot()
        result = u'\\section*{%s}\n\n%s' % (card.name, html2latex(root))
    except XMLSyntaxError:
        result = u'\\section*{%s}\n\n' % card.name
    return result


def blockquote_rule(child):
    """blockquote to latex"""
    return u'\\begin{leftbar}\n%s\n\\end{leftbar}' % html2latex(child)


def h1_rule(child):
    """h1 to latex"""
    return u'\\subsection*{%s}' % html2latex(child)


def h_rule(child):
    """h2, h3, ..., h7 rule"""
    return u'\\subsubsection*{%s}' % html2latex(child)


def table_rule(child):
    """table to latex"""
    result = []
    ncols = len(child.find('tbody').find('tr').findall('td'))
    colf = ur'p{{{:.1f}\hsize}}'.format(1 / float(ncols))
    colformat = '|'.join([colf] * ncols)
    result.append(ur'\begin{table}')
    result.append(ur'\begin{tabular}{|%s|}' % (colformat))
    result.append(u'\n\\hline\n')
    result.append(html2latex(child))
    result.append(ur'\end{tabular}')
    result.append(ur'\end{table}')
    return ''.join(result)


def tr_rule(child):
    """tr to latex"""
    row_cells = []
    for cell in child:
        if cell.tag == 'th':
            row_cells.append(ur'\textbf{%s}' % html2latex(cell))
        elif cell.tag == 'td':
            row_cells.append(html2latex(cell))
    result = ' & '.join(row_cells)
    result += u'\\\\' # latex new line
    result += u'\\hline\n' # horizontal line
    return result


def th_rule(child):
    """th to html"""
    return u'\\textbf{%s}' % html2latex(child)


def span_rule(child):
    """span to html"""
    span_class = child.attrib.get('class', '')
    if span_class == 'math-tex':
        # remove \( and \) or \[ and \]
        math = child.text[2:-2]
        if not math.startswith(ur'\begin{align'):
            return u'${}$'.format(math.replace('#', '\\#'))
        else:
            return math.replace(ur'\texttt', '')
    else:
        # any other kind of span
        return u'\\hline\n{}\\hline\n'.format(html2latex(child))


def ol_rule(child):
    """ol to latex"""
    if child.attrib.get('type', '') == 'a':
        return u'\\begin{enumerate}[a)]\n%s\\end{enumerate}' % html2latex(child)
    else:
        return u'\\begin{enumerate}\n%s\\end{enumerate}' % html2latex(child)


def ul_rule(child):
    """ul to latex"""
    return u'\\begin{itemize}\n%s\\end{itemize}' % html2latex(child)


def li_rule(child):
    """li to latex"""
    return u'\\item {}'.format(html2latex(child))


def p_rule(child):
    """p to latex"""
    p_style = child.attrib.get('style', '')
    if 'text-align:center' in ''.join(p_style.split()):
        return u'\\begin{center}\n%s\n\\end{center}' % html2latex(child)
    else:
        return html2latex(child)


def default_rule(child):
    """anything not treated to latex"""
    return html2latex(child)


def pre_rule(child):
    """pre to latex"""
    settings = ur"""
    \lstset{
        commentstyle=\color{mygreen},
        keywordstyle=\color{myred},
        frame=single,
        backgroundcolor=\color{gray!10},
        inputencoding=utf8,
        extendedchars=true,
        mathescape=true,
        breaklines=true,
        literate={á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1 {ñ}{{\~n}}1
    }
    """
    child.text = child.text.replace('\\lt', '<').replace('\\gt', '>')
    code = u'\\begin{lstlisting}[language=pseudo]%s\\end{lstlisting}' % html2latex(child)
    return settings + code


def strong_rule(child):
    """strong to latex"""
    return u'\\textbf{%s}' % html2latex(child)


def add_single_image(path, small=False):
    """Just one image"""
    if small:
        size = '[width=3cm]'
    else:
        size = ''
    max_w, max_h = r'\textwidth', r'\textheight'

    result = ur"""
    \begin{adjustbox}{max size={%s}{%s}}
        \includegraphics%s{%s}
        \end{adjustbox}
    """ % (max_w, max_h, size, path)
    return result


def add_gif(path):
    """Split gif and add all images"""
    _, tmp_file = mkstemp(suffix='.png')
    cmd = 'convert {source} {target}'.format(source=path, target=tmp_file)
    status, output = commands.getstatusoutput(cmd)
    if status != 0:
        raise Latex2PdfException(output)
    # collect all jpg files
    pattern = tmp_file.replace('.png', '*.png')
    result = []
    for jpg_file in glob.glob(pattern):
        if jpg_file == tmp_file:
            continue
        result.append(add_single_image(jpg_file, small=True))
    return ''.join(result)


def img_rule(child):
    """img to latex"""
    path = child.attrib.get('src').replace('/media/', '')
    if not path.endswith('.gif'):
        return add_single_image(path)
    else:
        return add_gif(os.path.join(st.MEDIA_ROOT, path))


def hr_rule(_):
    """hr to latex"""
    return ur'\vspace{0.5cm}\hrule\vspace{0.5cm}'


html2latex_rules = {
    'blockquote': blockquote_rule,
    'h1': h1_rule,
    'h2': h_rule,
    'h3': h_rule,
    'h4': h_rule,
    'h5': h_rule,
    'h6': h_rule,
    'h7': h_rule,
    'hr': hr_rule,
    'img': img_rule,
    'li': li_rule,
    'ol': ol_rule,
    'p': p_rule,
    'pre': pre_rule,
    'span': span_rule,
    'strong': strong_rule,
    'table': table_rule,
    'th': th_rule,
    'tr': tr_rule,
    'ul': ul_rule,
}

def html2latex(element):
    """Recursively transform html elements in latext text"""

    result = []
    if element.text:
        result.append(element.text.replace('&', '\\&').replace('#', '\\#'))

    for child in element:
        # recursion happens here
        rule = html2latex_rules.get(child.tag, default_rule)
        result.append(rule(child))

        if child.tail:
            result.append(child.tail.replace('&', '\\&'))

    return ''.join(result)

def _make_preamble():
    """Return preamble of latex document"""
    pre = r"""
\documentclass[10pt,a4paper]{article}
\nonstopmode
\usepackage{subcaption}
\usepackage{enumerate}
\usepackage[utf8]{inputenc}
\usepackage[margin=1.2in]{geometry}
\usepackage[makeroom]{cancel}
\DeclareUnicodeCharacter{00A0}{ }
\usepackage{adjustbox}
\usepackage{graphics}
\graphicspath{ {%s} }
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\allowdisplaybreaks[2]
\usepackage{setspace}
\usepackage[rgb]{xcolor}
\definecolor{mygreen}{rgb}{0,0.6,0}
\definecolor{myred}{rgb}{0.6,0,0}
\definecolor{lightgray}{rgb}{0.9,0.9,0.9}
\definecolor{darkgray}{rgb}{0.2,0.2,0.2}
\usepackage{framed}
\usepackage{listings}
\usepackage{framed}

\renewenvironment{leftbar}[1][\hsize]
{%%
\def\FrameCommand
{%%

    {\hspace{-3pt}\color{darkgray}\vrule width 2pt}%%
    \hspace{0pt}
    \fboxsep=\FrameSep\colorbox{lightgray}%%
}%%
\MakeFramed{\hsize#1\advance\hsize-\width\FrameRestore}%%
}
{\endMakeFramed}

\lstdefinelanguage{pseudo}{
    keywords = {
        procedure,function,while,for,
        foreach,if,else,elseif
    },
    morecomment=[l]{//},
    morecomment=[s]{/*}{*/},
    morestring=[b]",
}
\catcode`_=12
\begingroup\lccode`~=`_\lowercase{\endgroup\let~\sb}
\mathcode`_="8000
\begin{document}
""" % st.MEDIA_ROOT
    end = ur'\end{document}'
    return pre, end

def latex2pdf(latex, path):
    """Compile latex and produce pdf"""
    with TmpDir() as tmp_dir:
        sourcepath = os.path.join(tmp_dir, 'source.tex')
        with open(sourcepath, 'wb') as source:
            source.write(latex.encode('UTF-8'))
        latex_cmd = 'cd {tmp_dir} && pdflatex {sourcepath} -output-format=pdf'.format(**locals())
        status, output = commands.getstatusoutput(latex_cmd)
        if status != 0:
            raise Latex2PdfException(output)

        target = sourcepath.replace('tex', 'pdf')
        cp_cmd = 'cp "{target}" "{path}"'.format(target=target, path=path)
        status, output = commands.getstatusoutput(cp_cmd)
        if status != 0:
            raise Latex2PdfException(output)

def concepts2latex(concepts):
    """Return full latex string"""
    preamble, end = _make_preamble()
    content = map(card2latex, concepts)
    return '\n'.join([preamble] + content + [end])

def concepts2pdf(concepts, path):
    """Produce pdf output"""
    latex = concepts2latex(concepts)
    # copy latex for further analisis
    with open('/tmp/source.tex', 'wb') as copy:
        copy.write(latex.encode('UTF-8'))
    latex2pdf(latex, path)

if __name__ == '__main__':
    pass
