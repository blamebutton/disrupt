# Simple Example

The most basic Disrupt example. The Disrupt service is configured to check for image updates every 5 minutes (300 seconds).

It includes an example [jwilder/whoami](https://github.com/jwilder/whoami) service which will start an http server on port `8080`.

## Deploying

To deploy this example, run the following:

```bash
docker stack deploy -c docker-compose.yml <STACK_NAME>
```