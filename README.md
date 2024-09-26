# GenAI_Hackathon

## Alembic Spinup
1. Make sure you have Docker installed and running on your system
2. Create a new Virtual Env and `pip install -r ./alembic/requirements.txt`
3. Run `docker compose up`
4. Download the dataset from [here](https://www.kaggle.com/competitions/playground-series-s4e9/data)
5. Uncomment `load_car_sale_regression_data_from_csv("/Users/csweet/Downloads/playground-series-s4e9/train.csv")` and set path to your copy of the data
6. Run `python postgres_load_data`

When you're done for the day you can stock docker compose with a cntrl+c. If you run `docker compose down` you will need to reload the dataset. cntrl+c just stops the container, but persists the data