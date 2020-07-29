# Supported tags and respective `Dockerfile` links

-   [`latest` (/Dockerfile)](https://github.com/BlameButton/disrupt/blob/master/Dockerfile)

# Quick reference

-   **Where to get help**:\
    [Discord](https://discord.gg/U7RGvJY), [Mail](mailto:bramceulemans@me.com)

-   **Where to file issues**:\
    [GitHub](https://github.com/BlameButton/disrupt/issues)

-   **Maintained by**:\
    [BlameButton](https://github.com/BlameButton)

-   **Source of this description**:\
    [`/docker/DESCRIPTION.md` in GitHub](https://github.com/BlameButton/disrupt/blob/master/docker/DESCRIPTION.md)

# What is Disrupt?

Disrupt is a Python script that will check for updates for the images of your Docker Swarm services.
Disrupt can either run in a container or on the host itself.

## Configuration

Configuration of Disrupt is done through environment variables. This is done to make the deployment of Disrupt
environment-agnostic.

Below is a list of environment variables available to be configured.

| Name | Type | Options |
| - | - | - |
| UPDATE_DELAY | Integer | default = 300 |
| NOTIFICATION_URL | String | Any [Apprise](https://github.com/caronc/apprise#popular-notification-services) compatible URL |
