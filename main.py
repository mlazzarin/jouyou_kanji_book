# Python script to create a Kanji grid HTML file from the 常用漢字 list.
# Author: Marco Lazzarin

# Libraries required:
# - pandas: to read and process CSV file
# - jinja2: to build the HTML file from the template
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import json
from datetime import datetime


def truncate(text, maxlen=30):
    """Truncate text to the maximum length 'maxlen'."""
    assert maxlen > 0
    assert isinstance(text, str)
    return (text[:maxlen] + "…") if len(text) > maxlen else text


if __name__ == "__main__":
    # Load Kanji data from data sources and select relevant columns
    # Data source:
    # https://www.kanjidatabase.com/
    # https://github.com/scriptin/jmdict-simplified
    # https://www.edrdg.org/wiki/index.php/Main_Page
    df = pd.read_csv("kanji_database.csv", encoding="utf-8", sep=";")
    df = df[[
        "id",
        "Kanji",
        "Strokes",
        "Grade",
        "JLPT-test",
        "Kanji Frequency with Proper Nouns"
    ]]
    with open("kanjidic2-en-3.6.1.json", "r", encoding="utf-8") as f:
        kanjidic_data = json.load(f)  # used for kanji meanings and readings

    # Order by grade, number of strokes and id
    df_sorted = df.sort_values(by=["Grade", "Strokes", "id"], ascending=[True, True, True])

    # Prepare data for Jinja2
    kanji_cards = []
    for _, row in df_sorted.iterrows():

        # Most info are from kanji database
        kanji_info = {
            "number": row["id"],
            "kanji": row["Kanji"],
            "jlpt_level": row["JLPT-test"],
            "school_grade": row["Grade"]
        }
        # Get readings and meanings from kanjidic_data
        kanji_entry = next((k for k in kanjidic_data["characters"] if k["literal"] == kanji_info["kanji"]), None)
        assert kanji_entry is not None, f"Kanji {row['Kanji']} not found in kanjidic_data."
        readings = kanji_entry["readingMeaning"]["groups"][0]["readings"]
        readings_on = ", ".join([reading["value"] for reading in readings if reading["type"] == "ja_on"])
        readings_kun = ", ".join([reading["value"] for reading in readings if reading["type"] == "ja_kun"])
        meanings = kanji_entry["readingMeaning"]["groups"][0]["meanings"]
        meanings_en = ", ".join([meaning["value"] for meaning in meanings if meaning.get("lang") == "en"])

        kanji_cards.append({
            "number": row["id"],
            "kanji": row["Kanji"],
            "jlpt_level": row["JLPT-test"],
            "school_grade": row["Grade"],
            "readings_kun": readings_kun,
            "readings_on": readings_on,
            "meanings": meanings_en
        })

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template("template.html")

    # Render template
    output = template.render(kanji_cards=kanji_cards, creation_date=datetime.now().strftime("%Y-%m-%d"))

    # Save output to file
    with open("kanji_grid.html", "w", encoding="utf-8") as f:
        f.write(output)
