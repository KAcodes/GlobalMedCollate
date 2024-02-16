"""Script parses data from Pubmed Journals"""
import xml.etree.ElementTree as ET
from os import listdir

import pandas as pd
from pandarallel import pandarallel
import spacy
from rapidfuzz import fuzz


pandarallel.initialize(progress_bar=True)


nlp = spacy.load("en_core_web_sm")


def extract_article_info(article) -> dict:
    """Returns details for any given article"""

    title = article.find(".//ArticleTitle").text
    year =  article.find(".//PubMedPubDate/Year").text
    pmid = article.find(".//PMID").text
    keywords_list = article.findall(".//KeywordList/Keyword")
    keywords = [keyword.text for keyword in keywords_list]

    mesh_list = article.findall(".//PublicationTypeList/PublicationType")
    mesh_nos = [mesh.attrib["UI"] for mesh in mesh_list]

    return {
        "title": title,
        "year": year,
        "pmid": pmid,
        "keywords": keywords,
        "mesh_list": mesh_nos,
    }


def extract_author_info(author: ET) -> dict:
    """Returns details for any given Author"""

    id_search = ".//Identifier[@Source='GRID']"
    forename = author.find(".//ForeName").text if author.find(".//ForeName") is not None else None
    lastname = author.find(".//LastName").text if author.find(".//LastName") is not None else None
    initials = author.find(".//Initials").text if author.find(".//Initials") is not None else None
    grid_id = author.find(id_search).text if author.find(id_search) is not None else None
    affiliations_list = author.findall(".//AffiliationInfo/Affiliation")
    affiliations = [affiliation.text for affiliation in affiliations_list]

    return {
        "forename": forename,
        "surname": lastname,
        "initials": initials,
        "GRID_id": grid_id,
        "affiliations": affiliations,
    }


def xml_to_df(root) -> list:
    """Converts the xml file to list of authors contributing to every Sjogren article"""

    author_contributions = []
    articles = list(root)
    for article in articles:
        article_details = extract_article_info(article)

        for author in article.findall(".//Author"):
            copy_of_article = article_details.copy()
            author_info = extract_author_info(author)
            author_and_article_info = {**copy_of_article, **author_info}
            author_contributions.append(author_and_article_info)

    return author_contributions


def author_list_to_df(author_list) -> pd.DataFrame:
    """Returns list of authors contributing to every Sjogren article as a dataframe"""

    author_affiliations = pd.DataFrame(author_list)
    author_affiliations = author_affiliations.explode("affiliations").reset_index(drop=True)

    return author_affiliations


def add_emails(sjogren_df: pd.DataFrame) -> pd.DataFrame:
    """Adds email found in affiliations as seperate column to Dataframe"""

    emails = sjogren_df["affiliations"].str.extract(r"(\w+@\w+.\w+)")
    sjogren_df["emails"] = emails

    zipcodes = sjogren_df["affiliations"].str.extract(r"( \d{5} |\w{2}\d \d\w{2}|\w\d\w \d\w\d)")
    sjogren_df["zipcodes"] = zipcodes

    return sjogren_df


def extract_country(affiliation) -> str | None:
    """Returns country out of affiliation string via NLP matching"""

    if isinstance(affiliation, str):
        doc = nlp(affiliation)
        countries = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
        return countries[-1] if countries else None
    return None


def extract_institution(affiliation) -> str | None:
    """Returns institution out of affiliation string via NLP matching"""

    if isinstance(affiliation, str):
        doc = nlp(affiliation)
        countries = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        return countries[-1] if countries else None
    return None


def update_countries_and_institutions(sjogren_df: pd.DataFrame) -> pd.DataFrame:
    """Applies extracting country and institutions functions to dataframe"""

    sjogren_df['countries'] = sjogren_df['affiliations'].apply(extract_country)
    sjogren_df['institutions_pub'] = sjogren_df['affiliations'].apply(extract_institution)

    return sjogren_df


def match_institutions(pubmed_institute: str, institutes_df: pd.DataFrame) -> pd.DataFrame:
    """Returns closest institution match in csv for dataframe institute via fuzzy-matching"""

    if isinstance(pubmed_institute, str):

        institutes_df['match_ratio'] = institutes_df['name'].apply(
            lambda x: fuzz.partial_ratio(pubmed_institute, x))

        filtered_matches = institutes_df[institutes_df['match_ratio'] > 90]

        if not filtered_matches.empty:

            best_match = filtered_matches.loc[filtered_matches['match_ratio'].idxmax()]

            matched_name = best_match['name']
            matched_grid_id = best_match['grid_id']

            institutes_df.drop(columns=['match_ratio'], inplace=True)

            return matched_name, matched_grid_id

        return pubmed_institute, None

    return None, None


def update_grid_institutions(sjogren_df: pd.DataFrame) -> pd.DataFrame:
    """Adds institution GRID id to dataframe"""

    institutes_df = pd.read_csv('institutes.csv')
    sjogren_df['institutions_grid'], sjogren_df['institutions_grid_id'] = zip(
        *sjogren_df['institutions_pub'].parallel_apply(
            lambda x: match_institutions(x, institutes_df)))

    return sjogren_df


if __name__ == "__main__":

    file_path = listdir("downloaded_xmls")[0]
    file_name = file_path.replace('.xml', '')

    xml_root = ET.parse(F"downloaded_xmls/{file_name}.xml").getroot()
    authors_list = xml_to_df(xml_root)
    df = author_list_to_df(authors_list)[:1000]

    added_emails = add_emails(df)

    added_countries_df = update_countries_and_institutions(added_emails)

    updated_institutions = update_grid_institutions(added_countries_df)

    updated_institutions.to_csv(f"{file_name}.csv", index=False)

    print("CSV created")
