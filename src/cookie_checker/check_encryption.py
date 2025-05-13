#!/usr/bin/env python3
import json
import requests
import ssl
import socket
from .utils import extract_domain
from .types_models import BaseChecker, BrowserDataLogEntry


class EncryptionChecker(BaseChecker):
    """Checks for encryption-related security issues"""

    def __init__(self) -> None:
        super().__init__()

    def check_https_availability(self, url: str) -> bool:
        """
        Check if website is available over HTTPS
        ITS-ENC-359: Website only accessible via https://
        """

        try:
            response = requests.get(url, timeout=10)
            # Consider any non-error status as available
            if response.status_code < 400:
                status_msg = f"Status: {response.status_code}"
                msg = f"Website is accessible via HTTPS ({status_msg})"
                self.print_success(msg)
                return True
            else:
                msg = f"Website returned error status code: {response.status_code}"
                self.print_failure(msg)
                return False
        except requests.exceptions.SSLError:
            error_msg = "SSL Error occurred - HTTPS configuration issue detected"
            self.print_failure(error_msg)
            return False
        except requests.exceptions.RequestException as e:
            self.print_failure(f"Failed to connect via HTTPS: {e}")
            return False

    def check_http_availability(self, url: str) -> bool:
        """
        Check if website is available over HTTP
        ITS-ENC-359: Website only accessible via http://
        """

        try:
            response = requests.get(url, timeout=10)
            if response.status_code < 400:
                status_msg = f"Status: {response.status_code}"
                msg = f"Website is not accessible via HTTP ({status_msg})"
                self.print_failure(msg)
                return False
            else:
                msg = f"Website returned error status code: {response.status_code}"
                self.print_success(msg)
                return True
        except requests.exceptions.RequestException as e:
            self.print_failure(f"Failed to connect via HTTP: {e}")
            return True

    def check_http_to_https_redirect(self, domain: str) -> bool:
        """
        Check if HTTP requests redirect to HTTPS
        ITS-ENC-360: HTTP to HTTPS redirects configured
        """
        http_url = f"http://{domain}"

        try:
            response = requests.get(http_url, timeout=10, allow_redirects=True)
            final_url = response.url

            if final_url.startswith("https://"):
                msg = f"HTTP successfully redirects to HTTPS: {final_url}"
                self.print_success(msg)
                return True
            else:
                msg = f"HTTP does not redirect to HTTPS. Final URL: {final_url}"
                self.print_failure(msg)
                return False
        except requests.exceptions.RequestException as e:
            self.print_failure(f"Failed to check HTTP to HTTPS redirect: {e}")
            return False

    def check_tls_ssl_protocols(self, domain: str, port: int = 443) -> bool:
        """
        Check for outdated TLS/SSL protocols
        ITS-ENC-361: Rejection of outdated TLS/SSL protocols
        Reference:
        https://aws.amazon.com/de/compare/the-difference-between-ssl-and-tls/
        """

        # Define outdated protocols to check
        outdated_protocols = [
            ssl.PROTOCOL_TLSv1,  # TLS 1.0
            ssl.PROTOCOL_TLSv1_1,  # TLS 1.1
            ssl.PROTOCOL_SSLv23,  # SSL v2/v3
        ]

        protocol_names = {
            ssl.PROTOCOL_TLSv1: "TLS 1.0",
            ssl.PROTOCOL_TLSv1_1: "TLS 1.1",
            ssl.PROTOCOL_SSLv23: "SSL v2/v3",
        }

        results = {}

        for protocol in outdated_protocols:
            context = ssl.SSLContext(protocol)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            try:
                with socket.create_connection((domain, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as _:
                        results[protocol_names[protocol]] = "Supported (Insecure)"
            except (ssl.SSLError, socket.error, socket.timeout):
                results[protocol_names[protocol]] = "Rejected (Secure)"

        all_secure = True
        for protocol_name, status in results.items():
            if status == "Supported (Insecure)":
                self.print_failure(f"{protocol_name}: {status}")
                all_secure = False
            else:
                self.print_success(f"{protocol_name}: {status}")

        return all_secure

    def check_encryption(self, path_to_jsonl: str) -> dict:
        with open(path_to_jsonl, "r") as f:
            try:
                line = f.readline()
                data = BrowserDataLogEntry(**json.loads(line))
                url = data.url
            except Exception as e:
                print(f"Invalid browser data log format: {e}")
                raise e
        self.print_info(f"Starting security checks for {url}")
        print("=" * 60)

        # Extract domain using the helper function
        domain = extract_domain(url)

        results = {}

        # Run all checks
        results["https_available"] = self.check_https_availability(url)
        http_url = f"http://{domain}"
        results["http_disabled"] = self.check_http_availability(http_url)

        results["http_to_https_redirect"] = self.check_http_to_https_redirect(domain)

        results["tls_ssl_secure"] = self.check_tls_ssl_protocols(domain)

        return results
