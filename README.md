# FeatureFlow Quick Start 

1. Init virtualenv, pip install -r requirements.txt 
2. Init .env in GenAI_App_Frontend/
3. Need OPENAI_API_KEY and DATABRICKS_TOKEN in .env 

4. Run 'reflex run' in the GenAI_App_Frontend dir

## Problem Description/ Inspiration
This project was inspired by the need to make machine learning more accessible and efficient. Traditional feature engineering can be time-consuming and requires specialized knowledge, making it harder for teams to quickly find valuable insights in their data. We noticed that these challenges often slow down how fast businesses can experiment and make decisions based on data. In fast-paced environments, teams need easy-to-use tools that let everyone(technical and non-technical) contribute to building better models.

## Solution
By allowing Gen AI to handle feature creation based on simple, natural language prompts, we aimed to make machine learning workflows faster and more collaborative. Our solution helps teams harness their creativity alongside the power of AutoML, enabling them to quickly find, test, and refine impactful features. Ultimately, this makes machine learning more practical, effective, and valuable for businesses.

## What we did
Our team created a Gen AI application that automates feature engineering based on user-specified prompts and AI-suggested insights. Users simply describe their feature needs in natural language, which Gen AI then translates into new features for the dataset. These generated features are then passed to an AutoML pipeline to assess their impact over the baseline conversion metric, refining the dataset and optimizing predictive accuracy.

## How we did it
* Data store - The data is stored in Databricks Data Unity Catalog
* Frontend and Backend Development - We use Reflex to develop both the frontend and backend interfaces.
* Feature Engineering with Generative AI - Using models like Databricks Llama, Databricks Mixtral, Databricks DBRX, and GPT-4 Mini, we automatically generate code based on feature descriptions.
* AutoML - Used FLAML for automated model training and tuning to evaluate performance on the enriched dataset against baseline metrics.
* Model Serving - The model is deployed and served using Databricks Model Serving endpoint
* Model Registry - Utilized Databricks MLflow Model Registry to register and manage models

## Names and country of residence of all your teammates
- Cole Mabie - United States of America
- Chris Sweet - United States of America
- Gowri Dath - United States of America
- Johann West - United States America
