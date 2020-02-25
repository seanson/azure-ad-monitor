# azure-ad-monitor

![azure searching logo](./logo.png)

This is a utility intended to export some custom Azure Active Directory information out as Prometheus Metrics.

It currently only supports exposing Azure AD Application Secret expiry times.

## Why

Azure AD is a wonderful tool for setting up Single Sign On applications. These applications are secured with client secrets can be configured to expire after 1 year, 2 years or never. Ideally short lived credentials with a regular rotation capacity is best but there is no alerting mechanism.

The goal of this project is to provide a Prometheus metric in order to allow long term tracking, dashboarding and alerting of these credential expiry times and hopefully prevent future production incidents.

## Usage

### Running

This requires the following environment variables set:

- `TENANT_ID`: Global tenant ID for AD
- `CLIENT_ID`: The client ID for the configured App Registration
- `CLIENT_SECRET`: The client secret for the configured App Registration

The full list of applications will be queried every 10 minutes.

### Azure Permissions

This requires a Service Priniciple on Azure with the following permissions:

- Microsoft Graph `Application.Read.All`

## Development

This project uses Python [Poetry](https://python-poetry.org/) for local installation.

`poetry install`

If the above environment variables are not configured this will fall back to using your credentials from `az login`.

## TODO

- [ ] Kubernetes YAML in `deploy` to deploy the service
- [ ] Kubernetes YAML for Prometheus Operator rules / alerts
- [ ] Hashicorp Vault support
- [ ] Some tests
