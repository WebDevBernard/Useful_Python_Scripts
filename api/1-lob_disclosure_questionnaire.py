import pandas as pd 
from pathlib import Path
from docxtpl import DocxTemplate
from datetime import datetime, timedelta
from PyPDF2 import PdfReader, PdfWriter

#Directory Paths for each file
lob_filename = ["Disclosure and LOB.docx",
                "LOB - Family Blank.pdf"
                ]
questionnaire_filename = ["GORE - Rented Questionnaire.pdf", 
                          "Optimum West Rental Q.pdf", 
                          "WAWA Rental Condo Questionnaire.pdf",
                          "wawa rented dwelling Q.pdf",
                          "Rented Dwelling Quest INTACT.docx"
                          ]
base_dir = Path(__file__).parent.parent
excel_path = base_dir / "input.xlsx"  # name of excel
output_dir = base_dir / "output" # name of output folder
output_dir.mkdir(exist_ok=True)

#Pandas reading excel file
df = pd.read_excel(excel_path, sheet_name="Sheet1")

#Formats dates to MMM DD, YYYY
df["effective_date"] = df["effective_date"].dt.strftime("%B %d, %Y")
thirty_before_effective = pd.to_datetime(df["effective_date"], format="%B %d, %Y") - timedelta(days=30)
df["thirty_before_effective"] = thirty_before_effective.dt.strftime("%B %d, %Y")
df["today"] = datetime.today().strftime("%B %d, %Y")

#Remove white spaces
def whitespace_remover(dataframe):
    for i in dataframe.columns:
      if dataframe[i].dtype == 'object':
        dataframe[i] = dataframe[i].str.strip()
      else:
        pass
whitespace_remover(df)

#Checks if there is additonal_insured
def insuredNames(rows):
  if (pd.isnull(rows["additional_insured"])):
    return rows["insured_name"]
  return rows["insured_name"] + " & " + rows['additional_insured']

#Checks if no risk address, use mailing address as risk address
def riskAddress(rows):
  if (pd.isnull(rows["risk_address"])):
    return rows["mailing_address"]
  return rows["risk_address"]

#Reads and writes PDF
def writeToPdf(pdf, dictionary, rows):
  pdf_path = base_dir / "input" / pdf
  reader = PdfReader(pdf_path)
  writer = PdfWriter()
  for pageNum in range(reader.numPages):
    page = reader.getPage(pageNum)
    writer.add_page(page)
  writer.updatePageFormFieldValues(
  writer.getPage(0), dictionary
  )
  output_path = output_dir / f"{rows['insured_name']} - {rows['policy_number']} {pdf}"
  with open(output_path, "wb") as output_stream:
    writer.write(output_stream)
    
#Write to Docx    
def writeToDocx(docx, rows):
  template_path = base_dir / "input" / docx
  doc = DocxTemplate(template_path)
  doc.render(rows)
  if (rows["insurer"] == "Family"):
    output_path = output_dir / f"{rows['insured_name']} - {rows['policy_number']} Disclosure Notice.docx"
  else:
    output_path = output_dir / f"{rows['insured_name']} - {rows['policy_number']} {docx}"
  output_path.parent.mkdir(exist_ok=True)
  doc.save(output_path)

for rows in df.to_dict(orient="records"):
  #Make Disclosure and LOB.docx
  writeToDocx(lob_filename[0],rows)
  #Make LOB - Family Blank.pdf
  if (rows["insurer"] == "Family"):
    dictionary = {"Name of Insureds": insuredNames(rows),
                  "Address of Insureds": rows["mailing_address"],
                  "Day": rows["effective_date"].split(" ")[1],
                  "Month": rows["effective_date"].split(" ")[0],
                  "Year": rows["effective_date"].split(" ")[2],
                  "Policy Number": rows["policy_number"],
                  }
    writeToPdf(lob_filename[1], dictionary, rows)
  if pd.notnull(rows["risk_address"]):
    #Make GORE - Rented Questionnaire
    if (rows["insurer"] == "Gore Mutual"):
      dictionary = {"Applicant / Insured": insuredNames(rows),
                    "Gore Policy #": rows["policy_number"],
                    "Principal Street": rows["mailing_address"],
                    "Rental Street": riskAddress(rows)
                  }
      writeToPdf(questionnaire_filename[0], dictionary, rows)
    #Make Questionnaire - Optimum West Rental Q
    if (rows["insurer"] == "Optimum West"):
      dictionary = {"Policy_Number[0]": insuredNames(rows),
                    "Applicant_Insured[0]": rows["insured_name"],
                    "Rental_Location_Address[0]": riskAddress(rows),
                    }
      writeToPdf(questionnaire_filename[1], dictionary, rows)
    #Make Questionnaire - WAWA Rental Condo Questionnaire
    if (rows["insurer"] == "Wawanesa" and rows["type"] != "Revenue"):
      dictionary = {"Insureds Name": insuredNames(rows),
                    "Policy Number": rows["policy_number"],
                    "Address of Property": riskAddress(rows),
                    "Date Coverage is Required": rows["effective_date"],
                    }
      writeToPdf(questionnaire_filename[2], dictionary, rows)
    #Make Questionnaire - wawa rented dwelling Q 
    if (rows["insurer"] == "Wawanesa" and rows["type"] == "Revenue"):
      dictionary = {"Insured's Name": insuredNames(rows),
                    "Policy Number": rows["policy_number"],
                    "Address of Property": riskAddress(rows),
                    }
      writeToPdf(questionnaire_filename[3], dictionary, rows)   
    #Make Questionnaire - Rented Dwelling Quest INTACT 
    if (rows["insurer"] == "Intact"):
      writeToDocx(questionnaire_filename[4], rows)