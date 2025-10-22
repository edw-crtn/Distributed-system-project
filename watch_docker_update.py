import os
import time
import subprocess
from dotenv import load_dotenv
from kubernetes import client, config

# Load environment variables
load_dotenv()

DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
NAMESPACE = os.getenv("NAMESPACE")
DOCKER_USER = os.getenv("DOCKER_USER")
IMAGE_NAME = os.getenv("IMAGE_NAME")
IMAGE_BASE = f"{DOCKER_USER}/{IMAGE_NAME}"

config.load_kube_config()
apps_v1 = client.AppsV1Api()

def get_current_image():
    dep = apps_v1.read_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE)
    return dep.spec.template.spec.containers[0].image

def get_latest_remote_digest(tag):
    image = f"{IMAGE_BASE}:{tag}"
    result = subprocess.run(["docker", "pull", image], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Digest:" in line:
            return line.split("Digest:")[1].strip()
    return None

def update_deployment(new_image):
    print(f"Updating deployment to {new_image}")
    body = {
        "spec": {
            "template": {
                "spec": {
                    "containers": [{"name": IMAGE_NAME, "image": new_image}]
                }
            }
        }
    }
    apps_v1.patch_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE, body)
    print(" Deployment updated successfully!")

def main():
    last_digest = None
    tag = 'SHA'
    while True:
        print("Checking for updated images...")
        remote_digest = get_latest_remote_digest(tag)
        if remote_digest and remote_digest != last_digest:
            print("New image detected!")
            update_deployment(f"{IMAGE_BASE}:{tag}")
            last_digest = remote_digest
        else:
            print("No changes detected.")
        time.sleep(60)

if __name__ == "__main__":
    main()
