import os
import subprocess
import tempfile
import re
import htmlentitydefs
from . import htmlutils
##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


def cleanup_code(code):
    ''' Removes nested math delimiters of the form \( \) inside $ $ pairs'''
    result = re.findall(r'\$(.*?)\$', code)
    for snippet in result:
        newsnippet = snippet.replace(r'\(', ' ').replace(r'\)', ' ')
        code = code.replace(snippet, newsnippet)

    code = code.strip()

    # if align* in code we don't need delimiters
    if r'align*' in code:
        if code.startswith(r'\('):
            code = code[2:]
        if code.endswith('\)'):
            code = code[:-2]

    # remove blank lines and lines that start with %
    newcode = []
    for line in code.split('\n'):
        if line.strip().startswith('%'):
            continue
        if not line.strip():
            continue
        newcode.append(line)
    code = '\n'.join(newcode)

    # escape % signs, comments in LaTeX
#   perc_split = code.split('%')
#   for i, chunk in enumerate(perc_split):
#       if not chunk.endswith('\\'):
#           perc_split[i] = chunk + '\\'

#   code = '%'.join(perc_split)

    code = htmlutils.repair_equations(code)

    return code


pstricksTex = r'''
\documentclass[preview, border=1bp]{standalone}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{fp}
\usepackage{float} % for figures to appear where you want them
\usepackage{setspace}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{changebar}

%\usepackage{auto-pst-pdf}
\usepackage{pst-all}
\usepackage{pst-eucl}
\usepackage{pst-poly}
\usepackage{pst-math}
\usepackage{pstricks-add}

\usepackage{pst-spectra}
\usepackage{pst-slpe}
\usepackage{pst-3dplot}
\usepackage{pst-diffraction}
\usepackage{pst-lens}
\usepackage{pst-optic}
\usepackage{pst-solides3d}
\usepackage{pst-node}
\usepackage{pst-labo}
\usepackage{pst-electricfield}
\usepackage{pst-magneticfield}
\usepackage{pst-circ}



%% ************* NB ************
%% The order in which pstricks packages are loaded
%% matters - so I copied the order from pst-all.sty
%% and then added the two additional packages at the end.
%% ************* End NB ************

%% ************* Packages ************
\usepackage{pst-circ}
\usepackage{pstricks-add}         %Jo
\usepackage{pst-labo}         %Jo
\usepackage{subfigure}
\usepackage{multirow}
\usepackage{amsmath}
\usepackage{tabularx}
\usepackage{lscape}
\usepackage{fancyhdr}
\usepackage{wasysym}
\usepackage{url}
\usepackage{amsmath, amsthm, amsfonts, amssymb}
\usepackage{eurosym}
\usepackage{array}
\usepackage{enumitem}
\sffamily

%\usepackage{mdframed}

\newcommand{\ohm}{\ensuremath{\Omega}}
\newcommand{\eohm}{\,\Omega}
\newcommand{\eN}{\,\rm{N}}                %m in text
\newcommand{\emm}{\,\rm{m}}                %m in text
\newcommand{\ep}{\,\ekg \cdot \mbox{\ms}}                %m/s in text
\newcommand{\es}{\,\text{s}}                %s in equation
\newcommand{\ekg}{\,\text{kg}}                %kg in equation
\newcommand{\eJ}{\,\text{J}}                %J in equation
\newcommand{\eA}{\,\text{A}}                %A in equation
\newcommand{\eV}{\,\text{V}}                %J in equation
\newcommand{\eW}{\,\text{W}}                %W in equation
\newcommand{\ms}{$\text{m}\cdot\text{s}^{-1}$}                %m/s in text
\newcommand{\mss}{$\text{m}\cdot\text{s}^{-2}$}                %m/s in text
\newcommand{\ems}{\,\text{m} \cdot \text{s}^{-1}}            %m/s in equation
\newcommand{\emss}{\,\text{m} \cdot \text{s}^{-2}}            %m/s in equation
\newcommand{\px}{$x$}                % position x, in text
\newcommand{\py}{$y$}                % position y, in text
\newcommand{\edx}{\Delta x}        % displacement dx, in text
\newcommand{\dx}{$\edx$}            % displacement dx, in text
\newcommand{\edy}{\Delta y}            % displacement dy, in text
\newcommand{\dy}{$\edy$}            % displacement dy, in text
\newcommand{\edt}{\Delta t}            % delta time dt, in text
\newcommand{\dt}{$\edt$}            % delta time dt, in text
\newcommand{\vel}{$v$}                % velocity
\newcommand{\kph}{km$\cdot$hr$^{-1}$}    %km/h in text
\newcommand{\momen}{\vec{p}}            %momentum
\newcommand{\kener}{KE}                            %kinetic energy
\newcommand{\poten}{PE}                            %kinetic energy
\newcommand{\degree}{^{\circ}}
\newcommand{\ie}{{\em i.e.~}}
\newcommand{\eg}{{\em e.g.~}}
\newcommand{\cf}{{\em c.f.~}}
\newcommand{\resp}{{\em resp.~}}
\newcommand{\etc}{{\em etc.~}}
\newcommand{\nb}{{\em n.b.~}}
\newcommand{\eJSI}{{\,\text{kg} \cdot \text{m}^{2} \cdot \text{s}^{-2}}}
\def\deg{$^{\circ}$}
\newcommand{\ud}{\mathrm{d}}

% Arrow for objects and images
%\newpsobject{oi}{psline}{arrowsize=6pt, arrowlength=1.5, arrowinset=0, linewidth=2pt}
%\psset{lensHeight=3,lensColor=lightgray}
%\newpsobject{PrincipalAxis}{psline}{linewidth=0.5pt,linecolor=gray}

%\include{DefinitionsV0-5}

\makeatletter
\newcommand*{\getlengthinpt}[1]{\strip@pt#1}
\makeatother

\pagestyle{empty}
\begin{document}
\begin{pspicture}__CODE__
\end{pspicture}
\end{document}
'''

tikzTex = r'''
\documentclass[preview, border=1bp]{standalone}
\renewcommand{\familydefault}{\sfdefault}

\usepackage{tikz, ifthen}
\usetikzlibrary{arrows,shapes,backgrounds,patterns,decorations.pathreplacing,decorations.pathmorphing,decorations.markings,shadows,shapes.misc,calc,positioning,intersections}

\usepackage{setspace}
\usepackage{graphicx}
\usepackage{changebar}
\usepackage{xcolor}

\usepackage{pgfplots}
\usepackage{pgfplotstable}
\usepackage{tkz-euclide}
\usetkzobj{all}

%set diagram styles
\tikzset{
dot/.style={circle,inner sep=1pt,fill,},
every node/.append style={font={\small}},
-||-/.style={decoration={
  markings,
  mark=at position #1 with {\draw (-1pt,-3pt) -- (-1pt,3pt); \draw ( 1pt,-3pt) -- ( 1pt,3pt);}},postaction={decorate}},
}

\pgfplotsset{
axis lines =center,
xlabel = $x$,
ylabel =$y$,
clip=false,
cycle list={black\\},
ticklabel style={scale=1},
xlabel style={at=(current axis.right of origin), anchor=west},
 ylabel style={at=(current axis.above origin), anchor=south},
disabledatascaling,
}
%% ************* Packages ************
\usepackage{amsmath}
\usepackage{wasysym}
\usepackage{amsmath, amsthm, amsfonts, amssymb}
\usepackage{eurosym}
\sffamily

\pagestyle{empty}
\begin{document}
\begin{tikzpicture}__CODE__
\end{tikzpicture}
\end{document}
'''

equationTex = u'''\\documentclass[preview, border=1bp]{standalone}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}
\\usepackage{keystroke}
\\usepackage{cancel}
\\usepackage{xcolor}
\\begin{document}
__CODE__
\\end{document}'''.encode('utf-8')


def execute(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout, stderr


class LatexPictureError(Exception):
    pass


def pstikz2png(iPictureElement, iLatex, iReturnEps=False, iPageWidthPx=None,
               iDpi=150, iIncludedFiles={}):
    """
    Inputs:

      iPspictureElement - etree.Element

      iReturnEps - whether to also return the intermediate EPS file

      iPageWidthPx - page width in pixels, used to scale the
        style:width attribute in the element.

      iDpi - Will be used only if the width of the figure relative to
        the page width was not set (or the page width in pixels was not
        passed as an argument).

    Outputs:

    One or two paths, the first to the PNG, the second to the EPS.
    """

    tempDir = tempfile.mkdtemp()
    latexPath = os.path.join(tempDir, 'figure.tex')
    pngPath = os.path.join(tempDir, 'figure.png')
    pdfPath = os.path.join(tempDir, 'figure.pdf')

    # can send the raw string code or a <pre> element with <code> child
    if isinstance(iPictureElement, str):
        code = iPictureElement
        code = cleanup_code(code)
    else:
        code = iPictureElement.find('.//code').text.encode('utf-8')
    code = code.replace(r'&amp;', '&').replace(r'&gt;', '>').replace(r'&lt;', '<')

    if code is None:
        raise ValueError, "Code cannot be empty."
    with open(latexPath, 'wt') as fp:
        temp = unescape(iLatex.replace('__CODE__', code.strip()))
        try:
            fp.write(temp)
        except UnicodeEncodeError:
            fp.write(temp.encode('utf-8'))

    for path, pathFile in iIncludedFiles.iteritems():
        try:
            os.makedirs(os.path.join(tempDir, os.path.dirname(path)))
        except OSError:
            # Catch exception if path already exists
            pass
        with open(os.path.join(tempDir, path), 'wb') as fp:
            fp.write(pathFile.read())
    try:
        texlivepath = [p for p in os.getenv('PATH').split(':') if 'texlive' in p][0]
    except IndexError:
        # use the /usr/bin/pdflatex as fallback
        texlivepath = '/usr/bin'

    errorLog, temp = execute(["{texlive}/xelatex".format(texlive=texlivepath),
                              "-shell-escape", "-halt-on-error",
                              "-output-directory", tempDir, latexPath])
    try:
        open(pdfPath, "rb")
    except IOError:
        raise LatexPictureError, "LaTeX failed to compile the image. %s \n%s" % (latexPath, iLatex.replace('__CODE__', code.strip()))

    # crop the pdf image too
#   execute(['pdfcrop', '--margins', '1', pdfPath, pdfPath])

    execute(['convert',
             '-density',
             '%i' % iDpi,
             pdfPath,
             pngPath])

    return pngPath


def tikzpicture2png(iTikzpictureElement, *args, **kwargs):
    return pstikz2png(iTikzpictureElement, tikzTex, *args, **kwargs)


def pspicture2png(iPspictureElement, *args, **kwargs):
    return pstikz2png(iPspictureElement, pstricksTex, *args, **kwargs)


def equation2png(iPspictureElement, *args, **kwargs):
    # check to see how many lines are in the code
    iPspictureElement = iPspictureElement.replace(r'\[', '\(').replace(r'\]', '\)')
    iPspictureElement = iPspictureElement.replace(r'&', r' &')
    # remove tabs
    iPspictureElement = iPspictureElement.replace('\t', ' ')
    return pstikz2png(iPspictureElement, equationTex, *args, **kwargs)
