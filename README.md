<div id="top"></div>

# Monitor: Agent

Computer Science Final Degree Project @ USAL - Host to monitor

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPL License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



### Built With

[![Python][Python]][Python-url] [![PSUtils][PSUtils]][PSUtils-url] [![Poetry][Poetry]][Poetry-url]

[![FastAPI][FastAPI]][FastAPI-url] [![FastAPI Utils][FastAPI-Utils]][FastAPI-Utils-url] [![Uvicorn][Uvicorn]][Uvicorn-url]


<p align="right">(<a href="#top">back to top</a>)</p>


## Getting Started

### Installation

First, download the repository into your Home folder or the directory you prefer:

```bash
git clone https://github.com/n0nuser/monitor-agent
```

Install the Python dependencies:

```bash
sudo pip3 install -r requirements.txt
```

Then, create a Systemd service in `/etc/systemd/system/` called `agent.service`.

`sudo nano /etc/systemd/system/agent.service`:

```service
[Unit]
Description=RESTful web to track agents
After=network.target network-online.target
Requires=network-online.target

[Service]
RemainAfterExit=true
Restart=on-failure
ExecStart=/usr/bin/python3 /home/MYUSER/monitor-agent/monitor_agent/main.py

[Install]
WantedBy=multi-user.target
```

Modify `MYUSER` with your user, and `DIRECTORY` with the path to the `main.py`. In case you downloaded the repository in your Home folder you wouldn't need to change the directory in the service file.

Once the service is installed, you can enable it to run forever and start on startup:

```bash
sudo systemctl enable agent.service
sudo systemctl start agent.service
systemctl status agent.service
```

### Configuration

The user can configure the agent and server settings with the `settings.json` file:

```json
{
    "alerts": {
        "url": "http://localhost:8000/api/alerts/"
    },
    "auth": {
        "agent_token": "fb79210dd15ea00aeeb4bb21f81b27421a4e11a7",
        "name": "Laptop",
        "user_token": "19fc6e57b8fb0e5a1a7b55976952ab02865aa771"
    },
    "endpoints": {
        "agent_endpoint": "http://localhost:8000/api/agents/",
        "metric_endpoint": "http://localhost:8000/api/metrics/"
    },
    "logging": {
        "filename": "monitor.log",
        "level": "info"
    },
    "metrics": {
        "enable_logfile": false,
        "get_endpoint": false,
        "log_filename": "metrics.json",
        "post_interval": 60
    },
    "thresholds": {
        "cpu_percent": 50,
        "ram_percent": 30
    },
    "uvicorn": {
        "backlog": 2048,
        "debug": false,
        "host": "0.0.0.0",
        "log_level": "trace",
        "port": 8080,
        "reload": true,
        "timeout_keep_alive": 5,
        "workers": 4
    }
}
```

It's best to use the configurator from the Monitor Web App as it automatically generates it with the approppiate configuration.
You can always update the configuration with a form in the Web App.

Once configured, restart the service:

```bash
sudo systemctl restart agent.service
```



<!-- ROADMAP -->
## Roadmap

Check the [Roadmap here](https://github.com/n0nuser/Monitor-Agent/issues/5).

See the [open issues](https://github.com/n0nuser/Monitor-Agent/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the GPL-3.0 License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Pablo González Rubio - [@n0nuser_](https://twitter.com/n0nuser_) - gonzrubio.pablo@gmail.com

Project Link: [https://github.com/n0nuser/Monitor-Agent](https://github.com/n0nuser/Monitor-Agent)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/n0nuser/monitor-agent?style=for-the-badge
[contributors-url]: https://github.com/n0nuser/Monitor-Agent/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/n0nuser/monitor-agent?style=for-the-badge
[forks-url]: https://github.com/n0nuser/Monitor-Agent/network/members
[stars-shield]: https://img.shields.io/github/stars/n0nuser/monitor-agent?style=for-the-badge
[stars-url]: https://github.com/n0nuser/Monitor-Agent/stargazers
[issues-shield]: https://img.shields.io/github/issues/n0nuser/monitor-agent?style=for-the-badge
[issues-url]: https://github.com/n0nuser/Monitor-Agent/issues
[license-shield]: https://img.shields.io/github/license/n0nuser/monitor-agent?style=for-the-badge
[license-url]: https://github.com/n0nuser/Monitor-Agent/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/nonuser

[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
[FastAPI]: https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi
[FastAPI-url]: https://fastapi.tiangolo.com/
[FastAPI-Utils]: https://img.shields.io/badge/FastAPI%20Utils-005571?style=for-the-badge&logo=fastapi
[FastAPI-Utils-url]: https://fastapi-utils.davidmontague.xyz/
[PSUtils]: https://img.shields.io/badge/PSUtils-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[PSUtils-url]: https://psutil.readthedocs.io/en/latest/
[Poetry]: https://img.shields.io/badge/Poetry-3670A0?style=for-the-badge&logo=poetry&logoColor=ffdd54
[Poetry-url]: https://python-poetry.org/
[Uvicorn]: https://img.shields.io/badge/uvicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white
[Uvicorn-url]: https://www.uvicorn.org/
