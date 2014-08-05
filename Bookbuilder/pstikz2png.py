import os
import subprocess

from lxml import etree

pstricksTex = r'''
\documentclass[10pt]{report}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{fp}
\usepackage{float} % for figures to appear where you want them
\usepackage{setspace}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{changebar}

\usepackage{auto-pst-pdf}
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
\documentclass[10pt]{report}
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
axis equal image, 
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

    tempDir = os.curdir
    latexPath = os.path.join(tempDir, 'figure.tex')
    dviPath = os.path.join(tempDir, 'figure.dvi')
    psPath = os.path.join(tempDir, 'figure.ps')
    epsPath = os.path.join(tempDir, 'figure.epsi')
    pngPath = os.path.join(tempDir, 'figure.png')
    pdfPath = os.path.join(tempDir, 'figure.pdf')

    code = iPictureElement.find('.//code').text.encode('utf-8')
    code = code.replace(r'&amp;', '&').replace(r'&gt;', '>').replace(r'&lt;', '<')

    if code is None:
        raise ValueError, "Code cannot be empty."
    with open(latexPath, 'wt') as fp:
        fp.write(iLatex.replace('__CODE__', code.strip()))

    for path, pathFile in iIncludedFiles.iteritems():
        try:
            os.makedirs(os.path.join(tempDir, os.path.dirname(path)))
        except OSError:
            # Catch exception if path already exists
            pass
        with open(os.path.join(tempDir, path), 'wb') as fp:
            fp.write(pathFile.read())
    texlivepath = [p for p in os.getenv('PATH').split(':') if 'texlive' in p][0]
    errorLog, temp = execute(["{texlive}/pdflatex".format(texlive=texlivepath),
                              "-shell-escape", "-halt-on-error",
                              "-output-directory", tempDir, latexPath])
    try:
        open(pdfPath,"rb")
    except IOError:
        raise LatexPictureError, "LaTeX failed to compile the image. %s" % latexPath


    execute(['convert',
             '-density',
             '%i'%iDpi,
             pdfPath,
             '-trim',
             '-bordercolor',
             'None',
             '-border',
             '10x10',
             '+repage',
             pngPath])

    return pngPath


def tikzpicture2png(iTikzpictureElement, *args, **kwargs):
    return pstikz2png(iTikzpictureElement, tikzTex, *args, **kwargs)

def pspicture2png(iPspictureElement, *args, **kwargs):
    return pstikz2png(iPspictureElement, pstricksTex, *args, **kwargs)
