import networkx as nx
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to Python's module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.molecules import smiles_to_fingerprint

# Load data
df = pd.read_csv("./data/230106_frozen_metadata.csv.gz", low_memory=False)
df = df.dropna(subset=["organism_name"]).reset_index(drop=True)

# Remove duplicate organism-molecule pair
df_agg = (
    df.groupby(["organism_name", "structure_smiles_2D"])
    .size()
    .reset_index(name="reference_wikidata")
)

df_agg = (
    df.groupby(["organism_name", "structure_smiles_2D"])
    .agg(
        {
            "reference_wikidata": "size",
            "organism_taxonomy_08genus": "first",
            "organism_taxonomy_07tribe": "first",
            "organism_taxonomy_06family": "first",
            "organism_taxonomy_05order": "first",
            "organism_taxonomy_04class": "first",
            "organism_taxonomy_03phylum": "first",
            "organism_taxonomy_02kingdom": "first",
            "organism_taxonomy_01domain": "first",
            "structure_taxonomy_classyfire_01kingdom": "first",
            "structure_taxonomy_classyfire_02superclass": "first",
            "structure_taxonomy_classyfire_03class": "first",
            "structure_taxonomy_classyfire_04directparent": "first"
            # add other columns here as needed
        }
    )
    .reset_index()
)

df_agg["total_papers_molecule"] = df_agg.groupby("structure_smiles_2D")[
    "reference_wikidata"
].transform("sum")
df_agg["total_papers_species"] = df_agg.groupby("organism_name")[
    "reference_wikidata"
].transform("sum")

# get gbif data
gbif = pd.read_csv("./data/GBIF.csv.gz", index_col=0)
df_agg = df_agg.merge(gbif, on="organism_name")
df_agg = df_agg.dropna(subset="genus").reset_index(drop=True)

# get random subset of the database (comment to have the full DB)
# df_agg_train = df_agg_train.sample(n=100000).reset_index(drop=True)

# Fetch unique species and molecules and their respective features
unique_species_df = df_agg.drop_duplicates(subset=["organism_name"])
unique_molecules_df = df_agg.drop_duplicates(subset=["structure_smiles_2D"])

# Fetch the corresponding features
species_features = unique_species_df[
    ["kingdom", "phylum", "class", "order", "family", "genus", "organism_name"]
]
species_features.index = [i for i in unique_species_df["organism_name"]]

molecule_features = unique_molecules_df[
    [
        "structure_taxonomy_classyfire_01kingdom",
        "structure_taxonomy_classyfire_02superclass",
        "structure_taxonomy_classyfire_03class",
        "structure_taxonomy_classyfire_04directparent",
    ]
]
molecule_features.index = [i for i in unique_molecules_df["structure_smiles_2D"]]


# create features for species
# encoder_species = ce.BinaryEncoder(cols=[col for col in species_features_df.columns])
# species_features_dummy = encoder_species.fit_transform(species_features_df)
#
#
# encoder_molecule = ce.BinaryEncoder(cols=[col for col in molecule_features_df.columns])
# molecule_features_dummy = encoder_molecule.fit_transform(molecule_features_df)
#
# species_features_dummy.index = [i for i in unique_species_df['organism_name']]
# molecule_features_dummy.index = [i for i in unique_molecules_df['structure_smiles_2D']]

sample_fraction = 0.3  # 30% for example
df_test = df_agg.sample(frac=sample_fraction, random_state=42)
df_test.to_csv("./data/lotus_agg_test.csv.gz", compression="gzip")
df_train = df_agg.drop(df_test.index)
df_train.structure_smiles_2D.to_csv("./data/smiles_struct_train.csv")

g = nx.DiGraph()
for i, row in df_train.iterrows():
    g.add_edge(row["structure_smiles_2D"], row["organism_name"], label="present_in")

    # create edge in oppsite direction
    g.add_edge(row["organism_name"], row["structure_smiles_2D"], label="has")
    nx.set_node_attributes(
        g,
        {row["structure_smiles_2D"]: "molecule", row["organism_name"]: "species"},
        "label",
    )


mol_dum = smiles_to_fingerprint(unique_molecules_df["structure_smiles_2D"])

nx.write_graphml(g, "./graph/train_graph.gml")

molecule_features.to_csv("./data/molecule_features.csv.gz", compression="gzip")
species_features.to_csv("./data/species_features.csv.gz", compression="gzip")
df_train.to_csv("./data/lotus_agg_train.csv.gz", compression="gzip")
mol_dum.to_csv("./data/mol_dummy_rdkit.csv.gz", compression="gzip")
