# Google Cloud

## Google Cloud Architecture
```
--------------------------------          --------------------------------
| Public API                   |   ----- | BUCKET - Static Website      | 
--------------------------------          --------------------------------
            |
            | Exposes
            |
------------------------------------------------------
| SQL Database - Vector, tabular, flat file metadata |
-----------------------------------------------------
            |
            | References
            |
------------------------------------------
| BUCKET Flat files - imagery, pdfs, etc |
------------------------------------------
```

## PostgreSQL Database
- Hosted SQL Database named: `con000000109891-henn-carbon`
- Access credentials [here](https://docs.google.com/document/d/1ca5OP9XyRljkjH5VlIX6eIA1c9lDHD4E5JH1L6126TY/edit?tab=t.0)
- IP Ranges restricted to UMN network
- To Do:
  - Role-based access control for apps, etl, etc.
  - Grant minimal privileges:
    ```
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_read;
    GRANT INSERT, UPDATE, DELETE ON TABLE my_table TO app_write;
    ```

## Cloud Storage Bucket
- Hosted storage buckets:
  - Flat data assets: `con000000109891-henn-carbon-data` (Private)
  - Website: `con000000109891-henn-carbon-website` (Public at https://storage.googleapis.com/con000000109891-henn-carbon-website/)
- To Do:
  - Create custom domain -- impacts.runcklab.com

## 
