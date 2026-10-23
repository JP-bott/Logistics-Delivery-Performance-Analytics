<img src="assets/nexroute_logo.svg" width="380" alt="NexRoute Logistics Intelligence"/>

# Logistics & Delivery Performance Intelligence

**Author:** John Paul Torres · **License:** MIT · **Stack:** Python, pandas, NumPy, SQLite, Plotly, Streamlit, GeoPandas and SQL.

NexRoute is a **fictional Philippine logistics company**, designed as a junior data analyst / BI portfolio project. Its dashboard investigates synthetic shipment volumes, delivery reliability, courier productivity, regional geospatial patterns, delivery exceptions and shipping economics for **January 2024 through December 2025**. All costs, couriers, facilities and delivery transactions are simulated, not real carrier data.

## Quick start

In GitHub Codespaces, create a Codespace on `main`, allow the configured Python environment to install dependencies, then run:

```bash
python scripts/generate_data.py
python scripts/load_database.py
streamlit run app.py
```

Open the forwarded **8501** port. The same commands run in a local Python 3.11+ environment after `python -m pip install -r requirements.txt`. The SQLite database and large generated CSVs are **generated on demand**, not checked into this source repository. The downloadable complete ZIP in the associated ChatGPT conversation additionally contains the prebuilt database and full generated datasets.

## Dashboard sections

| Workspace | Visuals and business questions |
| --- | --- |
| Operations Overview | Shipment counts, success and on-time KPI cards, rolling-volume trends, regional SLA heatmap and waterfall |
| Geographic Delivery Analysis | Offline-capable Philippine city-center scatter map, origin/destination corridors and regional comparison |
| Courier Performance | Courier rankings with minimum-volume threshold, workload comparison and vehicle delivery distribution |
| SLA & Delay Analytics | SLA KPI cards, late-delivery histogram, service-region matrix, failure reasons, Pareto |
| Shipping Cost Analysis | Cost trends, geodesic distance correlation, cost distribution and route benchmarking |
| Shipment Explorer | Shipment lookup, filtered CSV download and actual generated tracking-event chronology |

The project includes six operational SQL files demonstrating relational JOINs, aggregations, CTEs and window functions; a reproducible analysis notebook; a fixed-seed data generator; a normalized database schema; and data integrity tests. All views use interactive sidebar filters for date, region, courier, service and delivery status.

## Data model

Regenerate approximately **26,000 synthetic shipments**, **60 fictional couriers**, **12 fictional hubs**, **114 route/service SLA rules**, and a detailed event history. Fixed generator seed: `20261107`. Source CSVs live in `data/raw/` after running the generator, and the database is created at `database/logistics_analytics.db`.

```text
shipments.Courier_ID      → couriers.Courier_ID
shipments.Origin_Hub_ID   → hubs.Hub_ID
shipments.SLA_ID          → sla_rules.SLA_ID
delivery_events.Shipment_ID → shipments.Shipment_ID
delivery_events.Hub_ID   → hubs.Hub_ID
```

SQL schema definitions are in `sql/01_create_tables.sql` with secondary indexes in `sql/02_create_indexes.sql`.

## KPI definitions

- **Success rate:** Delivered / (Delivered + Failed + Returned). In-transit and cancelled parcels are excluded.
- **On-time rate:** delivered on/before expected date / delivered, not all shipments.
- **First-attempt success:** delivered with exactly one delivery attempt / all delivered.
- **Average delivery time:** mean calendar days between dispatch and actual delivery, delivered only.
- **SLA days:** calendar days from dispatch. Same Day applies to intra-region trips.
- **Reporting cutoff:** December 31, 2025, Philippine local date. Incomplete shipments are not automatically counted as failed.

## Assumptions, geographic limits and ethical use

Destinations use representative city-center WGS84 latitude/longitude coordinates, not true delivery addresses or personal location records. Distances are **straight-line geodesics**, not road or travel-time measurements. Route flow lines are aggregated conceptual connections. No administrative boundary polygons are fabricated and no live basemap API is required. Simulated shipping costs depend on route distance, parcel weight, service, vehicle, island factor and noise, so observed correlations in this synthetic dataset must not be described as real-world causal evidence. The fictional operations model is intended for analytics practice, not actual shipping quotes or policy decisions.

## Notebook and validation

```bash
python -m pytest tests -q
jupyter lab
```

Open `notebooks/logistics_delivery_analysis.ipynb` to inspect data cleaning, database joins, KPIs, geospatial aggregation, service performance and cost relationships. A GitHub Actions workflow regenerates the database, runs tests and compiles source after commits to main. The checked-in project is source-first; the local ZIP has additional generated assets and a populated database.

**© 2026 John Paul Torres.** MIT License.
