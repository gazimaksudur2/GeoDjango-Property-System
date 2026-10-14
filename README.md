# GeoProperty System

A location-aware property discovery platform built with **Django**, **GeoDjango**, **PostGIS**, and **pgvector**.

The system combines:

- Geographic search using PostGIS
- Semantic property search using vector embeddings
- Location intelligence
- Property recommendation foundations
- REST APIs for frontend/mobile integration

The goal is to build a modern real-estate search engine where users can discover properties based on:

- Location
- Distance
- Natural language queries
- Property characteristics
- Similarity relationships

---

# Features

## Geographic Property Search

Powered by:

- GeoDjango
- PostGIS
- Geographic PointField

Each location and property stores real coordinates:

```
Latitude
Longitude
SRID 4326
```

Supported spatial operations:

- Nearby properties
- Distance calculation
- Nearest property lookup
- Radius-based filtering

---

## Semantic Search with AI Embeddings

The project uses:

```
sentence-transformers/all-MiniLM-L6-v2
```

to generate 384-dimensional embeddings.

Embeddings are stored using:

```
pgvector
```

with HNSW indexes for efficient similarity search.

Supported semantic queries:

Example:

```
luxury apartment near Gulshan
```

or

```
family home with modern facilities
```

The system understands meaning instead of only matching keywords.

---

# Technology Stack

## Backend

- Python 3.12
- Django 4.2
- Django REST Framework

## Database

- PostgreSQL
- PostGIS
- pgvector

## AI / ML

- Sentence Transformers
- Vector similarity search

## GIS

- GeoDjango
- Spatial queries
- Geographic indexing

## Frontend

- Django Templates
- Tailwind CSS
- JavaScript autocomplete

## Infrastructure

- Docker
- Docker Compose

---

# Project Architecture

```
GeoDjango_Property_System

│
├── config
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── properties
│
│   ├── models.py
│   │
│   │   ├── Location
│   │   ├── Property
│   │   └── PropertyImage
│   │
│   ├── api
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   ├── services
│   │   └── search.py
│   │
│   ├── utils
│   │   ├── embeddings.py
│   │   └── image_embeddings.py
│   │
│   ├── management
│   │   └── commands
│   │       ├── import_locations.py
│   │       ├── import_properties.py
│   │       ├── generate_location_embeddings.py
│   │       └── generate_property_embeddings.py
│   │
│   └── migrations
│
├── data
│   ├── locations.csv
│   ├── properties.csv
│   └── property_images.csv
│
├── static
│   └── js
│       └── location_autocomplete.js
│
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

---

# Database Models

## Location

Stores geographic areas.

Contains:

- Name
- Address
- City
- Country
- Geographic point
- Semantic embedding


Example:

```
Gulshan
Dhaka
Bangladesh
```

---

## Property

Stores real-estate listings.

Contains:

- Title
- Description
- Type
- Status
- Price
- Bedrooms
- Bathrooms
- Area
- Location relationship
- Geographic point
- Semantic embedding


Example:

```
Modern Luxury Apartment

3 bedrooms
1800 sqft
Gulshan, Dhaka
```

---

## PropertyImage

Stores property images and supports future visual similarity search.

Contains:

- Image
- Caption
- Metadata
- Image embedding

---

# Data Import

The project supports CSV-based data loading.

## Import locations

```
python manage.py import_locations
```

Loads:

```
data/locations.csv
```

Creates geographic Location objects.

---

## Import properties

```
python manage.py import_properties
```

Loads:

```
data/properties.csv
```

Creates properties linked with locations.

---

# Generate Embeddings

## Location embeddings

```
python manage.py generate_location_embeddings
```

Creates semantic vectors for:

- Neighborhoods
- Cities
- Real estate context


---

## Property embeddings

```
python manage.py generate_property_embeddings
```

Creates semantic vectors from:

- Title
- Description
- Property type
- Location context

---

# API Endpoints

Base URL:

```
/api/v1/
```

---

# Location APIs

## Location autocomplete

```
GET

/api/v1/locations/autocomplete/?q=gul
```

Returns matching locations.

---

## Semantic location search

```
GET

/api/v1/locations/semantic_search/?q=residential area near dhaka
```

Uses embeddings.

---

# Property APIs

## Property list

```
GET

/api/v1/properties/
```

---

## Semantic property search

```
GET

/api/v1/properties/semantic_search/?q=luxury apartment
```

---

## Nearby properties

Example:

```
GET

/api/v1/properties/nearby/?lng=90.4078&lat=23.7925
```

Returns properties inside a geographic radius.

---

## Nearest property

```
GET

/api/v1/properties/nearest/?lng=90.4078&lat=23.7925
```

Returns closest property.

---

## Hybrid search

Combines:

- Semantic similarity
- Geographic filtering


Example:

```
GET

/api/v1/properties/hybrid_search/?q=luxury apartment&lng=90.4078&lat=23.7925
```

---

# Running the Project

## Clone repository

```
git clone <repository-url>

cd GeoDjango_Property_System
```

---

## Create environment

Using uv:

```
uv sync
```

or:

```
pip install -r requirements.txt
```

---

## Environment variables

Create:

```
.env
```

from:

```
.env.example
```

---

## Start PostgreSQL + PostGIS

```
docker compose up -d
```

---

## Run migrations

```
python manage.py migrate
```

---

## Import initial data

```
python manage.py import_locations

python manage.py import_properties
```

---

## Generate embeddings

```
python manage.py generate_location_embeddings

python manage.py generate_property_embeddings
```

---

## Start development server

```
python manage.py runserver
```

Application:

```
http://127.0.0.1:8000/
```

---

# Future Improvements

Planned features:

## Advanced Ranking

Combine:

```
semantic similarity
+
distance
+
property quality
+
featured score
```

---

## Recommendation Engine

Examples:

```
Similar properties
Recently viewed properties
User preference matching
```

---

## Image-Based Search

Using CLIP embeddings:

Example:

Upload:

```
modern white kitchen
```

Find visually similar properties.

---

## More GIS Features

Future additions:

- Polygon boundaries
- Neighborhood maps
- Heat maps
- Nearby amenities
- Travel distance

---

# License

This project is currently developed for educational and experimental purposes.
