from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup
import requests

# Don't change this
matplotlib.use('Agg')
app = Flask(__name__)  # Do not change this

# Insert the scraping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content, "html.parser")

# Find your right key here
table = soup.find('table', attrs={'class':'history-rates-data'})
row = table.find_all('tr')

row_length = len(row)

temp = []  # Init

# Assuming you have already obtained the 'table' element
elements_a = table.find_all('a', href=True, attrs={'class': 'w'})
elements_span = table.find_all('span', attrs={'class': 'w'})

for i in range(min(len(elements_a), len(elements_span))):
    tanggal = elements_a[i].text  # Assign the value to 'tanggal'
    harga = elements_span[i].text  # Assign the value to 'harga'
    
    # Check if tanggal is equal to elements_a[i].text
    # Check if harga is equal to elements_span[i].text
    if tanggal == elements_a[i].text and harga == elements_span[i].text:
        # If both conditions are met, append to 'temp'
        temp.append((tanggal, harga))

temp = temp[::-1]

# Change into a DataFrame
df = pd.DataFrame(temp, columns = ('Tanggal','Harga'))

# Insert data wrangling here
df['Tanggal'] = df['Tanggal'].astype('datetime64[ns]')
df['Harga'] = df['Harga'].str.replace('$1 = Rp','')
df['Harga'] = df['Harga'].str.replace(',','')
df['Harga'] = df['Harga'].astype('int64')
dfv1 = df.set_index(['Tanggal'])


# End of data wrangling

@app.route("/")
def index():
    #Card data for showing average result
    card_data = f'{dfv1["Harga"].mean().round(2)}'  # Average Price

    # Generate plot for Price
    fig_harga, ax_harga = plt.subplots(figsize=(16, 5))  # Adjust the width (16) and height (5) as needed
    dfv1['Harga'].plot(ax=ax_harga)

    # Rendering plot for By IMDB Rating
    figfile_harga = BytesIO()
    plt.savefig(figfile_harga, format='png', transparent=True)
    figfile_harga.seek(0)
    figdata_png_harga = base64.b64encode(figfile_harga.getvalue())
    plot_result = str(figdata_png_harga)[2:-1]
    plt.close(fig_harga)

    return render_template('index.html',
                           card_data=card_data, # Pass the Average Price
                           plot_result=plot_result  # Pass the Price
                           )

if __name__ == "__main__":
    app.run(debug=True)
