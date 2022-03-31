import argparse
import os
import pdb
from subprocess import check_output
from shutil import which, copy

# TODO add functionality for cutting out of large book

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
TITLE_PAGE_TEX_PATH = f"{SCRIPT_PATH}/templates/title.tex"
BLANK_PAGE_TEX_PATH = f"{SCRIPT_PATH}/templates/blank.tex"

def num_of_pages(pdf_path):
    num_pages = check_output(f"pdftk {pdf_path} dump_data | grep NumberOfPages | awk '{{print $2}}'", shell=True)
    return int(num_pages)

def build_latex(tex_path):
    os.system(f"pdflatex {tex_path}")
    return os.path.splitext(tex_path)[0] + ".pdf"

def is_pdf(string):
    if os.path.isfile(string) and os.path.splitext(string)[-1] == ".pdf":
        return string
    else:
        raise Exception(f"{string} is not a pdf file")

def wrap_book(content_pdf_path, title_pdf_path, blank_pdf_path):
    file_path = "wrap.pdf"

    os.system(f"pdfunite {title_pdf_path} {blank_pdf_path} {content_pdf_path} {file_path}")
    num_pages = num_of_pages(file_path)
    trash_paths = []
    while num_pages % 4 != 0:
        dst = f"temp-{num_pages}-{file_path}"
        trash_paths.append(dst)
        os.system(f"pdfunite {file_path} {blank_pdf_path} {dst}")
        num_pages += 1

    copy(f"temp-{num_pages-1}-{file_path}", file_path)
    for p in trash_paths:
        os.remove(p)
    return file_path

def bookletify(pdf_path, output_path):
    num_pages = num_of_pages(pdf_path)

    assert num_pages % 4 == 0, "Only can handle pdf with page count divisible by 4"
    assert num_pages % 2 == 0

    print(f"Number of logical pages: {num_pages}")
    print(f"Number of printed pages: {num_pages/4}")

    l = []

    swap = True

    for i in range(1, int(num_pages/2) + 1):
        if swap:
            l.append(num_pages + 1 - i)
            l.append(i)
            swap = False
        else:
            l.append(i)
            l.append(num_pages + 1 - i)
            swap = True

    num_str = ""
    for i,e in enumerate(l):
        num_str += str(e) 
        if i < len(l) - 1:
            num_str += " "

    temp_file = f"temp_{output_path}"

    os.system(f"pdftk {pdf_path} cat {num_str} output {temp_file}")
    os.system(f"pdfnup --nup 2x1 --outfile {output_path} {temp_file}")
    os.remove(temp_file)

def edit(path):
    editor = check_output("echo $EDITOR", shell=True)
    editor = editor.decode("utf-8").strip()
    os.system(f"{editor} {path}")

def main():
    for p in ["pdftk", "pdfnup", "pdflatex"]:
        assert which(p) is not None, f"Script needs '{p}' executables in path."

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest="input_path", required=True, type=is_pdf, help="Input pdf file.")
    parser.add_argument('-o', '--output', dest="output_path", required=True, help="output pdf file.")
    parser.add_argument('-ed', '--edit', dest="edit", action="store_true", default=False, help="Edit title.tex")
    args = parser.parse_args()

    if args.edit:
        edit(TITLE_PAGE_TEX_PATH)
        exit(0)

    print("Building templates")
    blank_page_pdf_path = build_latex(BLANK_PAGE_TEX_PATH)
    title_page_pdf_path = build_latex(TITLE_PAGE_TEX_PATH)

    print("Wraping book")
    wraped_pdf_path = wrap_book(args.input_path, title_page_pdf_path, blank_page_pdf_path)

    print("Bookletify wraped book")
    bookletify(wraped_pdf_path, args.output_path)

if __name__ == "__main__":
    main()
