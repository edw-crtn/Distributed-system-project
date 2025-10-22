import os
import time
import subprocess
import json
from kubernetes import client, config

# ---------------- Configuration ---------------- #
DEPLOYMENT_NAME = "hello-k8s-deployment"
NAMESPACE = "default"
DOCKER_USER = "edwin765"
IMAGE_NAME = "hello-k8s"
IMAGE_BASE = f"{DOCKER_USER}/{IMAGE_NAME}"
CHECK_INTERVAL = 60  # secondes
# ---------------------------------------------- #

# Config Kubernetes
config.load_kube_config()
apps_v1 = client.AppsV1Api()

def get_latest_sha_tag():
    """
    Récupère le dernier tag pushé (SHA) sur Docker Hub via l'API publique.
    """
    url = f"https://hub.docker.com/v2/repositories/{DOCKER_USER}/{IMAGE_NAME}/tags?page_size=5&page=1"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
    data = json.loads(result.stdout)
    if "results" in data and len(data["results"]) > 0:
        # Trier par date de push
        sorted_tags = sorted(data["results"], key=lambda x: x["last_updated"], reverse=True)
        return sorted_tags[0]["name"]
    return None

def get_digest_for_tag(tag):
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
    print("Deployment updated successfully!")

def main():
    last_digest = None
    print(f"Monitoring Docker image: {IMAGE_BASE} (auto-detect SHA)")

    while True:
        print("Checking for updated image...")
        tag = get_latest_sha_tag()
        if not tag:
            print("Could not retrieve latest SHA tag. Retrying...")
            time.sleep(CHECK_INTERVAL)
            continue

        remote_digest = get_digest_for_tag(tag)
        if remote_digest and remote_digest != last_digest:
            print(f"New image detected! SHA: {tag}")
            update_deployment(f"{IMAGE_BASE}:{tag}")
            last_digest = remote_digest
        else:
            print("No changes detected.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
