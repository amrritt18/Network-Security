import ipaddress
import re
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

import pandas as pd
import requests
import whois
from bs4 import BeautifulSoup


class URLFeatureExtractor:
    """
    Extract the 30 features expected by the phishing-detection model.

    NOTE:
    Some features from the original phishing dataset depend on legacy
    reputation/search/ranking services. For live URL prediction, those
    features are practical approximations and should be separately
    validated before claiming production-level accuracy.
    """

    FEATURE_COLUMNS = [
        "having_IP_Address",
        "URL_Length",
        "Shortining_Service",
        "having_At_Symbol",
        "double_slash_redirecting",
        "Prefix_Suffix",
        "having_Sub_Domain",
        "SSLfinal_State",
        "Domain_registeration_length",
        "Favicon",
        "port",
        "HTTPS_token",
        "Request_URL",
        "URL_of_Anchor",
        "Links_in_tags",
        "SFH",
        "Submitting_to_email",
        "Abnormal_URL",
        "Redirect",
        "on_mouseover",
        "RightClick",
        "popUpWidnow",
        "Iframe",
        "age_of_domain",
        "DNSRecord",
        "web_traffic",
        "Page_Rank",
        "Google_Index",
        "Links_pointing_to_page",
        "Statistical_report",
    ]

    SHORTENING_SERVICES = {
        "bit.ly",
        "goo.gl",
        "tinyurl.com",
        "ow.ly",
        "t.co",
        "is.gd",
        "buff.ly",
        "adf.ly",
        "bit.do",
        "cutt.ly",
        "tiny.cc",
        "rebrand.ly",
        "shorturl.at",
    }

    SUSPICIOUS_TLDS = {
        "zip",
        "review",
        "country",
        "kim",
        "cricket",
        "science",
        "work",
        "party",
        "gq",
        "tk",
        "ml",
        "ga",
        "cf",
    }

    def __init__(self, url: str):

        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        self.original_url = url.strip()

        self.url = self._normalize_url(
            self.original_url
        )

        self.parsed_url = urlparse(
            self.url
        )

        self.hostname = (
            self.parsed_url.hostname or ""
        ).lower()

        if not self.hostname:
            raise ValueError(
                "Unable to determine hostname from URL."
            )

        self.response = None
        self.soup = None

        # Cached WHOIS information
        self._whois_loaded = False
        self._whois_data = None

        self._fetch_webpage()

    # =========================================================
    # BASIC HELPERS
    # =========================================================

    @staticmethod
    def _normalize_url(url):

        if not re.match(
            r"^https?://",
            url,
            flags=re.IGNORECASE,
        ):
            url = "https://" + url

        return url

    def _fetch_webpage(self):

        try:

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/120.0 Safari/537.36"
                )
            }

            self.response = requests.get(
                self.url,
                headers=headers,
                timeout=8,
                allow_redirects=True,
            )

            self.soup = BeautifulSoup(
                self.response.text,
                "html.parser",
            )

        except requests.RequestException:

            self.response = None
            self.soup = None

    def _get_whois(self):

        if self._whois_loaded:
            return self._whois_data

        self._whois_loaded = True

        try:

            self._whois_data = whois.whois(
                self.hostname
            )

        except Exception:

            self._whois_data = None

        return self._whois_data

    @staticmethod
    def _first_date(value):

        if isinstance(value, list):

            valid_values = [
                item
                for item in value
                if isinstance(item, datetime)
            ]

            if not valid_values:
                return None

            return valid_values[0]

        if isinstance(value, datetime):
            return value

        return None

    def _is_external_url(self, resource):

        if not resource:
            return False

        resource = resource.strip()

        if resource.startswith(
            (
                "#",
                "javascript:",
                "mailto:",
                "tel:",
                "data:",
            )
        ):
            return False

        try:

            absolute = urljoin(
                self.url,
                resource,
            )

            parsed = urlparse(
                absolute
            )

            host = (
                parsed.hostname or ""
            ).lower()

            if not host:
                return False

            base = self.hostname.removeprefix(
                "www."
            )

            host_without_www = (
                host.removeprefix("www.")
            )

            return not (
                host_without_www == base
                or host_without_www.endswith(
                    "." + base
                )
            )

        except Exception:

            return False

    # =========================================================
    # 1. HAVING IP ADDRESS
    # =========================================================

    def having_ip_address(self):

        try:

            ipaddress.ip_address(
                self.hostname
            )

            return -1

        except ValueError:

            return 1

    # =========================================================
    # 2. URL LENGTH
    # =========================================================

    def url_length(self):

        length = len(
            self.original_url
        )

        if length < 54:
            return 1

        if length <= 75:
            return 0

        return -1

    # =========================================================
    # 3. SHORTENING SERVICE
    # =========================================================

    def shortening_service(self):

        host = self.hostname.removeprefix(
            "www."
        )

        for service in self.SHORTENING_SERVICES:

            if (
                host == service
                or host.endswith(
                    "." + service
                )
            ):
                return -1

        return 1

    # =========================================================
    # 4. @ SYMBOL
    # =========================================================

    def having_at_symbol(self):

        return (
            -1
            if "@" in self.original_url
            else 1
        )

    # =========================================================
    # 5. DOUBLE SLASH REDIRECT
    # =========================================================

    def double_slash_redirecting(self):

        without_protocol = re.sub(
            r"^https?://",
            "",
            self.url,
            flags=re.IGNORECASE,
        )

        return (
            -1
            if "//" in without_protocol
            else 1
        )

    # =========================================================
    # 6. PREFIX SUFFIX
    # =========================================================

    def prefix_suffix(self):

        return (
            -1
            if "-" in self.hostname
            else 1
        )

    # =========================================================
    # 7. SUB DOMAIN
    # =========================================================

    def having_sub_domain(self):

        host = self.hostname.removeprefix(
            "www."
        )

        parts = [
            part
            for part in host.split(".")
            if part
        ]

        if len(parts) <= 2:
            return 1

        if len(parts) == 3:
            return 0

        return -1

    # =========================================================
    # 8. SSL FINAL STATE
    # =========================================================

    def ssl_final_state(self):

        if (
            self.parsed_url.scheme.lower()
            != "https"
        ):
            return -1

        try:

            context = ssl.create_default_context()

            with socket.create_connection(
                (self.hostname, 443),
                timeout=5,
            ) as sock:

                with context.wrap_socket(
                    sock,
                    server_hostname=self.hostname,
                ) as secure_socket:

                    certificate = (
                        secure_socket.getpeercert()
                    )

                    if certificate:
                        return 1

            return -1

        except Exception:

            return -1

    # =========================================================
    # 9. DOMAIN REGISTRATION LENGTH
    # =========================================================

    def domain_registration_length(self):

        try:

            info = self._get_whois()

            if info is None:
                return -1

            creation = self._first_date(
                info.creation_date
            )

            expiration = self._first_date(
                info.expiration_date
            )

            if (
                creation is None
                or expiration is None
            ):
                return -1

            days = (
                expiration - creation
            ).days

            return (
                1
                if days > 365
                else -1
            )

        except Exception:

            return -1

    # =========================================================
    # 10. FAVICON
    # =========================================================

    def favicon(self):

        if self.soup is None:
            return -1

        try:

            icons = []

            for link in self.soup.find_all(
                "link"
            ):

                rel = link.get("rel")

                if rel and any(
                    "icon" in str(item).lower()
                    for item in rel
                ):
                    icons.append(link)

            if not icons:
                return 1

            for icon in icons:

                href = icon.get("href")

                if (
                    href
                    and self._is_external_url(
                        href
                    )
                ):
                    return -1

            return 1

        except Exception:

            return -1

    # =========================================================
    # 11. PORT
    # =========================================================

    def port_feature(self):

        try:

            port = self.parsed_url.port

            if port is None:
                return 1

            return (
                1
                if port in (80, 443)
                else -1
            )

        except ValueError:

            return -1

    # =========================================================
    # 12. HTTPS TOKEN
    # =========================================================

    def https_token(self):

        host = self.hostname.removeprefix(
            "www."
        )

        return (
            -1
            if "https" in host
            else 1
        )

    # =========================================================
    # 13. REQUEST URL
    # =========================================================

    def request_url(self):

        if self.soup is None:
            return -1

        try:

            resources = []

            for tag in self.soup.find_all(
                [
                    "img",
                    "audio",
                    "video",
                    "source",
                ]
            ):

                src = tag.get("src")

                if src:
                    resources.append(src)

            if not resources:
                return 1

            external = sum(
                self._is_external_url(item)
                for item in resources
            )

            percentage = (
                external
                / len(resources)
            ) * 100

            if percentage < 22:
                return 1

            if percentage <= 61:
                return 0

            return -1

        except Exception:

            return -1

    # =========================================================
    # 14. URL OF ANCHOR
    # =========================================================

    def url_of_anchor(self):

        if self.soup is None:
            return -1

        try:

            anchors = self.soup.find_all(
                "a",
                href=True,
            )

            if not anchors:
                return 1

            suspicious = 0

            for anchor in anchors:

                href = (
                    anchor.get("href")
                    or ""
                ).strip()

                lower = href.lower()

                if (
                    not href
                    or lower.startswith("#")
                    or lower.startswith(
                        "javascript:"
                    )
                    or self._is_external_url(
                        href
                    )
                ):
                    suspicious += 1

            percentage = (
                suspicious
                / len(anchors)
            ) * 100

            if percentage < 31:
                return 1

            if percentage <= 67:
                return 0

            return -1

        except Exception:

            return -1

    # =========================================================
    # 15. LINKS IN TAGS
    # =========================================================

    def links_in_tags(self):

        if self.soup is None:
            return -1

        try:

            links = []

            for tag in self.soup.find_all(
                ["meta", "script", "link"]
            ):

                resource = (
                    tag.get("href")
                    or tag.get("src")
                )

                if resource:
                    links.append(resource)

            if not links:
                return 1

            external = sum(
                self._is_external_url(item)
                for item in links
            )

            percentage = (
                external
                / len(links)
            ) * 100

            if percentage < 17:
                return 1

            if percentage <= 81:
                return 0

            return -1

        except Exception:

            return -1

    # =========================================================
    # 16. SFH
    # =========================================================

    def sfh(self):

        if self.soup is None:
            return -1

        try:

            forms = self.soup.find_all(
                "form"
            )

            if not forms:
                return 1

            result = 1

            for form in forms:

                action = (
                    form.get("action")
                    or ""
                ).strip()

                if (
                    not action
                    or action.lower()
                    == "about:blank"
                ):
                    return -1

                if self._is_external_url(
                    action
                ):
                    result = 0

            return result

        except Exception:

            return -1

    # =========================================================
    # 17. SUBMITTING TO EMAIL
    # =========================================================

    def submitting_to_email(self):

        if self.soup is None:
            return -1

        html = str(
            self.soup
        ).lower()

        if (
            "mailto:" in html
            or "mail(" in html
        ):
            return -1

        return 1

    # =========================================================
    # 18. ABNORMAL URL
    # =========================================================

    def abnormal_url(self):
        """
        Practical WHOIS-based approximation.

        Checks whether the hostname is consistent with
        the domain information returned by WHOIS.
        """

        try:

            info = self._get_whois()

            if info is None:
                return -1

            domain_name = info.domain_name

            if isinstance(
                domain_name,
                list,
            ):
                domain_names = [
                    str(item).lower()
                    for item in domain_name
                ]

            elif domain_name:

                domain_names = [
                    str(domain_name).lower()
                ]

            else:

                return -1

            host = self.hostname.removeprefix(
                "www."
            )

            for domain in domain_names:

                domain = domain.removeprefix(
                    "www."
                )

                if (
                    host == domain
                    or host.endswith(
                        "." + domain
                    )
                ):
                    return 1

            return -1

        except Exception:

            return -1

    # =========================================================
    # 19. REDIRECT
    # =========================================================

    def redirect(self):

        if self.response is None:
            return -1

        try:

            count = len(
                self.response.history
            )

            if count <= 1:
                return 1

            if count <= 4:
                return 0

            return -1

        except Exception:

            return -1

    # =========================================================
    # 20. ON MOUSEOVER
    # =========================================================

    def on_mouseover(self):

        if self.soup is None:
            return -1

        html = str(
            self.soup
        ).lower()

        patterns = [
            "onmouseover",
            "window.status",
        ]

        return (
            -1
            if any(
                item in html
                for item in patterns
            )
            else 1
        )

    # =========================================================
    # 21. RIGHT CLICK
    # =========================================================

    def right_click(self):

        if self.soup is None:
            return -1

        html = str(
            self.soup
        ).lower()

        patterns = [
            "event.button==2",
            "event.button == 2",
            "oncontextmenu",
            "contextmenu",
        ]

        return (
            -1
            if any(
                item in html
                for item in patterns
            )
            else 1
        )

    # =========================================================
    # 22. POPUP WINDOW
    # =========================================================

    def popup_window(self):

        if self.soup is None:
            return -1

        html = str(
            self.soup
        ).lower()

        patterns = [
            "window.open(",
            "prompt(",
        ]

        return (
            -1
            if any(
                item in html
                for item in patterns
            )
            else 1
        )

    # =========================================================
    # 23. IFRAME
    # =========================================================

    def iframe(self):

        if self.soup is None:
            return -1

        frames = self.soup.find_all(
            ["iframe", "frame"]
        )

        return (
            -1
            if frames
            else 1
        )

    # =========================================================
    # 24. AGE OF DOMAIN
    # =========================================================

    def age_of_domain(self):

        try:

            info = self._get_whois()

            if info is None:
                return -1

            creation = self._first_date(
                info.creation_date
            )

            if creation is None:
                return -1

            if creation.tzinfo is None:

                now = datetime.now()

            else:

                creation = (
                    creation.astimezone(
                        timezone.utc
                    )
                )

                now = datetime.now(
                    timezone.utc
                )

            age_days = (
                now - creation
            ).days

            return (
                1
                if age_days >= 180
                else -1
            )

        except Exception:

            return -1

    # =========================================================
    # 25. DNS RECORD
    # =========================================================

    def dns_record(self):

        try:

            socket.getaddrinfo(
                self.hostname,
                None,
            )

            return 1

        except Exception:

            return -1

    # =========================================================
    # 26. WEB TRAFFIC
    # =========================================================

    def web_traffic(self):
        """
        The original dataset's traffic-ranking source cannot be
        reproduced reliably from a raw URL without an external
        ranking service.

        Practical live approximation:
        reachable successful website -> 1
        reachable but error response -> 0
        unreachable -> -1
        """

        if self.response is None:
            return -1

        try:

            status = (
                self.response.status_code
            )

            if 200 <= status < 400:
                return 1

            return 0

        except Exception:

            return -1

    # =========================================================
    # 27. PAGE RANK
    # =========================================================

    def page_rank(self):
        """
        True historical Google PageRank is not available through
        a normal public lookup.

        Conservative approximation using domain age and live
        reachability.
        """

        age = self.age_of_domain()

        if (
            age == 1
            and self.response is not None
            and self.response.status_code < 400
        ):
            return 1

        return -1

    # =========================================================
    # 28. GOOGLE INDEX
    # =========================================================

    def google_index(self):
        """
        Direct Google-index querying is unreliable and can violate
        search-engine automation restrictions.

        Practical approximation based on domain availability and
        successful page retrieval.
        """

        dns = self.dns_record()

        if (
            dns == 1
            and self.response is not None
            and self.response.status_code < 400
        ):
            return 1

        return -1

    # =========================================================
    # 29. LINKS POINTING TO PAGE
    # =========================================================

    def links_pointing_to_page(self):
        """
        Approximation based on internal links present in the
        retrieved page.

        True backlinks require an external backlink index.
        """

        if self.soup is None:
            return -1

        try:

            anchors = self.soup.find_all(
                "a",
                href=True,
            )

            internal = 0

            for anchor in anchors:

                href = anchor.get(
                    "href"
                )

                if (
                    href
                    and not self._is_external_url(
                        href
                    )
                ):
                    internal += 1

            if internal == 0:
                return -1

            if internal <= 2:
                return 0

            return 1

        except Exception:

            return -1

    # =========================================================
    # 30. STATISTICAL REPORT
    # =========================================================

    def statistical_report(self):
        """
        The original feature may depend on external reputation /
        blacklist information.

        This local approximation checks a few structural warning
        signs without calling an external blacklist API.
        """

        try:

            suspicious_score = 0

            # Raw IP used as hostname
            if (
                self.having_ip_address()
                == -1
            ):
                suspicious_score += 1

            # Known URL shortener
            if (
                self.shortening_service()
                == -1
            ):
                suspicious_score += 1

            # Suspicious TLD
            parts = self.hostname.split(
                "."
            )

            if parts:

                tld = parts[-1].lower()

                if (
                    tld
                    in self.SUSPICIOUS_TLDS
                ):
                    suspicious_score += 1

            # No DNS
            if (
                self.dns_record()
                == -1
            ):
                suspicious_score += 1

            return (
                -1
                if suspicious_score >= 2
                else 1
            )

        except Exception:

            return -1

    # =========================================================
    # EXTRACT ALL 30 FEATURES
    # =========================================================

    def extract_features(self):

        features = {

            "having_IP_Address":
                self.having_ip_address(),

            "URL_Length":
                self.url_length(),

            "Shortining_Service":
                self.shortening_service(),

            "having_At_Symbol":
                self.having_at_symbol(),

            "double_slash_redirecting":
                self.double_slash_redirecting(),

            "Prefix_Suffix":
                self.prefix_suffix(),

            "having_Sub_Domain":
                self.having_sub_domain(),

            "SSLfinal_State":
                self.ssl_final_state(),

            "Domain_registeration_length":
                self.domain_registration_length(),

            "Favicon":
                self.favicon(),

            "port":
                self.port_feature(),

            "HTTPS_token":
                self.https_token(),

            "Request_URL":
                self.request_url(),

            "URL_of_Anchor":
                self.url_of_anchor(),

            "Links_in_tags":
                self.links_in_tags(),

            "SFH":
                self.sfh(),

            "Submitting_to_email":
                self.submitting_to_email(),

            "Abnormal_URL":
                self.abnormal_url(),

            "Redirect":
                self.redirect(),

            "on_mouseover":
                self.on_mouseover(),

            "RightClick":
                self.right_click(),

            # Keep original dataset spelling
            "popUpWidnow":
                self.popup_window(),

            "Iframe":
                self.iframe(),

            "age_of_domain":
                self.age_of_domain(),

            "DNSRecord":
                self.dns_record(),

            "web_traffic":
                self.web_traffic(),

            "Page_Rank":
                self.page_rank(),

            "Google_Index":
                self.google_index(),

            "Links_pointing_to_page":
                self.links_pointing_to_page(),

            "Statistical_report":
                self.statistical_report(),
        }

        return features

    # =========================================================
    # RETURN EXACT MODEL INPUT DATAFRAME
    # =========================================================

    def get_dataframe(self):

        features = (
            self.extract_features()
        )

        df = pd.DataFrame(
            [features]
        )

        # Force exact training column order
        df = df[
            self.FEATURE_COLUMNS
        ]

        return df