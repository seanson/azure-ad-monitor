import logging
from datetime import datetime
from operator import attrgetter

import pytz
from azure.common.credentials import get_azure_cli_credentials
from azure.graphrbac import GraphRbacManagementClient
from prometheus_client.core import GaugeMetricFamily

logger = logging.getLogger(__name__)


def get_credential_expiry():
    # Query the Graph endpoint for a list of applications and get their credentials
    data = {}

    # Build our client from environment credentials
    # TODO: Environment credentials
    cred, _, tenant_id = get_azure_cli_credentials(
        resource="https://graph.windows.net", with_tenant=True
    )
    client = GraphRbacManagementClient(cred, tenant_id)

    # Cast to a list to avoid paging
    result = list(client.applications.list())

    logger.warning("Querying %d applications for credentials", len(result))
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
    credentials = {}

    def cred_update(self):
        self.credentials = get_credential_expiry()

    def collect(self):
        c = GaugeMetricFamily(
            "azure_credential_expiry",
            "Number of days until azure application credentials expire",
            value=None,
            labels=["app_name", "app_id"],
        )
        for app_name, values in self.credentials.items():
            app_id, expiry = values
            c.add_metric([app_name, app_id], expiry)
        yield c
