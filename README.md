# GNN
In this repo we try to implement a graph neural network that should ideally predict the chemical compositions of organisms in across the tree of life. 

If the user wants to reproduce this, it should first download the latest version of LOTUS [here](https://zenodo.org/record/7534071) or like this : 

```bash
wget https://zenodo.org/record/7534071/files/230106_frozen_metadata.csv.gz
```

The algorithm implements a link classification task in a graph between nodes `species` and nodes `molecule`. We use HinSAGE with mean aggregator from [StellarGraph](https://stellargraph.readthedocs.io/en/stable/index.html) library.

## Playing around
To reproduce the model, the user should first : 

```bash
conda env create -f environment.yaml
conda activate stellar_graph
```
We will first parse the LOTUS database and get the taxonomy from GBIF for each species. This will be the species features.
Then we create a graph of LOTUS and split them into training and testing dataset (for now 70-30 split):
```bash
python gbif_taxo.py
python graph_creation_train.py
python graph_creation_test.py
```

After grid searching for the best parameters, we set the neural network with two hidden layers of 1024 neurons each with activations "elu" and "selu" respectively. The training of the model can be seen in the `HinSAGE_mol_to_species.ipynb` or `HinSAGE_species_to_mol.ipynb` notebooks. Testing on unseen data is in the `HinSAGE_test_*.ipynb` notebooks.

If we want to recreate the entire LOTUS database as a graph simply run : 
```python
g_train = nx.read_graphml("./graph/train_graph.gml")
g_test = nx.read_graphml("./graph/test_graph.gml")
g = nx.compose(g_train, g_test)
```

## Training
Since HinSAGE can only predict one edge type at a time, we created two models. One for predicting **unknown molecules** in **known species** and one for predicting **unknown species** in **known molecules**. 

To train the models, you can run the two Jupyter Notebooks, `HinSAGE_mol_to_species.ipynb` and `HinSAGE_species_to_mol.ipynb`. 

## Testing
### Molecules to species
With known species but unknown molecules, the model has a an accuracy of 0.94 (with threshold at 0.5 or above considered as *present*). 
### Species to molecules
With known molecules but unknown species, the model has an accuracy of 0.8 (same threshold). 

 