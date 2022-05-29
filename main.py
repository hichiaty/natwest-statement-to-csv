import tabula
import pandas as pd
import glob
import argparse
from tqdm import tqdm
import os
from PyPDF2 import PdfFileReader
parser = argparse.ArgumentParser(
    description='Convert Natwest Statement PDF to CSV')
parser.add_argument('--pdf', '-p', type=str, help='PDF file path')
parser.add_argument('--merge', '-m', action='store_true',
                    help='Merge CSV files')


def get_num_pages(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        pdf = PdfFileReader(pdf_file)
        return pdf.getNumPages()


def pdf_to_csv(pdf_path, csv_path):
    current_date = None
    dfs = []
    for page in range(1, get_num_pages(pdf_path)+1):
        tables = tabula.read_pdf(pdf_path, pages=page,
                                 lattice=True)
        for table in tables:
            if 'Branch Details' in table.columns or (table.empty and 'Date' in table.columns):
                continue

            res = {'Date': [], 'Type': [], 'Description': [],
                   'Paid in': [], 'Paid out': [], 'Balance': []}

            if current_date is None:
                current_date = table.columns[0]
                res['Date'].append(current_date)
                res['Type'].append(table.columns[1])
                res['Description'].append(table.columns[2])
                res['Paid in'].append(table.columns[3])
                res['Paid out'].append(table.columns[4])
                res['Balance'].append(table.columns[5])

            for i, row in table.iterrows():
                if row[0] != current_date and isinstance(row[0], str):
                    current_date = row[0]

                tx_type = row[1]
                desc = row[2]
                paid_in = row[3]
                paid_out = row[4]
                balance = row[5]

                res['Date'].append(current_date)
                res['Type'].append(tx_type)
                res['Description'].append(desc)
                res['Paid in'].append(paid_in)
                res['Paid out'].append(paid_out)
                res['Balance'].append(balance)

            df = pd.DataFrame(res)
            df['Date'] = pd.to_datetime(df['Date'])
            dfs.append(df)

    final_df = pd.concat(dfs)
    final_df.to_csv(csv_path, index=False)
    return


if __name__ == '__main__':
    args = parser.parse_args()
    if not args.pdf.endswith('.pdf'):
        pdfs = glob.glob(args.pdf + '/*.pdf')
    else:
        pdfs = [args.pdf]

    for pdf in tqdm(pdfs):
        csv_path = pdf.replace('.pdf', '.csv')
        pdf_to_csv(pdf, csv_path)
    # check if merge is required
    if args.merge:
        print('Merging CSV files')
        csv_files = [i.replace('.pdf', '.csv') for i in pdfs]
        df = pd.concat([pd.read_csv(csv) for csv in tqdm(csv_files)])
        # sort by Date column
        df = df.sort_values(by='Date')
        df.to_csv(os.path.join(os.path.dirname(
            pdf), 'statements.csv'), index=False)
        print('Merged CSV file saved to {}'.format(
            os.path.join(os.path.dirname(pdf), 'statements.csv')))
    else:
        print('CSV files saved to {}'.format(os.path.dirname(pdf)))
