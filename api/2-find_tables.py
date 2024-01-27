from pathlib import Path
import pdfplumber

def filter_dict(dictionary):
    for key, value in dictionary.items():
        filtered_list = [sublist for sublist in value if sublist[0] != '']
        cleaned_list = [[s.split('\n') if i == 0 else s for i, s in enumerate(sublist)] for sublist in
                        filtered_list]
        dictionary[key] = cleaned_list
    return dictionary

def extract_tables_from_pdf(pdf_path):
    result_dict = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            tables = []
            table_coords = []
            page = pdf.pages[page_number]
            find_tables = page.find_tables()
            for table in find_tables:
                table_coords.extend(table.cells)
            for cell in table_coords:
                extracted_text = page.crop(cell).extract_text(layout=False)
                tables.append(extracted_text)
            result_dict[page_number + 1] = [[elem1, elem2] for elem1, elem2 in zip(tables, table_coords)]
    return filter_dict(result_dict)

def draw_rectangles(pdf_path, dictionary):
    with pdfplumber.open(pdf_path) as pdf:
        for page_number in range(len(pdf.pages)):
            if page_number + 1 in dictionary:
                dict_list = dictionary[page_number + 1]
                pdf.pages[page_number].to_image(resolution=400).draw_rects([x[1] for x in dict_list]).show()

base_dir = Path(__file__).parent.parent
pdf_directory = Path(base_dir / "input")
pdf_files = pdf_directory.glob("*.pdf")
pdf_file_paths = []
output_dir = base_dir / "output"  # name of output folder
output_dir.mkdir(exist_ok=True)

# Loop through each PDF file and append the full path to the list
for pdf_file in pdf_files:
    file_path = str(pdf_file)
    pdf_file_paths.append(file_path)

for pdf_path in pdf_file_paths:
    print(f"\n<========= PDF_FILENAME: {pdf_path} =========>\n")
    pages = extract_tables_from_pdf(pdf_path)
    # draw_rectangles(pdf_path, pages)
    with open(output_dir / f"{Path(pdf_path).stem} find_table_coordinates.txt", 'w') as file:
        for page, value in pages.items():
            file.write(f"\n<========= Page: {page} =========>\n")
            print(f"\n<========= Page: {page} =========>\n")
            for text, box in enumerate(value):
                file.write(f"#{text} : {box}\n")
                print(f"#{text} : {box}")
