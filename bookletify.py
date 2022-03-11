import argparse
import os
import pdb
from subprocess import check_output
from shutil import which

# TODO
# - Make it so that also page numbers that are not a multiple of 4 are possible, such that the first page will always be the first page of the booklet, and all empty pages are at the end of the booklet.

for p in ["pdftk", "pdfnup"]:
    assert which(p) is not None, f"Script needs '{p}' executables in path."

def is_pdf(string):
    if os.path.isfile(string) and os.path.splitext(string)[-1] == ".pdf":
        return string
    else:
        raise Exception(f"{string} is not a pdf file")

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', dest="input_path", required=True, type=is_pdf, help="Input pdf file.")
parser.add_argument('-o', '--output', dest="output_path", required=True, help="output pdf file.")
args = parser.parse_args()

num_pages = check_output(f"pdftk {args.input_path} dump_data | grep NumberOfPages | awk '{{print $2}}'", shell=True)
num_pages = int(num_pages)

print(f"Number of pages in pdf: {num_pages}")

l = []

swap = True

assert num_pages % 4 == 0, "Only can handle pdf with page count divisible by 4"
assert num_pages % 2 == 0

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

temp_file = f"temp_{args.output_path}"

os.system(f"pdftk C2.pdf cat {num_str} output {temp_file}")
os.system(f"pdfnup --nup 2x1 --outfile {args.output_path} {temp_file}")
os.remove(temp_file)
