# Smart Plant Health Monitor App - Server
Server is hosted on https://muc-server.onrender.com

## Endpoints:
### GET:
- `/` - home page, nothing here really
- `/data` - retrieve all the data in the database  
You can optionally add a startDate and/or endDate parameter to filter by dates. E.g., to filter between April 5 (inclusive) and April 7 (exclusive): https://muc-server.onrender.com/data?startDate=2026-04-05&endDate=2026-04-07
- `/data/latest` - retrieve the most recent entry in the database
- `/data/<field>` specify a field to filter data by (temperature, humidity, light, moisture)  
You can optionally add a startDate parameter to filter for data after a certain date, e.g.:
https://muc-server.onrender.com/data/humidity?startDate=2026-04-06 - This returns all the entries from April 6, 2026 onwards.

### POST:
- `/data` - post a new entry to the database. Requires the correct API key for writing to the API. Not for external use, only for ESP32 to send sensor data to the server.
