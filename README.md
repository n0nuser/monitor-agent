# Monitor - Agent

Final Degree Project - Host to monitor

## Agent configuration

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
