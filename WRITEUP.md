# Write-up Template

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*
- *Analyze costs, scalability, availability, and workflow*
- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*

I chose to use the App Service solution because I've used VMs many times and wanted to see the "full service" option that could possibly automate much of the configuration/integration/IAAS setup.

It is more expensive, but for a learning project that remains small, I'm willing to deploy it with a subscription limit of $20 and try it out.  

App service is more scalable if this was a larger project that could grow, even if the base cost is higher, that option could be worth it in real world deployment scenarios.

### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.* 

If the cost was high, or the App Service configuration proved cumbersome or error prone, I might choose to use the VM for the cheapness and ease of debugging without the layers of abstraction.

