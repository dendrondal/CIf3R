import sqlite3
from pathlib import Path
import pickle
import click


@click.command()
@click.option("--table_name")
def create_metadata(table_name):
    project_dir = Path(__file__).resolve().parents[2]
    data_path = project_dir / "data" / "interim"
    db_path = data_path / "metadata.sqlite3"
    guideline_path = project_dir / "data/external" / f"{table_name}.pickle"
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cleanup = "DROP TABLE {}".format(table_name)
    try: 
        cur.execute(cleanup)
    except Exception:
        pass

    init = """CREATE TABLE {} (
        hash text PRIMARY KEY,
        recyclable text NOT NULL,
        stream text NOT NULL,
        subclass text NOT NULL
    )
    """.format(
        table_name
    )
    cur.execute(init)

    with open(guideline_path, "rb") as f:
        guideline_dict = pickle.load(f)
    for key in ["R", "O"]:
        for stream in guideline_dict[key]:
            for subclass in guideline_dict[key][stream]:
                folder = data_path / key / subclass.replace(" ", "_")
                for img in folder.glob("*.jpg"):
                    query = """
                    INSERT INTO {} (hash, recyclable, stream, subclass) VALUES (?, ?, ?, ?)
                    """.format(
                        table_name
                    )
                    try:
                        cur.execute(
                            query, (str(data_path / img), key, stream, subclass)
                        )
                    except sqlite3.IntegrityError:
                        pass

    init = """CREATE TABLE IF NOT EXISTS models (
        university text PRIMARY KEY,
        model_name text NOT NULL
    )
    """
    cur.execute(init)


    subtbl = """ CREATE TABLE IF NOT EXISTS class_mapping (
        university text PRIMARY KEY,
        label text NOT NULL,
        key_index integer NOT NULL
    )"""
    cur.execute(subtbl)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_metadata()
