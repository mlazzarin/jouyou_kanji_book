# Python script to create a Kanji grid HTML file from the 常用漢字 list.
# Author: Marco Lazzarin

# Libraries required:
# - pandas: to read and process CSV file
# - jinja2: to build the HTML file from the template
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os


def truncate(text, maxlen=30):
    """Truncate text to the maximum length 'maxlen'."""
    assert maxlen > 0
    assert isinstance(text, str)
    return (text[:maxlen] + "…") if len(text) > maxlen else text


if __name__ == "__main__":
    # Load Kanji data from CSV file and select relevant columns
    # Data source: https://www.kanjidatabase.com/
    df = pd.read_csv("kanji_database.csv", encoding="utf-8", sep=";")
    df = df[[
        "id",
        "Kanji",
        "Strokes",
        "Grade",
        "JLPT-test",
        "Reading within Joyo",
        "Reading beyond Joyo",
        "Translation of On",
        "Translation of Kun",
        "Kanji Frequency with Proper Nouns"
    ]]
    df["Reading beyond Joyo"] = df["Reading beyond Joyo"].fillna("")

    # Order by grade, number of strokes and id
    df_sorted = df.sort_values(by=["Grade", "Strokes", "id"], ascending=[True, True, True])

    # Prepare data for Jinja2
    kanji_cards = []
    for _, row in df_sorted.iterrows():
        meaning_on = f"On: {row['Translation of On']}"
        meaning_kun = f"Kun: {row['Translation of Kun']}"
        kanji_cards.append({
            "number": row["id"],
            "kanji": row["Kanji"],
            "jlpt_level": row["JLPT-test"],
            "school_grade": row["Grade"],
            "reading_within": row["Reading within Joyo"],
            "reading_beyond": row["Reading beyond Joyo"],
            "meaning_on": truncate(meaning_on, 40),
            "meaning_kun": truncate(meaning_kun, 40)
        })

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__))))
    template = env.get_template("template.html")

    # Render template
    output = template.render(kanji_cards=kanji_cards)

    # Save output to file
    with open("kanji_grid.html", "w", encoding="utf-8") as f:
        f.write(output)
