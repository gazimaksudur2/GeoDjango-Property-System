# GeoProperty: Spatial & Semantic Real Estate Discovery Engine

GeoProperty is a GeoDjango, PostGIS, and `pgvector` discovery platform that unifies geodesic spatial queries with local dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) inside a single PostgreSQL 16 engine.

---

## Core Architectural Decisions & Solutions

### 1. Unified Spatial + Vector Storage in PostgreSQL
* **Decision:** Build a custom Docker image atop `pgvector/pgvector:pg16` with `postgresql-16-postgis-3` installed instead of splitting state across a relational DB and an external vector store.
* **Solution:** `0001_initial.py` provisions both `CreateExtension("postgis")` and `VectorExtension()`. This allows single-query execution combining PostGIS spatial predicates (`DWithin`, `Distance`, `Contains`) with `pgvector` cosine distance (`<=>`) without cross-service network latency.

### 2. Geodesic Coordinate Modeling (`geography=True`, SRID 4326)
* **Decision:** Store `Location.point` and `Property.point` as `PointField(geography=True, srid=4326)` alongside `MultiPolygonField` (`Location.boundary`) and `PolygonField` (`Property.footprint`).
* **Solution:** Enabling `geography=True` calculates distances over the WGS 84 spheroid in meters/kilometers rather than planar Euclidean degrees, ensuring accurate radius filtering (`D(km=radius_km)`) and distance annotations.

### 3. In-Process Embedding Singleton & HNSW Indexing
* **Decision:** Generate 384-dimensional embeddings locally via `all-MiniLM-L6-v2` and index them with PostgreSQL HNSW indexes.
* **Solution:**
  * **Process Caching:** `properties/utils/embeddings.py` caches `SentenceTransformer("all-MiniLM-L6-v2")` with `@lru_cache(maxsize=1)` so model weights load only once per worker process.
  * **Context-Enriched Prompts:** Management commands (`generate_location_embeddings`, `generate_property_embeddings`) synthesize structured natural-language profiles (combining title, neighborhood, city, property type, bed/bath counts, and description) prior to encoding.
  * **Sub-Linear ANN Search:** Both `Location` and `Property` models define an `HnswIndex` (`m=16`, `ef_construction=64`, `opclasses=["vector_cosine_ops"]`) to accelerate `CosineDistance` queries.

### 4. Dual-Mode Hybrid Search Pipeline
The search engine (`property_list` view and `static/js/location_autocomplete.js`) separates user intent into two retrieval pipelines via a frontend toggle:

| Mode | Retrieval & Ranking Pipeline | Spatial Distance Anchor |
| :--- | :--- | :--- |
| **Location Mode** (`search_type=location`) | **3-Tier Location Resolution:** Attempts exact ID match (`target_id`), falls back to `icontains` on `name`/`city`, and finally falls back to vector similarity (`CosineDistance <= 0.55`). Filters properties via `point__dwithin=(matched_location.point, D(km=radius_km))` or foreign key relation. | Annotates `search_distance` from `matched_location.point` and sorts by `(search_distance, similarity)`. |
| **Property Mode** (`search_type=property`) | **Hybrid Lexical + Vector Retrieval:** Matches active properties via `target_id`, substring (`title`, `description`, `property_type`), or vector similarity (`CosineDistance <= 0.68`). Uses a SQL `Case/When` expression (`exact_boost`) to pin exact matches before ordering by cosine distance. | Resolves the top or selected property (`matched_property`) and annotates `search_distance` from `matched_property.point` for all results. |

### 5. Context-Aware Spatial Distance & Nearby Engine
* **Listing Cards:** Dynamically display `search_distance` relative to the active search anchor (`matched_location` or `matched_property`), falling back to `city_distance` (`Distance("point", "location__point")`) when browsing unfiltered listings.
* **Detail Page Nearby Recommendations:** `property_detail` executes a PostGIS nearest-neighbor lookup (`exclude(id=property_obj.id).annotate(search_distance=Distance("point", property_obj.point)).order_by("search_distance")[:3]`) to display the 3 closest properties with exact kilometer offsets.

### 6. Low-Latency Hybrid Autocomplete & Input Validation
* **Debounced Dual-Endpoint Autocomplete:** Frontend debouncing (`300ms`) routes requests to `/api/v1/locations/autocomplete/` or `/api/v1/properties/autocomplete/`. Each endpoint validates parameters via `AutocompleteQuerySerializer`, prioritizes fast `icontains` lexical matches, excludes seen IDs, and backfills remaining slots using `pgvector` `CosineDistance`.
* **Two-Layer Validation:** `PropertySearchForm` enforces search mode, regex character whitelisting, radius bounds (`0.5`–`100` km), and min/max price cross-validation on HTML views, while DRF serializers validate coordinate bounds (`-180..180`, `-90..90`), positive pricing/area, and residential bedroom rules on API payloads.

### 7. Idempotent Data Ingestion & Admin GIS Tooling
* **Transactional ETL Commands:** `import_locations`, `import_properties`, and `import_property_images` sanitize CSV `NaN` values with Pandas, construct `Point(lng, lat, srid=4326)` geometries, cache remote Unsplash image downloads in memory, and execute inside `@transaction.atomic` blocks using `update_or_create`.
* **GIS Admin & Custom Filters:** Configured with `GISModelAdmin` map widgets, custom `PriceRangeFilter` and `EmbeddingStatusFilter` classes, and `PropertyImageInline` with HTML thumbnail previews.

---

## Quick Start

### First-time setup

Prerequisites: Docker Compose and [uv](https://docs.astral.sh/uv/).

```bash
# 1. Build and start PostgreSQL 16 with PostGIS 3 and pgvector
docker compose up -d --build

# 2. Create the virtual environment and install project dependencies
uv sync

# 3. Apply database migrations
uv run python manage.py migrate

# 4. Create an admin account (one time)
uv run python manage.py createsuperuser

# 5. Import the included CSV data
uv run python manage.py import_locations
uv run python manage.py import_properties
uv run python manage.py import_property_images

# 6. Generate embeddings for semantic search
uv run python manage.py generate_location_embeddings
uv run python manage.py generate_property_embeddings
```

Use a strong password when prompted by `createsuperuser`; Django may ask whether to bypass validation for weak passwords. For normal use, do not bypass it.

### Run and maintain the project

```bash
# Start the database after initial setup, if it is not already running
docker compose up -d

# Apply any new migrations
uv run python manage.py migrate

# Run the test suite
uv run python manage.py test

# Start the development server
uv run python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the site or `http://127.0.0.1:8000/admin/` for the Django admin. The database container can be stopped with `docker compose down`; its data is retained in the Compose volume.

---

## API Reference (`/api/v1/`)

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/v1/locations/` | `GET, POST` | CRUD operations for locations with coordinate validation |
| `/api/v1/locations/autocomplete/?q=<str>&limit=8` | `GET` | Hybrid lexical + `pgvector` location autocomplete |
| `/api/v1/locations/semantic_search/?q=<str>` | `GET` | Top 10 locations ranked by `CosineDistance` |
| `/api/v1/properties/` | `GET, POST` | Filterable/searchable property CRUD (`property_type`, `status`, `bedrooms`, `price`) |
| `/api/v1/properties/autocomplete/?q=<str>&limit=8` | `GET` | Hybrid lexical + `pgvector` property autocomplete |
| `/api/v1/properties/nearby/?lng=<x>&lat=<y>&radius=5` | `GET` | PostGIS `distance_lte` spatial radius filtering |
| `/api/v1/properties/nearest/?lng=<x>&lat=<y>` | `GET` | Single closest property using PostGIS `Distance` |
| `/api/v1/properties/contains/?lng=<x>&lat=<y>` | `GET` | Properties whose `footprint` polygon contains the given point |
| `/api/v1/properties/semantic_search/?q=<str>` | `GET` | Top 10 properties ranked by `CosineDistance` |
| `/api/v1/properties/hybrid_search/?q=<str>&lng=<x>&lat=<y>&radius=5` | `GET` | Spatial radius filter combined with vector similarity ranking |
| `/api/v1/properties/location_hybrid_search/?q=<str>` | `GET` | Resolves semantic location first, then ranks its properties by vector similarity |
