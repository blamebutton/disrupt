# Notification Example

A Disrupt example including notification support. The Disrupt service is configured to check for image updates every 5 minutes (300 seconds).

It includes an example [jwilder/whoami](https://github.com/jwilder/whoami) service which will start an http server on port `8080`.

## Configuring

To configure this example, edit `docker-compose.yml` and set the `NOTIFICATION_URL` environment variable to a valid [Apprise URL](https://github.com/caronc/apprise#popular-notification-services).

## Deploying

To deploy this example, run the following:

```bash
docker stack deploy -c docker-compose.yml <STACK_NAME>
```