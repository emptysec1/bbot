from bbot.modules.bucket_aws import bucket_aws


class bucket_gcp(bucket_aws):
    """
    Adapted from https://github.com/RhinoSecurityLabs/GCPBucketBrute/blob/master/gcpbucketbrute.py
    """

    watched_events = ["DNS_NAME", "STORAGE_BUCKET"]
    produced_events = ["STORAGE_BUCKET", "FINDING"]
    flags = ["active", "safe", "cloud-enum"]
    meta = {"description": "Check for Google object storage related to target"}
    options = {"max_threads": 10, "permutations": False}
    options_desc = {
        "max_threads": "Maximum number of threads for HTTP requests",
        "permutations": "Whether to try permutations",
    }

    cloud_helper_name = "gcp"
    delimiters = ("", "-", ".", "_")
    base_domains = ["storage.googleapis.com"]
    bad_permissions = [
        "storage.buckets.setIamPolicy",
        "storage.objects.list",
        "storage.objects.get",
        "storage.objects.create",
    ]

    def build_url(self, bucket_name, base_domain, region):
        return f"https://www.googleapis.com/storage/v1/b/{bucket_name}"

    def check_bucket_open(self, bucket_name, url):
        bad_permissions = []
        try:
            list_permissions = "&".join(["=".join(("permissions", p)) for p in self.bad_permissions])
            url = f"https://www.googleapis.com/storage/v1/b/{bucket_name}/iam/testPermissions?" + list_permissions
            response = self.helpers.request(url)
            permissions = response.json()
            if isinstance(permissions, dict):
                bad_permissions = list(permissions.get("permissions", {}))
        except Exception as e:
            self.warning(f'Failed to enumerate permissions for bucket "{bucket_name}": {e}')
        msg = ""
        if bad_permissions:
            perms_str = ",".join(bad_permissions)
            msg = f"Open permissions on storage bucket ({perms_str})"
        return (msg, set())

    def check_bucket_exists(self, bucket_name, url):
        response = self.helpers.request(url)
        status_code = getattr(response, "status_code", 0)
        existent_bucket = status_code not in (0, 400, 404)
        return existent_bucket, set()
