from azure.mgmt.containerregistry import ContainerRegistryManagementClient, models


class ContainerRegistryHook:

    def create_registry(self, auth, name, resource_group, location, subscription_id, admin_user_enabled):
        client = ContainerRegistryManagementClient(auth, subscription_id)
        registry = models.Registry(sku=models.Sku(name="Standard"),
                                   location=location,
                                   admin_user_enabled=admin_user_enabled)
        return client.registries.create(resource_group, name, registry, subscription_id=subscription_id).result()

    def delete_registry(self, auth, name, resource_group, subscription_id):
        client = ContainerRegistryManagementClient(auth, subscription_id)
        return client.registries.delete(resource_group, name).result()
