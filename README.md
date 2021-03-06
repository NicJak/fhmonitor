# File History Monitor
A tool to monitor File History from server. The tool calls a defined HTTP address whenever a change occurs. Services such as https://healthchecks.io (see picture below) can be configured to send E-Mail / Instant Messaging messages when a timeout between backups has occured.

### Overview from Healthchecks.io
![](https://raw.githubusercontent.com/NicJak/fhmonitor/main/images/healthchecks.png)
### Telegram Alert
![](https://raw.githubusercontent.com/NicJak/fhmonitor/main/images/telegram.png)

## Config
A JSON array in which pairs of path and URL are defined. Usually the directory structure follows the pattern [base]/[windows-username].

### Sample

```
[
    {
        "path": "/markus/markus@domain.com",
        "url": "https://hc-ping.com/00000000-1111-2222-3333-444444444444"
    },
    {
        "path": "/peter/peter",
        "url": "https://hc-ping.com/55555555-6666-7777-8888-999999999999"
    }
]
```

## Usage

### Python
Python and all libraries in requirements.txt are required.

```
pip install -r requirements.txt
```

```
python fhmonitor.py /path/to/config.json
```

### Docker

```
version: "3.8"

services:
  fhmonitor:
    image: nicjak/fhmonitor
    container_name: fhmonitor
    volumes:
      - /path/to/config:/config
      - /path/to/backups:/backups
    restart: unless-stopped
```