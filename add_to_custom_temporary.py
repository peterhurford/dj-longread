import os
import boto # Fail fast if Python env is not properly loaded
import psycopg2
import pandas as pd
import random
from datetime import datetime


def execute_shell_command(command):
    """Executes the given shell command."""
    os.system(command)


def clear_file_content(filepath):
    """Clears the content of the specified file."""
    with open(filepath, 'w') as file:
        pass  # Just open and close to clear the file
    print(f"File content cleared: {filepath}")


def new_entry(links, url, title):
    """Generates a new entry for the links DataFrame."""
    return {
        'id': links['id'].max() + 1,
        'url': url.strip().replace(',', ''),
        'title': title.strip().replace(',', ''),
        'summary': '\\N',
        'domain': '\\N',
        'added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'liked': '\\N',
        'category': '\\N',
        'aggregator': 'Custom',
        'seed': random.randint(1, 100),
        'starred': '\\N',
        'tweet': 0
    }


def clean_text_field(txt):
    """Cleans specific HTML entities and quotation marks from text fields."""
    if not isinstance(txt, str):
        return txt
    replacements = {
        '&nbsp;': '', '&ldquo;': '"', '&rdquo;': '"',
        '&lsquo;': '\'', '&rsquo;': '\'', '&mdash;': '-',
        '&ndash;': '-', '"""': '"', '\'\'\'': '\'', 'n"t': 'n\'t', 'n""t': 'n\'t'
    }
    for old, new in replacements.items():
        txt = txt.replace(old, new)
    return txt


def process_links(filepath):
    """Processes new links from a file and updates the links DataFrame."""
    links = pd.read_csv('data/export.csv')
    last_added_date = links['added'].max()

    with open(filepath, 'r') as file:
        new_links = file.readlines()
    
    for i, new_link in enumerate(new_links):
        if ' | ' in new_link:
            url, title = new_link.strip().replace('    - ', '').split(' | ', maxsplit=1)
            entry = new_entry(links, url, title)
            links = pd.concat([links, pd.DataFrame([entry])], ignore_index=True)
    
    # Clean text fields
    links['summary'] = links['summary'].apply(clean_text_field)
    links['title'] = links['title'].apply(clean_text_field)

    # Correct data types and sort
    links = links[links['id'].notnull()]
    links['id'] = links['id'].astype(int)
    links['seed'] = links['seed'].astype(int)
    links['tweet'] = links['tweet'].apply(lambda x: 0 if str(x) == '\\N' else int(float(str(x)))).astype(int)
    links = links.sort_values('id')
    
    links.to_csv('data/export.csv', index=False)
    print(f"Updated links exported to data/export.csv. Latest added date: {last_added_date}")


def confirm_step(message):
    """Asks the user for confirmation to proceed with a step."""
    response = input(message + " Type 'c' to confirm: ").lower()
    return response == 'c'


def main():
    # Fail fast if psql is not properly loaded
    DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
    psycopg2.connect(DATABASE_URL, sslmode='require')

    # Run initial database export/import command
    print("Exporting and importing database...")
    execute_shell_command("heroku run --app guarded-everglades-89687 make exportdb && make importdb")
    
    # Process new links
    links_filepath = '/Users/peterhurford/Documents/links.txt'
    process_links(links_filepath)
    
    # Confirmation before running the final command
    if confirm_step("Ready to run the final pipeline command"):
        print("Running final pipeline command...")
        execute_shell_command("make csv_to_s3 && heroku run --app guarded-everglades-89687 make importdb && make pipeline")
    else:
        print("Final pipeline command aborted.")
        return
    
    # Confirmation before clearing the file content
    if confirm_step("Ready to clear the content of the links file"):
        clear_file_content(links_filepath)
    else:
        print("File clearing aborted.")

if __name__ == "__main__":
    main()
