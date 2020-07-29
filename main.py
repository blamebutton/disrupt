#!/usr/bin/env python3
import logging
import re
import time
from os import getenv
from sys import stdout
from typing import Optional

import docker
from apprise import Apprise, NotifyType
from docker import DockerClient
from docker.models.images import Image
from docker.models.services import Service


class DissectException(Exception):
    pass


logger = logging.getLogger('Disrupt')
handler = logging.StreamHandler(stream=stdout)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def main():
    """
    Loops over all the Swarm services, checking if they need updates.

    :raises Exception when Docker Engine is not in Swarm Mode
    """
    update_delay = getenv('UPDATE_DELAY', '300')
    notification_url = getenv('NOTIFICATION_URL', '')

    try:
        client = docker.from_env()
    except ConnectionError:
        logger.error('Could not connect to Docker Engine. Check https://git.io/JJujV for possible solutions')
        return

    logger.info('Started checking for updates')
    apprise = Apprise()
    if len(notification_url) > 0:
        # Add notification provider from URL if provided
        apprise.add(notification_url)

    if not is_swarm_manager(client):
        raise Exception('Docker Engine is not in Swarm Mode')
    while True:
        update_services(client, apprise)
        time.sleep(float(update_delay))


def is_swarm_manager(client: DockerClient) -> bool:
    """
    Check if the given client is connected to a Docker Engine
    running in Swarm Mode and has the manager role.

    :param client: DockerClient
    :rtype: bool
    :return: true if Docker Engine is in Swarm mode, else false
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
    logger.info(f'Checking for updates on {len(services)} service(s).')
    for service in services:
        name = service.name
        outdated, tag, digest = is_service_outdated(client, service)
        if outdated:
            update_message = f'Found update for `{tag}`, updating.'
            mode = service.attrs['Spec']['Mode']
            replicated = 'Replicated' in mode
            if replicated:
                replicas = mode['Replicated']['Replicas']
                plural = 's' if replicas > 1 else ''
                update_message = f"Found update for `{tag}`, updating {replicas} replica{plural}."

            apprise.notify(title=f'Service: `{name}`', body=update_message, notify_type=NotifyType.INFO)

            logger.info(f'Found update for service \'{name}\', updating using image {tag}')
            start = time.time()
            full_image = f"{tag}@{digest}"
            service.update(image=full_image, force_update=True)  # Update the service
            end = time.time()
            elapsed = str((end - start))[:4]  # Calculate the time it took to update the service
            logger.info(f'Update for service \'{name}\' successful, took {elapsed} seconds ({full_image})')

            success_message = f'Update successful. Took {elapsed} seconds.'
            apprise.notify(title=f'Service: `{name}`', body=success_message, notify_type=NotifyType.SUCCESS)
        else:
            logger.debug(f'No update found for service \'{name}\'')


def is_service_outdated(client: DockerClient, service: Service) -> tuple:
    """
    Check if the given service it outdated, based on the repository digest.

    :param client:  the Docker Engine client
    :param service: the service to check for updates
    :return:        tuple containing the following information (
                        if the service is outdated,
                        image tag for the given service,
                        digest of the remote image if available
                    )
    """
    service_image = service.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image']
    tag, digest = split_image(service_image)
    remote_image = client.images.pull(tag)
    remote_digest = get_image_digest(remote_image)
    if not digest:
        return False, tag, digest
    if digest != remote_digest:
        return True, tag, remote_digest
    return False, tag, digest


def split_image(tag: str) -> tuple:
    """
    Generic split method for splitting an image tag from it's digest. I.e.::

        python:latest@sha256:3f8bb7c750e86d031dd14c65d331806105ddc0c6f037ba29510f9b9fbbb35960

    Would return::

        ('python:latest', 'sha256:3f8bb7c750e86d031dd14c65d331806105ddc0c6f037ba29510f9b9fbbb35960')

    :param tag: the image tag to split up
    :return: the split up image tag
    """
    search = re.search('^([a-zA-Z0-9/_.:-]{0,128})(?:@(sha256:[0-9a-f]{64}))?$', tag)
    tag = search.group(1)
    digest = search.group(2)
    return tag, digest


def get_image_digest(image: Image) -> Optional[str]:
    """
    Get the repository digest out of an image object.

    :param image: the image object to get the digest out of
    :return: the repository digest for the given image or None if it's not present
    """
    digests = image.attrs.get('RepoDigests')
    if digests:
        tag, digest = split_image(digests[0])
        return digest
    return None


if __name__ == '__main__':
    main()
