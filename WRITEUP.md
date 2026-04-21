# Write-up Template

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*
- *Analyze costs, scalability, availability, and workflow*
- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*

I chose to use the App Service solution because I've used VMs many times and wanted to see the "full service" option that could possibly automate much of the configuration/integration/IAAS setup.

It is more expensive, but for a learning project that remains small, I'm willing to deploy it with a subscription limit of $20 and try it out.  

App service is more scalable if this was a larger project that could grow, even if the base cost is higher, that option could be worth it in real world deployment scenarios.

# Addendum for submission #2 since more explicit analysis was requested:

## COSTS:
VM costs are cheaper, but scaling is a more of manual process that requires more prep/configuration.

## SCALABILITY:
App Service Scales easier, with auto-scaling horizontally and scaling vertically.

## AVAILABILITY:
App Service has high availability out of the box, while VMs require setup and config to get similar availability.

## WORKFLOW:
VMs require configuring basically everything yourself.
App service allows you to just deploy the minimal code and get the web server, load balancer, and scale sets out of the box.

### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.* 

While the cost of the App Service is higher, even for a small app like this, it's not high enough to worry about.  I'm more concerend with ease of deployment for the webapp and the promise of an App Service is to enable that easy deployment.  However, if the layers of abstraction make it more challenging, I might choose to switch to the VM for the cheapness and ease of debugging, even if it means giving up some of the automatic front end features.
