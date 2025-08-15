import pandas as pd
import zipfile
import requests
from io import BytesIO

# 1. Télécharger le fichier ZIP depuis geonames
url = "https://download.geonames.org/export/dump/BF.zip"
response = requests.get(url)
with zipfile.ZipFile(BytesIO(response.content)) as z:
    z.extractall("data")  # dossier où on extrait

# 2. Lire le fichier texte principal (BF.txt)
cols = [
    "geonameid", "name", "asciiname", "alternatenames",
    "latitude", "longitude", "feature class", "feature code",
    "country code", "cc2", "admin1 code", "admin2 code",
    "admin3 code", "admin4 code", "population", "elevation",
    "dem", "timezone", "modification date"
]
df = pd.read_csv("data/BF.txt", sep="\t", names=cols, dtype=str)

# 3. Garder les colonnes utiles et renommer
df_clean = df[["geonameid", "name", "latitude", "longitude"]].copy()
df_clean.columns = ["ID", "location_name", "lat", "long"]

# Sauvegarder
df_clean.to_csv("burkina_location.csv", index=False)

# 4.1 Filtre 'gounghin'
df_gounghin = df_clean[df_clean["location_name"].str.lower().str.contains("gounghin")]
df_gounghin.to_csv("gounghin.csv", index=False)

# 4.2 Noms commençant de A à P
mask_ap = df_clean["location_name"].str[0].str.upper().between("A", "P")
df_ap = df_clean[mask_ap]
lat_min = df_ap["lat"].astype(float).min()
lon_min = df_ap["long"].astype(float).min()
lat_min_name = df_ap[df_ap["lat"].astype(float) == lat_min]["location_name"].tolist()
lon_min_name = df_ap[df_ap["long"].astype(float) == lon_min]["location_name"].tolist()

# 4.3 Coordonnées lat >= 11 et lon <= 0.5
df_coord = df_clean[(df_clean["lat"].astype(float) >= 11) & (df_clean["long"].astype(float) <= 0.5)]

# 5. Export vers Excel
with pd.ExcelWriter("mini_projet.xlsx") as writer:
    df_gounghin.to_excel(writer, sheet_name="gounghin", index=False)
    df_ap.to_excel(writer, sheet_name="A_to_P", index=False)

# Affichage résultats clés
print("Latitude minimale :", lat_min, "->", lat_min_name)
print("Longitude minimale :", lon_min, "->", lon_min_name)
print("Nombre de lieux lat >= 11 et lon <= 0.5 :", len(df_coord))