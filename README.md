## Recurring patterns in online social media interactions during highly engaging events
Github Repository to reproduce the analysis and figure in [https://arxiv.org/abs/2205.03639](https://arxiv.org/abs/2205.03639)

## Dependencies
Python (3.10.0)
\
Python Modules: [requirements.txt](https://github.com/ComplexConnectionsLab/Recurrent_Patterns_Reddit/blob/main/requirements.txt)

### How the `code` folder is structured
- `data_analysis`: this folder contains the code to reproduce the analysis presented in the paper.
- `data_collection`: this folder contains the code to collect Reddit data by querying the Pushshift API.
- `plot`: this folder contains the code to reproduce the subplots of the paper (as well as the figure in the supplementary).
- `data_analysis/temporal`: this folder contains the code to reproduce the temporal analysis presented in the paper.
- `data_analysis/semantic`: this folder contains the code to reproduce the semantic analysis presented in the paper.
- `data_analysis/users`: this folder contains the code to reproduce the users analysis presented in the paper.

## Data
- [Pushshift API](https://github.com/pushshift/api)
- [Google Trends](https://github.com/GeneralMills/pytrends)


## For Developers
License: MIT