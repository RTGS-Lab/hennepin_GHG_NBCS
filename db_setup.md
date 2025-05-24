# SQL Database Setup

Database setup was done using DBeaver and Google Cloud's SQL Studio in browser. 

0. Create databases `henn-management-units` and `henn-management-units-test`
Done through browser.

2. Enable PostGIS and pgvector for embeddings
```
create extension postgis;
create extension postgis_topology;
create extension vector;
```

3. Create the schema
Using the Google Cloud SQL Studio editor. Execute:
```

```
