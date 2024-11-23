Erklärungen zu den Änderungen
Importieren der erforderlichen Bibliotheken für die Visualisierung
Um die Volatilität zu berechnen und zu visualisieren, müssen wir zusätzliche Bibliotheken importieren:

python
Code kopieren
import matplotlib.pyplot as plt
import numpy as np
Anpassen der get_stock_data-Funktion
Die Funktion get_stock_data wurde angepasst, um alle verfügbaren Daten herunterzuladen und zu speichern. Dadurch stellen wir sicher, dass wir alle notwendigen Spalten für die Volatilitätsberechnung haben.

python
Code kopieren
data[ticker] = ticker_data  # Alle Spalten für die Verarbeitung beibehalten
Auswahl der Preisarten für die Excel-Datei
Nach dem Abrufen der Daten wählen wir die vom Benutzer angegebenen Preisarten für die Speicherung in der Excel-Datei aus.

python
Code kopieren
df_selected = df.xs(price_types, level=1, axis=1, drop_level=False)
Berechnung der Volatilität
Renditen berechnen: Für jeden Ticker werden die Renditen basierend auf dem Schlusskurs oder dem bereinigten Schlusskurs berechnet.

Rollierende Volatilität: Die rollierende Volatilität wird mit einem Fenster berechnet, das vom Intervall abhängt (z. B. 20 Tage für tägliche Daten).

python
Code kopieren
returns = price_data.pct_change()
volatility = returns.rolling(window=window).std() * np.sqrt(window)
Visualisierung
Darstellung: Kurs- und Volatilitätsdaten werden in einem Diagramm mit zwei y-Achsen dargestellt.

Speichern des Plots: Das Diagramm wird als PNG-Datei im Ausgabeordner gespeichert.

python
Code kopieren
plt.savefig(plot_file)
plt.close()
Installation der erforderlichen Bibliotheken
Stellen Sie sicher, dass Sie die folgenden Bibliotheken installiert haben, bevor Sie das Skript ausführen:

bash
Code kopieren
pip install yfinance pandas matplotlib numpy