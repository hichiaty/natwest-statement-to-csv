import tabula
import pandas as pd
import glob
import argparse
from tqdm import tqdm
parser = argparse.ArgumentParser(
    description='Convert Natwest Statement PDF to CSV')
parser.add_argument('--pdf', '-p', type=str, help='PDF file path')


def pdf_to_csv(pdf_path, csv_path):
    table = tabula.read_pdf(pdf_path, pages=1)
    current_date = table[2].columns[0]
    res = {'Date': [], 'Type': [], 'Description': [],
           'Paid in': [], 'Paid out': [], 'Balance': []}

    res['Date'].append(current_date)
    res['Type'].append(table[2].columns[1])
    res['Description'].append(table[2].columns[2])
    res['Paid in'].append(table[2].columns[3])
    res['Paid out'].append(table[2].columns[4])
    res['Balance'].append(table[2].columns[5])

    for i, row in table[2].iterrows():
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
    df.to_csv(csv_path, index=False)
    return df


if __name__ == '__main__':
    args = parser.parse_args()
    if not args.pdf.endswith('.pdf'):
        pdfs = glob.glob(args.pdf + '/*.pdf')
    else:
        pdfs = [args.pdf]

    for pdf in tqdm(pdfs):
        csv_path = pdf.replace('.pdf', '.csv')
        pdf_to_csv(pdf, csv_path)
