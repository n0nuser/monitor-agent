# Monitor - Agent

Final Degree Project - Host to monitor


## Configuration

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

## Installation

First, install the Python dependencies:

```bash
pip3 install -r requirements.txt
```

Then, create a SystemD service in `/etc/systemd/system/` called `agent.service`.

`/etc/systemd/system/agent.service`:

```service
[Unit]
Description=RESTful web to track agents
After=network.target network-online.target
Requires=network-online.target

[Service]
RemainAfterExit=true
Restart=on-failure
ExecStart=/usr/bin/python3 /home/MYUSER/DIRECTORY/monitor_agent/monitor_agent/main.py

[Install]
WantedBy=multi-user.target
```

Modify `MYUSER` with your user, and `DIRECTORY` with the path to the `main.py`.
