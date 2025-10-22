import time
import subprocess
from kubernetes import client, config

DEPLOYMENT_NAME = "hello-k8s-deployment"
CONTAINER_NAME = "hello-k8s"
NAMESPACE = "default"
DOCKER_USER = "edw-crtn"
IMAGE_BASE = f"{DOCKER_USER}/hello-k8s"

config.load_kube_config()
apps_v1 = client.AppsV1Api()

def get_current_image():
    dep = apps_v1.read_namespaced_deployment(DEPLOYMENT_NAME, NAMESPACE)
    return dep.spec.template.spec.containers[0].image

def get_remote_digest(tag):
    result = subprocess.run(
        ["docker", "pull", f"{IMAGE_BASE}:{tag}"],
        capture_output=True,
        text=True
    )
    for line in result.stdout.splitlines():
        if "Digest:" in line:
            return line.split("Digest:")[1].strip()
    return None

def get_latest_tag():
    result = subprocess.run(
        ["curl", "-s", f"https://hub.docker.com/v2/repositories/{DOCKER_USER}/hello-k8s/tags?page_size=1"],
        capture_output=True,
        text=True
    )
    import json
    data = json.loads(result.stdout)
    if "results" in data and len(data["results"]) > 0:
        return data["results"][0]["name"]
    return None

def update_deployment(new_image):
    print(f"Deployment update to {new_image}")
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
    print("Deployment updated!")

def main():
    last_tag = None
    while True:
        print("Checking for updated images...")
        latest_tag = get_latest_tag()
        if latest_tag and latest_tag != last_tag:
            print(f"New tag detected: {latest_tag}")
            new_image = f"{IMAGE_BASE}:{latest_tag}"
            update_deployment(new_image)
            last_tag = latest_tag
        else:
            print("Nothing new detected")
        time.sleep(60)

if __name__ == "__main__":
    main()
