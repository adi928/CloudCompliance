# Compliance Tools

### Azure PCI Compliance

Input required for azure configuration:
* Tenant Id
* Subscription Id
* Client Id
* Client Secret

Steps performed by the script:
* Gets access token from login.microsoftonline.com
* Creates a policy set definition from the list of policy names accessed from 'policies-required.json'.
* Make a REST request to create the policy definition.
* Make a REST request to assign the new policy set to a scope(subscription, resource, resource group, etc.)

### Todo

* Add more policies to conform to the PCI controls. 