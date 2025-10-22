import time
from kubernetes import client, config
import subprocess

#  Config
DEPLOYMENT_NAME = "hello-k8s-deployment"
CONTAINER_NAME = "hello-k8s"
NAMESPACE = "default"
IMAGE_NAME = "edw-crtn/hello-k8s:latest"  #  Docker image

# Load local cluster config
config.load_kube_config()
apps_v1 = client.AppsV1Api()

def get_current_image():
    dep = apps_v1.read_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE)
    return dep.spec.template.spec.containers[0].image

def get_latest_remote_digest():
    result = subprocess.run(
        ["docker", "pull", IMAGE_NAME],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if "Digest:" in line:
            return line.split("Digest:")[1].strip()
    return None

def update_deployment(new_image):
    print(f" Deployment update to {new_image}")
    body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{
                        "name": CONTAINER_NAME,
                        "image": new_image
                    }]
                }
            }
        }
    }
    apps_v1.patch_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE, body)
    print("Deployment updated !")

def main():
    last_digest = None
    while True:
        print("Checking updated images")
        remote_digest = get_latest_remote_digest()
        if remote_digest and remote_digest != last_digest:
            print("New image detected !")
            update_deployment(IMAGE_NAME)
            last_digest = remote_digest
        else:
            print("Nothing new detected")
        time.sleep(60)

if __name__ == "__main__":
    main()
