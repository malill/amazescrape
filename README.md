# AmazeScrape - A Python Web Scraper :snake:

[![Build Status](https://travis-ci.com/malill/amzscrape.svg?branch=master)](https://travis-ci.com/malill/amzscrape)
[![Coverage Status](https://coveralls.io/repos/github/malill/amzscrape/badge.svg?branch=master)](https://coveralls.io/github/malill/amzscrape?branch=master)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description :page_facing_up:

A web scraper that is simply amazing...

### Selenium :robot:

This project uses Selenium to scrape the web. Selenium is a portable framework for testing web applications.

### Proxy Rotation :arrows_counterclockwise:

Currently, there is no proxy rotation implemented. However, it is planned to be implemented in the future.

### Random User Agent :bust_in_silhouette:

This project uses a random user agent to avoid being banned by the websites that we're scraping.

### Random Call Interval :alarm_clock:

This project uses a random call interval to avoid being banned by the websites that we're scraping.

### Database :floppy_disk:

tbd

## Installation :computer:

### Download the Project :arrow_down:

Download the project using git clone. You can clone the project wherever you want. In this case, we're going to clone it in the `/home/pi` folder.

```sh
cd /home/pi
git clone https://github.com/malill/amzscrape.git
```

### Run as Service :rocket:

We're going to define a service to run this script. This way, we can run it in the background and it will start automatically on boot. A shell script is included in the project to start the script. This shell script is called `start.sh` and it should be located in the `/home/pi/dev/amzscrape` folder.

#### Raspberry Pi :strawberry:

```sh
cd /lib/systemd/system/
sudo nano amzscrape.service
```

The service definition must be on the /lib/systemd/system folder. Our service is going to be called `amzscrape.service`. Here is an example of the service definition file:

```sh
[Unit]
Description=AmazeScrape Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi/dev/amzscrape/start.sh
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

Now that we have our service we need to activate it. We can do it by executing the following commands:

```sh
sudo chmod 644 /lib/systemd/system/amzscrape.service
sudo systemctl daemon-reload
sudo systemctl enable amzscrape.service
sudo systemctl start amzscrape.service
```

#### Windows :computer:

tbd

## Usage :wrench:

tbd

## Service Tasks

For every change that we do on the /lib/systemd/system folder we need to execute a daemon-reload (third line of previous code).

### Status service :vertical_traffic_light:

```sh
sudo systemctl status amzscrape.service
```

### Start service (if not started) :arrow_forward:

```sh
sudo systemctl start amzscrape.service
```

### Stop service (if started) :stop_sign:

```sh
sudo systemctl stop amzscrape.service
```

### Check service's log :page_facing_up:

```sh
sudo journalctl -f -u amzscrape.service
```

## Contributing :family:

## License :memo:

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
