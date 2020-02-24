# azure-ad-monitor

This is a utility intended to export some custom Azure Active Directory information out as Prometheus Metrics.

It currently only supports exposing Azure AD Application Secret expiry times.

## Why

Azure AD is a wonderful tool for setting up Single Sign On applications. These applications are secured with client secrets can be configured to expire after 1 year, 2 years or never. Ideally short lived credentials with a regular rotation capacity is best but there is no alerting mechanism.

The goal of this project is to provide a Prometheus metric in order to allow long term tracking, dashboarding and alerting of these credential expiry times and hopefully prevent future production incidents.

## Development

This project uses Python [Poetry](https://python-poetry.org/) for local installation.

`poetry install`

## TODO

- [ ] Kubernetes YAML in `deploy` to deploy the service
- [ ] Kubernetes YAML for Prometheus Operator rules / alerts
- [ ] Some tests
