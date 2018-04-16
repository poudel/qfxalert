# Introduction

Send email alert when a movie matching the subscribed keywords becomes available.

Save this as `run.sh`:


```bash
#!/usr/bin/env sh
/path/to/venv/bin/python /path/to/qfxalert/qfxalert.py
```

Make it executable:

```bash
sudo chmod +x run.sh
```

Example of crontab that runs every 30 minutes

```crontab
*/30 * * * * /path/to/run.sh
```
