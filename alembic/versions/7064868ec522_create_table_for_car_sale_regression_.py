"""create table for car sale regression dataset

Revision ID: 7064868ec522
Revises: 
Create Date: 2024-09-26 11:29:30.651580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7064868ec522'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "car_sale_regression",
        sa.Column("id", sa.Integer(), nullable=False,
                  comment="Unique integer representation of each row in the dataset", primary_key=True),
        
        sa.Column("brand", sa.String(50), 
                  comment="String representing the brand/manufacturer of the vehicle (e.g. `Ford`). Brands are a super set of Models. Models are not guaranteed to be unique to a single brand."),
        
        sa.Column('model', sa.String(100), nullable=False,
                  comment='Specific model of the car (e.g. `Mustang`). Models always belong to a brand.'),
        
        sa.Column('model_year', sa.Integer(), nullable=False,
                  comment='Year that instance of the car was produced'),
        
        sa.Column('mileage', sa.Integer(), nullable=False,
                  comment='Total distance the car has been driven (in miles)'),
        
        sa.Column('fuel_type', sa.String(50), nullable=True,
                  comment='Type of fuel the car uses (e.g., `Gasoline`, `E85 Flex Fuel`)'),
        
        sa.Column('engine', sa.String(100), nullable=False,
                  comment='Engine specifications (e.g., "172.0HP 1.6L 4 Cylinder Engine Gasoline Fuel")'),
        
        sa.Column('transmission', sa.String(100), nullable=False,
                  comment='Transmission type (e.g., A/T for Automatic Transmission)'),
        
        sa.Column('ext_col', sa.String(100), nullable=False,
                  comment='Exterior color of the car. Colors are specifically "Base Colors" such as `Silver`, `Black`, `Red`, rather than their manufacturer name'),
        
        sa.Column('int_col', sa.String(100), nullable=False,
                  comment='Interior color of the car. Colors are specifically "Base Colors" such as `Silver`, `Black`, `Red`, rather than their manufacturer name'),
        
        sa.Column('accident', sa.String(200), nullable=True,
                  comment='Accident history of the car. Description includes if an accident or damage has been reported, and if so, how many have been'),
        
        sa.Column('clean_title', sa.String(5), nullable=False,
                  comment='"yes"/"no" or "true"/"false" indicating if the car has a clean title'),
        
        sa.Column('price', sa.Integer(), nullable=False,
                  comment='Price of the car in whole currency units (e.g., USD)')
    )

def downgrade() -> None:
    op.drop_table('car_sale_regression')
