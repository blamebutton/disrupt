import time
from os import getenv

import docker
from apprise import Apprise, NotifyType
from docker import DockerClient
from docker.models.images import Image
from docker.models.services import Service


def main():
    """
    Loops over all the Swarm services, checking if they need updates

    :raises Exception when Docker Engine is not in Swarm Mode
    """
    update_delay = getenv('UPDATE_DELAY', '300')
    notification_url = getenv('NOTIFICATION_URL', '')

    client = docker.from_env()
    apprise = Apprise(notification_url)
    if not is_swarm(client):
        raise Exception('Docker Engine is not in Swarm Mode')
    while True:
        update_services(client, apprise)
        time.sleep(float(update_delay))


def is_swarm(client: DockerClient) -> bool:
    """
    Check if the given client is connected to a Docker Engine
    running in Swarm Mode and has the manager role.

    :param client: DockerClient
    :rtype: bool
    :return: true if Docker Engine is in Swarm mode, else falses
    """
    info = client.info()
    swarm = info['Swarm']
    return swarm['LocalNodeState'] == 'active' and swarm['ControlAvailable']


def update_services(client: DockerClient, apprise: Apprise):
    """
    Update all the services found on the Docker Swarm.

    :param client: Docker Client that is connected to a Docker Swarm Manager
    :param apprise: Apprise notification service
    """
    services = client.services.list()
    for service in services:
        try:
            is_outdated, new_tag = is_service_outdated(client, service)
        except DisectException:
            # Skip updating this service when image tag could not be extracted
            print(service, 'could not be updated, invalid image found.')
            continue
        mode = service.attrs['Spec']['Mode']
        replicated = 'Replicated' in mode
        update_message = 'Found update for `' + new_tag + '`, updating.'
        if replicated:
            replicas = mode['Replicated']['Replicas']
            plural = 's' if replicas > 1 else ''
            update_message = f"Found update for `{new_tag}`, updating {replicas} replica{plural}."

        if is_outdated:
            apprise.notify(
                title='Service: `' + service.name + '`',
                body=update_message,
                notify_type=NotifyType.INFO)
            start = time.time()
            service.update(image=new_tag)
            end = time.time()
            elapsed = str((end - start))[:4]
            apprise.notify(
                title='Service: `' + service.name + '`',
                body='Update successful. Took ' + elapsed + ' seconds.',
                notify_type=NotifyType.SUCCESS)


def is_service_outdated(client: DockerClient, service: Service) -> tuple:
    """
    Pull image for service, check if digests match, if not, return True.

    :param client: Docker Client that is connected to a Docker Swarm Manager
    :param service: the Docker Swarm service to check for updates
    :return: if the given service is outdated, i.e. needs a new image assigned
    :rtype: bool
    """
    image_tag, image_hash = disect_service(service)
    remote_image = client.images.pull(image_tag)
    remote_digest = disect_repo_digest(remote_image)
    _, pulled_digest = disect_image(remote_digest)
    return image_hash != pulled_digest, image_tag


def disect_repo_digest(repo_digest: Image) -> str:
    return repo_digest.attrs['RepoDigests'][0]


def disect_service(service: Service) -> tuple:
    """
    Get a tuple of the name/tag and hash for this service, i.e.::

        ('nginx:latest', 'sha256:98efe605f61725fd817ea69521b0eeb32bef007af0e3d0aeb6258c6e6fe7fc1a')

    :param service: the service to disect into a name/tag and image hash
    :return: image name and hash, image hash
    :rtype: tuple
    """
    image = service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
    return disect_image(image)


def disect_image(image: str) -> tuple:
    """
    Split an image name + tag + digest, i.e.::

        nginx:latest@sha256:98efe605f61725fd817ea69521b0eeb32bef007af0e3d0aeb6258c6e6fe7fc1a

    will become::

        ('nginx:latest', 'sha256:98efe605f61725fd817ea69521b0eeb32bef007af0e3d0aeb6258c6e6fe7fc1a')

    :param image: the image string, containing the name, tag and hash
    :return: image name and hash, image hash
    :rtype: tuple
    :raises DisectException: when the image name+tag+digest could not be split into a tuple
    """
    tag = image.split('@')
    if len(tag) != 2:
        raise DisectException('Unable to disect image digest.')
    return tag[0], tag[1]


if __name__ == '__main__':
    main()


class DisectException(Exception):
    pass
