# AmazeScrape - A Python Web Scraper :snake:

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Scrapy](https://img.shields.io/badge/scrapy-2.11.0-blue.svg)](https://scrapy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description :page_facing_up:

A web scraper that is simply amazing...

### Proxy Rotation :arrows_counterclockwise:

Currently, there is no proxy rotation implemented. However, it is planned to be implemented in the future.

### Random User Agent :bust_in_silhouette:

This project uses a random user agent to avoid being banned by the websites that we're scraping.

### Random Call Interval :alarm_clock:

This project uses a random call interval to avoid being banned by the websites that we're scraping.

### Database :floppy_disk:

Scraped information are stored in a database. Currently, the database used is SQLite.

## Installation :computer:

Download the project using git clone. You can clone the project wherever you want. In this case, we're going to clone it in the `/home/pi` folder.

```sh
cd /home/pi
git clone https://github.com/malill/amazescrape.git
```

## Run the Scraper :rocket:

We're going to define a service to run this script on a Raspberry Pi. This way, we can run it in the background and it will start automatically on boot.

First, you need to define shell script to start the script. This shell script is called `start.sh` and it should be located in the `/home/pi/amazescrape` folder. Here is an example of the shell script:

```sh
#!/bin/bash
# [Optional, recommended] Activate the virtual environment
source /home/pi/amazescrape/.venv/bin/activate

# Navigate to the Scrapy project's directory
cd /home/pi/amazescrape

# Run the spider
scrapy crawl amazon
```

Now, we need to define a service. To do so, we need to create a service definition file. We can do it by executing the following commands:

```sh
cd /lib/systemd/system/
sudo nano amazescrape.service
```

The service definition must be on the `/lib/systemd/system folder`. Our service is going to be called `amazescrape.service`. Here is an example of the service definition file:

```sh
[Unit]
Description=Amazescrape Spider Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/amazescrape/start.sh
Restart=always
RestartSec=10s

[Install]
WantedBy=multi-user.target

```

Now that we have our service we need to activate it. We can do it by executing the following commands:

```sh
sudo chmod 644 /lib/systemd/system/amazescrape.service
sudo systemctl daemon-reload
sudo systemctl enable amazescrape.service
sudo systemctl start amazescrape.service
```

## Service Tasks

For every change that we do on the `/lib/systemd/system` folder we need to execute a daemon-reload (third line of previous code).

### Status service :vertical_traffic_light:

```sh
sudo systemctl status amazescrape.service
```

### Start service (if not started) :arrow_forward:

```sh
sudo systemctl start amazescrape.service
```

### Stop service (if started) :stop_sign:

```sh
sudo systemctl stop amazescrape.service
```

### Check service's log :page_facing_up:

```sh
sudo journalctl -f -u amazescrape.service
```

## Contributing :family:

## License :memo:

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
