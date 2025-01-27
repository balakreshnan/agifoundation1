from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

account_url = "https://agentaihubeast1538884886.blob.core.windows.net"
default_credential = DefaultAzureCredential()



def main():

     # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    # Create a unique name for the container
    # container_name = "3a3e7884-d8c2-40b0-80de-4fefa308f10b-azureml"

    container_name = "insights-logs-auditevent"

    # Create the container
    # container_client = blob_service_client.create_container(container_name)
    container_client = blob_service_client.get_container_client(container= container_name)
  

    print("\nListing blobs...")

    # List the blobs in the container
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)

if __name__ == '__main__':
    main()