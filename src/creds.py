import logging
import json

from datetime import datetime
from operator import attrgetter
from os import environ, path

import pytz
from azure.common.credentials import (
    ServicePrincipalCredentials,
    get_azure_cli_credentials,
)
from azure.graphrbac import GraphRbacManagementClient
from prometheus_client.core import GaugeMetricFamily

logger = logging.getLogger(__name__)


def get_azure_client():
    client_id = environ.get("CLIENT_ID", "")
    client_secret = environ.get("CLIENT_SECRET", "")
    tenant_id = environ.get("TENANT_ID", "")
    if client_id and client_secret and tenant_id:
        logger.info(
            "Found credentials in environment variables, using service principle for auth"
        )
        credentials = ServicePrincipalCredentials(
            tenant=tenant_id,
            client_id=client_id,
            secret=client_secret,
            resource="https://graph.windows.net",
        )
        return GraphRbacManagementClient(credentials, tenant_id)

    try:
        credentials, _, tenant_id = get_azure_cli_credentials(
            resource="https://graph.windows.net", with_tenant=True
        )
    except FileNotFoundError:
        logger.fatal(
            "Failed to find Azure credentials. Please configure environment variables or an az login JSON."
        )
        raise
    return GraphRbacManagementClient(credentials, tenant_id)


def get_credential_expiry():
    # Query the Graph endpoint for a list of applications and get their credentials
    data = {}

    client = get_azure_client()

    # Cast to a list to avoid paging
    result = list(client.applications.list())

    logger.info("Querying %d applications for credentials", len(result))
    start_time = datetime.now()
    today = datetime.utcnow().replace(tzinfo=pytz.utc)

    for item in result:
        # Casting again to avoid paging
        credentials = list(
            client.applications.list_password_credentials(item.object_id)
        )

        # TODO: Do we extract no-creds values?
        if len(credentials) == 0:
            continue
        credentials.sort(key=attrgetter("end_date"))

        days_left = (credentials[0].end_date - today).days
        data[item.display_name] = [item.app_id, days_left]
    end_time = datetime.now()
    logger.warning("Finished query in %d seconds", (end_time - start_time).seconds)
    return data


class CredentialCollector:
    def _get_credentials(self):
        if not path.exists("results.json"):
            return {}
        with open("results.json", "r") as result_file:
            return json.load(result_file)

    def cred_update(self):
        # Share amongst threads
        credentials = get_credential_expiry()
        with open("results.json", "w") as result_file:
            json.dump(credentials, result_file)

    def collect(self):
        c = GaugeMetricFamily(
            "azure_credential_expiry",
            "Number of days until azure application credentials expire",
            value=None,
            labels=["app_name", "app_id"],
        )
        for app_name, values in self._get_credentials().items():
            app_id, expiry = values
            c.add_metric([app_name, app_id], expiry)
        yield c
