# Smart Plant Health Monitor App - Server
Server is hosted on https://muc-server.onrender.com

## Endpoints:
### GET:
- `/` - home page, nothing here really
- `/data` - retrieve all the data in the database
- `/data/latest` - retrieve the most recent entry in the database
- `/data/<field>` specify a field to filter data by (temperature, humidity, light, moisture)
You can optionally add a startDate parameter to filter for data after a certain date, e.g.:
https://muc-server.onrender.com/data/humidity?startDate=2026-03-08T00:00:00 - This returns all the entries from March 8, 2026 onwards.

### POST:
- `/data` - post a new entry to the database. Requires the correct API key for writing to the API. Not for external use, only for ESP32 to send sensor data to the server.