# GeoProperty System: Enterprise Location-Aware Property Discovery Platform

A production-ready real estate and vacation rental discovery platform built with **Django 4.2**, **GeoDjango**, **PostGIS**, and **pgvector**. The system combines **geospatial queries** (PostGIS `DWithin` and `Distance`) with **AI-powered semantic vector search** (`sentence-transformers/all-MiniLM-L6-v2` and `pgvector` HNSW indexing) and features an interactive **Location vs. Property Dual-Mode Search Toggle**.

---

## Core Features

* **Dual-Mode Search Toggle (`Location` vs. `Property`)**:
  * **Location Mode**: Autocompletes locations via `/api/v1/locations/autocomplete/` (hybrid exact + `pgvector` cosine similarity) and executes a PostGIS `DWithin` + `Distance` radius search anchored at the matched location's coordinates.
  * **Property Mode**: Autocompletes properties directly via `/api/v1/properties/autocomplete/` and ranks listings using `pgvector` `CosineDistance` semantic similarity plus keyword relevance.
* **Geographic & Spatial Property Search**: Powered by PostGIS and GeoDjango `PointField` coordinates (`SRID 4326`) supporting radius filtering (`DWithin`), city-center distance annotations (`Distance`), and nearest-neighbor lookups.
* **AI-Powered Semantic & Hybrid Search**: Generates 384-dimensional text embeddings using `sentence-transformers/all-MiniLM-L6-v2`, indexed with HNSW indexes (`vector_cosine_ops`) in `pgvector`.
* **Automated Pandas Data Pipeline**: Custom Django management commands leveraging `pandas` for cleaning and importing locations, properties, and property images from CSV files.
* **Advanced Django Admin**: Configured with `GISModelAdmin`, custom `PriceRangeFilter` and `EmbeddingStatusFilter` list filters, and `PropertyImageInline` with HTML thumbnail previews.
* **Django Forms & DRF APIs**: Frontend `PropertySearchForm` with custom validation (`clean_search_type`, `clean_location`, `clean_radius`, `clean`) alongside a Django REST Framework (DRF) API suite with serializer payload validation.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.12, Django 4.2, Django REST Framework (DRF) |
| **Database** | PostgreSQL 16, PostGIS 3, pgvector (HNSW Indexing) |
| **AI / ML** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **GIS** | GeoDjango, Spatial Operations (`DWithin`, `Distance`, `Contains`) |
| **Frontend** | Django Templates, Tailwind CSS, Dual-Mode Vanilla JS Autocomplete |
| **Infrastructure** | Docker, Docker Compose, Pandas |

---

## API Endpoints Reference

Base URL: `/api/v1/`

* **Location Autocomplete (Toggle = Location)**: `GET /api/v1/locations/autocomplete/?q=gul`
* **Property Autocomplete (Toggle = Property)**: `GET /api/v1/properties/autocomplete/?q=luxury`
* **Semantic Location Search**: `GET /api/v1/locations/semantic_search/?q=residential+area+near+dhaka`
* **Property List / Filters**: `GET /api/v1/properties/`
* **Semantic Property Search**: `GET /api/v1/properties/semantic_search/?q=luxury+apartment`
* **Nearby Properties (Radius)**: `GET /api/v1/properties/nearby/?lng=90.4078&lat=23.7925&radius=10`
* **Nearest Property Lookup**: `GET /api/v1/properties/nearest/?lng=90.4078&lat=23.7925`
* **Fused Hybrid Search**: `GET /api/v1/properties/hybrid_search/?q=luxury+apartment&lng=90.4078&lat=23.7925&radius=10`

# GeoProperty System: Enterprise Location-Aware Property Discovery Platform

A modern, production-ready real estate discovery platform built with **Django 4.2**, **GeoDjango**, **PostGIS**, and **pgvector**. The system seamlessly blends **spatial geospatial queries** (PostGIS) with **AI-powered semantic vector search** (`sentence-transformers` and `pgvector`) to allow users to discover properties via geographic proximity, natural language queries, and precise property filters.

---

## 🌟 Core Features

* **Geographic & Spatial Property Search**: Powered by PostGIS and GeoDjango `PointField` coordinates (`SRID 4326`) supporting radius filtering (`DWithin`), distance annotations, and nearest-neighbor lookups.


* **AI-Powered Semantic & Hybrid Search**: Generates 384-dimensional text embeddings using `sentence-transformers/all-MiniLM-L6-v2`, indexed with HNSW indexes in `pgvector` for lightning-fast cosine similarity vector searches.


* **Robust Data Pipeline**: Automated bulk CSV data ingestion via custom Django management commands leveraging `pandas` for locations, properties, and property images.


* **Advanced Django Admin**: Fully configured with `GISModelAdmin` OpenStreetMap integrations, custom price range & embedding status list filters, and inline image uploads featuring rendered HTML thumbnail previews.


* **Django Forms & DRF APIs**: Secure frontend search forms with custom input sanitization & validation, alongside a complete Django REST Framework (DRF) API suite featuring field-level and object-level payload validations.


* **Responsive User Interface**: Built with Tailwind CSS and JavaScript autocomplete, ensuring seamless pagination and query-string preservation across search and detail views.



---

## 🛠️ Technology Stack

| Layer | Technologies |
| --- | --- |
| **Backend** | Python 3.12, Django 4.2, Django REST Framework (DRF)

 |
| **Database** | PostgreSQL 16, PostGIS 3, pgvector (HNSW Indexing)

 |
| **AI / ML** | Sentence-Transformers (`all-MiniLM-L6-v2`)

 |
| **GIS** | GeoDjango, Spatial Vector Operations (`DWithin`, `Distance`)

 |
| **Frontend** | Django Templates, Tailwind CSS, JavaScript Autocomplete

 |
| **Infrastructure** | Docker, Docker Compose, Pandas

 |

---

## 📁 Project Architecture

```text
GeoDjango_Property_System
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── properties/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── api/
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── management/
│   │   └── commands/
│   │       ├── import_locations.py
│   │       ├── import_properties.py
│   │       ├── import_property_images.py
│   │       ├── generate_location_embeddings.py
│   │       └── generate_property_embeddings.py
│   ├── services/
│   │   └── search.py
│   ├── utils/
│   │   └── embeddings.py
│   └── migrations/
│
├── data/
│   ├── locations.csv
│   ├── properties.csv
│   └── property_images.csv
│
├── static/
│   └── js/
│       └── location_autocomplete.js
│
├── templates/
│   ├── base.html
│   ├── home/
│   │   └── index.html
│   └── properties/
│       ├── listing.html
│       ├── detail.html
│       └── components/
│           ├── property_card.html
│           ├── search_box.html
│           └── pagination.html
│
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md

```

---

## 🗄️ Database Models

1. **`Location`**: Stores geographic regions (neighborhoods, cities, states) complete with PostGIS point coordinates and 384-dimensional semantic text embeddings.


2. **`Property`**: Stores real estate listings with pricing, specifications (bedrooms, bathrooms, area), active status, geographic points, and semantic vector representations.


3. **`PropertyImage`**: Stores associated property photos and metadata linked to properties for gallery rendering and admin inline previews.



---

## 🚀 Installation & Setup Guide

### 1. Clone the Repository

```bash
git clone <repository-url>
cd GeoDjango_Property_System

```

### 2. Install Dependencies

Using `uv` or `pip`:

```bash
uv install -r requirements.txt

```

### 3. Start PostgreSQL + PostGIS + pgvector (Docker)

```bash
docker compose up -d

```

### 4. Run Database Migrations

```bash
python manage.py migrate

```

### 5. Import Bulk CSV Data

Run the custom management commands sequentially to ingest locations, properties, and images:

```bash
python manage.py import_locations
python manage.py import_properties
python manage.py import_property_images

```

### 6. Generate AI Embeddings

Run the embedding generators to compute vector representations for semantic search:

```bash
python manage.py generate_location_embeddings
python manage.py generate_property_embeddings

```

### 7. Run the Development Server

```bash
python manage.py runserver

```

Access the application at: `[http://127.0.0.1:8000/](http://127.0.0.1:8000/)`

---

## 🔌 API Endpoints Reference

Base URL: `/api/v1/`

* **Location Autocomplete**: `GET /api/v1/locations/autocomplete/?q=gul`

* **Semantic Location Search**: `GET /api/v1/locations/semantic_search/?q=residential+area+near+dhaka`

* **Property List / Filters**: `GET /api/v1/properties/`

* **Semantic Property Search**: `GET /api/v1/properties/semantic_search/?q=luxury+apartment`

* **Nearby Properties (Radius)**: `GET /api/v1/properties/nearby/?lng=90.4078&lat=23.7925&radius=10`

* **Nearest Property Lookup**: `GET /api/v1/properties/nearest/?lng=90.4078&lat=23.7925`

* **Fused Hybrid Search**: `GET /api/v1/properties/hybrid_search/?q=luxury+apartment&lng=90.4078&lat=23.7925&radius=10`

