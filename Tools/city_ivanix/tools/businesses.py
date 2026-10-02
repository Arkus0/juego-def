"""Shops of a Cantabrian-Asturian port town around 2000 (invented names, no real brands).

Each category: names, sign colours (background, letters), the sign letter style (font file in C:/Windows/Fonts for the
look-dev; to be replaced by OFL fonts before release), the blade icon and what the shop puts out on the street.
"""

CATEGORIES = {
    "bar":         {"names": ["Bar El Puerto", "Bar Casa Tino", "Bar La Ribera", "Bodega Los Arcos", "Bar Chelo", "Taberna El Pescador", "Bar Avenida", "Café Bar Moderno"],
                    "colors": [("#1F5A3A", "#F2E6C8"), ("#8E2A22", "#F7E7C4"), ("#1E3A6E", "#F4EBD2")], "font": "COOPBL.TTF", "blade": "BAR", "goods": "terraza"},
    "cafe":        {"names": ["Café Central", "Café Indiano", "Cafetería La Nube", "Café de la Plaza"],
                    "colors": [("#4A2C1E", "#F3D9A4"), ("#2B4D5C", "#F1E3C2")], "font": "BRUSHSCI.TTF", "blade": "CAFÉ", "goods": "terraza"},
    "sidreria":    {"names": ["Sidrería El Llagar", "Sidrería La Pomarada"],
                    "colors": [("#2F5D1F", "#F5E9B8")], "font": "ROCKEB.TTF", "blade": "SIDRA", "goods": "barriles"},
    "fruteria":    {"names": ["Frutas Maribel", "Frutería La Huerta"],
                    "colors": [("#E07B1A", "#FFFFFF"), ("#3E8E2E", "#FFF6D8")], "font": "COOPBL.TTF", "blade": "FRUTAS", "goods": "fruta"},
    "pescaderia":  {"names": ["Pescados Hnos. Ruiz", "Pescadería La Rula"],
                    "colors": [("#1C5D99", "#FFFFFF")], "font": "FRAHV.TTF", "blade": "PESCADOS", "goods": "pescado"},
    "panaderia":   {"names": ["Panadería La Espiga", "Horno San Roque", "Confitería La Dulce"],
                    "colors": [("#F1DDAE", "#6B3A1E"), ("#7A3B1F", "#F8E3B5")], "font": "BRITANIC.TTF", "blade": "PAN", "goods": "pan"},
    "farmacia":    {"names": ["Farmacia Mier", "Farmacia de la Plaza"],
                    "colors": [("#F4F4F0", "#0F7A3A")], "font": "FRAHV.TTF", "blade": "+", "goods": None},
    "estanco":     {"names": ["Estanco nº 1", "Expendeduría nº 2"],
                    "colors": [("#6A3B1C", "#F2C230")], "font": "ROCKEB.TTF", "blade": "TABACOS", "goods": None},
    "ultramarinos": {"names": ["Ultramarinos Remedios", "Coloniales Herrera", "Alimentación La Plaza"],
                    "colors": [("#B23A2A", "#FFF3D6"), ("#244B2B", "#F6E7B6")], "font": "BERNHC.TTF", "blade": "ALIMENTACIÓN", "goods": "cajas"},
    "ferreteria":  {"names": ["Ferretería Gutiérrez", "Droguería Norte"],
                    "colors": [("#F2C12E", "#1A1A1A")], "font": "FRAHV.TTF", "blade": "FERRETERÍA", "goods": "ferreteria"},
    "moda":        {"names": ["Modas Carmen", "Mercería La Aguja", "Calzados Pereda"],
                    "colors": [("#6E1E3A", "#F6E2EA"), ("#1F1F1F", "#E8C77A")], "font": "BOD_B.TTF", "blade": "MODAS", "goods": "caballete"},
    "prensa":      {"names": ["Librería El Faro", "Papelería La Pluma", "Prensa y Revistas"],
                    "colors": [("#1D4E89", "#FFD84A"), ("#9C2B2B", "#FFFFFF")], "font": "BRITANIC.TTF", "blade": "PRENSA", "goods": "prensa"},
    "caja":        {"names": ["Caja Cantábrica", "Caja Rural del Valle"],
                    "colors": [("#0E4C92", "#FFFFFF"), ("#12704A", "#FFFFFF")], "font": "AGENCYB.TTF", "blade": "CAJA", "goods": None},
    "peluqueria":  {"names": ["Peluquería Loli", "Barbería Toño"],
                    "colors": [("#C2185B", "#FFFFFF"), ("#263238", "#F5F5F5")], "font": "BRUSHSCI.TTF", "blade": "PELUQUERÍA", "goods": None},
    "optica":      {"names": ["Óptica Norte"], "colors": [("#00838F", "#FFFFFF")], "font": "AGENCYB.TTF", "blade": "ÓPTICA", "goods": None},
    "electro":     {"names": ["Electrodomésticos Hnos. Saiz"], "colors": [("#C62828", "#FFFFFF")], "font": "FRAHV.TTF", "blade": "ELECTRO", "goods": "caballete"},
    "videoclub":   {"names": ["Videoclub Estrella"], "colors": [("#1A1446", "#FFD400")], "font": "BROADW.TTF", "blade": "VÍDEO", "goods": "caballete"},
    "seguros":     {"names": ["Seguros Díaz", "Inmobiliaria del Puerto"], "colors": [("#37474F", "#FFFFFF")], "font": "GILB____.TTF", "blade": None, "goods": None},
}

# when a trade runs out of names: "<prefix> <surname>" with Cantabrian-Asturian surnames
SURNAMES = ["Cobo", "Velarde", "Ceballos", "Bustamante", "Rivas", "Abascal", "Cuesta", "Mier", "Sainz", "Herrera", "Pereda",
            "Gutiérrez", "Llano", "Revuelta", "Quintana", "Arce", "Noriega", "Lavín", "Sobrado", "Escandón"]
PREFIX = {"bar": "Bar Casa", "cafe": "Café", "sidreria": "Sidrería Casa", "fruteria": "Frutas", "pescaderia": "Pescados",
          "panaderia": "Panadería", "farmacia": "Farmacia", "estanco": "Estanco", "ultramarinos": "Ultramarinos",
          "ferreteria": "Ferretería", "moda": "Modas", "prensa": "Librería", "caja": "Caja", "peluqueria": "Peluquería",
          "optica": "Óptica", "electro": "Electro", "videoclub": "Vídeo", "seguros": "Gestoría"}

# programme buildings carry their own sign
PROGRAMME_SIGNS = {
    "P_BAR": ("bar", "Bar El Puerto"),
    "P_HOTEL": ("hotel", "Hotel Miramar"),
    "P_PENSION": ("pension", "Pensión Rosi"),
    "P_MERCADO": ("mercado", "Mercado de Abastos"),
    "P_AYTO": ("ayuntamiento", "Casa Consistorial"),
    "P_CULTURA": ("cultura", "Casa de Cultura"),
    "P_HOGAR": ("hogar", "Hogar del Pensionista"),
    "P_COMANDANCIA": ("cuartel", "Casa Cuartel"),
    "P_ALMACEN": ("almacen", "Almacenes del Puerto"),
}
PROGRAMME_STYLE = {
    "hotel": ("#13294B", "#F2D27A", "BOD_B.TTF", "HOTEL"),
    "pension": ("#F3E9D2", "#7B2E1F", "BRITANIC.TTF", "PENSIÓN"),
    "mercado": ("#7A1F1F", "#F7E9C9", "ROCKEB.TTF", None),
    "ayuntamiento": ("#E9E2D0", "#3A2A1A", "BOD_B.TTF", None),
    "cultura": ("#E9E2D0", "#1F3A5A", "BOD_B.TTF", None),
    "hogar": ("#2E5E3A", "#F5ECD0", "BRITANIC.TTF", None),
    "cuartel": ("#F1EFEA", "#1F5A2E", "FRAHV.TTF", None),
    "almacen": ("#3B3F44", "#F2C12E", "FRAHV.TTF", None),
    "bar": ("#1F3A6E", "#F4EBD2", "COOPBL.TTF", "BAR"),
}

# what a main street's ground floors are, by weight (a Calle Mayor around 2000)
MAIN_MIX = [("bar", 18), ("cafe", 6), ("ultramarinos", 8), ("fruteria", 6), ("panaderia", 7), ("farmacia", 3), ("estanco", 3),
            ("moda", 8), ("prensa", 4), ("caja", 4), ("peluqueria", 5), ("ferreteria", 4), ("pescaderia", 4), ("optica", 2),
            ("electro", 3), ("videoclub", 2), ("seguros", 3), ("sidreria", 3)]
SIDE_MIX = [("bar", 10), ("ultramarinos", 6), ("panaderia", 3), ("peluqueria", 3), ("ferreteria", 3), ("sidreria", 3), ("seguros", 2)]
