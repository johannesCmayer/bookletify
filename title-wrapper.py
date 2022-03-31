title = "Analysis 1"
author = "Terence Tao "
chapter = 2

template = f"""
    \\documentclass{{article}}

    \\begin{{document}}
        \\begin{{center}}
            \\vspace*{{1cm}}
            \Huge
            {title} \\\\
            \\vspace*{{0.4cm}}
            \huge
            {author} \\\\
            \\vspace*{{1cm}}
            \huge
            Chapter {chapter}
        \end{{center}}
    \end{{document}}
"""

# TODO write .tex

os.system("pdflatex ")

