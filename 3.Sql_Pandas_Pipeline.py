import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect('India_Agriculture.db')
cursor = conn.cursor()

# Create Tables

cursor.execute('''
               CREATE TABLE IF NOT EXISTS states(
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT UNIQUE NOT NULL,
                region  TEXT,
                area_km2    INTEGER
               )
               ''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS crops (
                id  INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT NOT NULL,
                category    TEXT,
                season      TEXT
                )
''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS production(
                   id   INTEGER PRIMARY KEY AUTOINCREMENT,   
                   state_id     INTEGER,
                   crop_id      INTEGER,
                   year     INTEGER,
                   area_ha      REAL,
                   production_mt    REAL,
                   yield_kg_ha      REAL,
                   FOREIGN KEY (state_id) REFERENCES states(id),
                   FOREIGN KEY (crop_id) REFERENCES crops(id)
               )
               ''')

conn.commit()
print('Tables Created!')



# Insertion of Data

states = [
    ('Punjab',       'North',  50362),
    ('Haryana',      'North',  44212),
    ('Uttar Pradesh','North',  240928),
    ('Maharashtra',  'West',   307713),
    ('Gujarat',      'West',   196024),
    ('Rajasthan',    'West',   342239),
    ('Karnataka',    'South',  191791),
    ('Andhra Pradesh','South', 162975),
    ('Tamil Nadu',   'South',  130058),
    ('West Bengal',  'East',   88752),
    ('Bihar',        'East',   94163),
    ('Madhya Pradesh','Central',308252),
]
cursor.executemany('''
                   INSERT OR IGNORE INTO states (name,region,area_km2) 
                   VALUES (?,?,?)''',states)

crops = [
    ('Wheat',     'Cereal',     'Rabi'),
    ('Rice',      'Cereal',     'Kharif'),
    ('Maize',     'Cereal',     'Kharif'),
    ('Cotton',    'Cash Crop',  'Kharif'),
    ('Sugarcane', 'Cash Crop',  'Annual'),
    ('Soybean',   'Oilseed',    'Kharif'),
    ('Mustard',   'Oilseed',    'Rabi'),
    ('Potato',    'Vegetable',  'Rabi'),
]
cursor.executemany('''
                   INSERT OR IGNORE INTO crops (name,category,season) 
                   VALUES (?,?,?)''',crops)


conn.commit()

# Generate Realistic Production Data

np.random.seed(42)
production_data = []
states_ids = list(range(1,13))
crop_ids = list(range(1,9))
years = [2019,2020,2021,2022,2023]

base_yield = {
    1: 4800,
    2: 3200,
    3: 2800,
    4: 1500,
    5: 7200,
    6: 1800,
    7: 1200,
    8: 22000
}

for state_id in states_ids:
    for crop_id in crop_ids:
        for year in years:
            
            area = np.random.uniform(50000, 800000)
            yield_base = base_yield[crop_id]
            yield_val = yield_base * np.random.uniform(0.8, 1.3)
            production = (area * yield_val) / 100
            
            production_data.append((
                state_id,
                crop_id,
                year,
                round(area,2),
                round(production,2),
                round(yield_val,2)
            ))
            

cursor.executemany('''
                   INSERT INTO production(
                       state_id,crop_id, year, area_ha, production_mt, yield_kg_ha
                   )
                   VALUES (?,?,?,?,?,?)
                   ''', production_data)

conn.commit()
print(f'Inserted {len(production_data)} production records!')



# SQL Analysis Queries
 
print("\n" + "="*60)
print("SQL ANALYSIS")
print("="*60)           

# Top production states overall

print('\n 1. Top 5 states by total production:')

cursor.execute('''
               SELECT s.name, ROUND(SUM(p.production_mt)/1000000,2) AS total_mt_million
               FROM states s
               INNER JOIN production p 
               ON s.id = p.state_id
               GROUP BY s.id, s.name
               ORDER BY total_mt_million DESC
               LIMIT 5
               ''')

for row in cursor.fetchall():
    print(f'{row[0]:20s} : {row[1]} million MT')
    

# BEST crop by yield

print('\n 2. Average yield by crop')

cursor.execute('''
               SELECT c.name, c.category,
               ROUND(AVG(p.yield_kg_ha),0) AS avg_yield
               FROM crops c
               INNER JOIN production p 
               ON c.id = p.crop_id
               GROUP BY c.id, c.name
               ORDER BY avg_yield DESC
               ''')

for row in cursor.fetchall():
    print(f"  {row[0]:12s} ({row[1]:10s}): {row[2]} kg/ha")




# Region-wise performance
print("\n3. Region-wise production:")
cursor.execute('''
    SELECT s.region,
           COUNT(DISTINCT s.id)            AS states,
           ROUND(AVG(p.yield_kg_ha), 0)    AS avg_yield,
           ROUND(SUM(p.production_mt)/1e6, 2) AS total_million_mt
    FROM states s
    INNER JOIN production p ON s.id = p.state_id
    GROUP BY s.region
    ORDER BY total_million_mt DESC
''')
for row in cursor.fetchall():
    print(f"  {row}")
    
    

# Year on year trend
print("\n4. Year-wise production trend:")
cursor.execute('''
    SELECT year,
           ROUND(SUM(production_mt)/1e6, 2) AS total_million_mt,
           ROUND(AVG(yield_kg_ha), 0)        AS avg_yield
    FROM production
    GROUP BY year
    ORDER BY year
''')
for row in cursor.fetchall():
    print(f"  {row}")
    
    

# States above average yield
print("\n5. States above average yield:")
cursor.execute('''
    SELECT s.name, ROUND(AVG(p.yield_kg_ha), 0) AS avg_yield
    FROM states s
    INNER JOIN production p ON s.id = p.state_id
    GROUP BY s.id, s.name
    HAVING AVG(p.yield_kg_ha) > (
        SELECT AVG(yield_kg_ha) FROM production
    )
    ORDER BY avg_yield DESC
''')
for row in cursor.fetchall():
    print(f"  {row[0]:20s}: {row[1]} kg/ha")


# Load into pandas and Visualize:

print("\n" + "="*60)
print("PANDAS + VISUALIZATION")
print("="*60)

# LOAD full joined dataset

df = pd.read_sql('''
                 SELECT 
                 s.name AS state,
                 s.region,
                 c.name AS crop,
                 c.category,
                 c.season,
                 p.year,
                 p.area_ha,
                 p.production_mt,
                 p.yield_kg_ha
                 FROM production p
                 INNER JOIN states s
                 ON p.state_id = s.id
                 INNER JOIN crops c
                 ON p.crop_id = c.id
                 ''', conn)

print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(df.head())

# DASHBOARD
fig, axes = plt.subplots(2,2, figsize = (16,12))
fig.suptitle('India Agriculture Analysis Dashboard',
             fontsize = 16, fontweight = 'bold')



# CHART 1 - Top states by production

state_prod = df.groupby('state')['production_mt'].sum().sort_values(ascending=True).tail(8)

axes[0,0].barh(state_prod.index, state_prod.values / 1e6, color = 'steelblue')
axes[0,0].set_title('Top 8 States by Total Production')
axes[0,0].set_xlabel('Production (Million MT)')



# Chart 2 - Crop category breakdown
cat_prod = df.groupby('category')['production_mt'].sum()

axes[0,1].pie(cat_prod.values, labels = cat_prod.index,     
              autopct = '%1.1f%%', startangle=90)
axes[0,1].set_title('Production by Crop Category')



# Chart 3 — Yield trend over years
year_yield = df.groupby(['year', 'category'])['yield_kg_ha'].mean().unstack()

for col in year_yield.columns:
    axes[1,0].plot(year_yield.index, year_yield[col],
                   marker='o', label=col, linewidth=2)
    
axes[1,0].set_title('Average Yield Trend by Category')
axes[1,0].set_xlabel('Year')
axes[1,0].set_ylabel('Yield (kg/ha)')
axes[1,0].legend(fontsize=8)



# Chart 4 — Region comparison heatmap
region_crop = df.groupby(['region', 'crop'])['yield_kg_ha'].mean().unstack()

sns.heatmap(region_crop.round(0), annot=True, fmt='.0f',
            cmap='YlOrRd', ax=axes[1,1], linewidths=0.5)

axes[1,1].set_title('Average Yield by Region and Crop')
axes[1,1].tick_params(axis='x', rotation=45)



plt.tight_layout()
plt.savefig('agriculture_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()
print("Dashboard saved!")

# Save final report to SQL
summary = df.groupby(['state', 'crop']).agg({
    'production_mt': 'sum',
    'yield_kg_ha': 'mean',
    'area_ha': 'sum'
}).round(2).reset_index()

summary.to_sql('production_summary', conn, if_exists='replace', index=False)
print(f"Summary table saved to SQL ({len(summary)} rows)")

conn.close()