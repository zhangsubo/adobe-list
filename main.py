import re
import sys
import os
import ipaddress
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


URL = "https://www.macat.vip/list.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(BASE_DIR, "host", "list.list")


def is_valid_domain(domain: str) -> bool:
    if not domain or len(domain) > 253:
        return False
    d = domain.lower().rstrip(".")
    try:
        ipaddress.ip_address(d)
        return False
    except ValueError:
        pass
    labels = d.split(".")
    if len(labels) < 2:
        return False
    tld = labels[-1]
    if tld.isdigit():
        return False
    label_re = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
    return all(label_re.match(x) for x in labels)


def extract_domains(text: str) -> list:
    domains = []
    seen = set()
    rx = re.compile(r"(?<![a-zA-Z0-9-])([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+)")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        for m in rx.findall(line):
            candidate = m.lower().lstrip(".*")
            if is_valid_domain(candidate) and candidate not in seen:
                seen.add(candidate)
                domains.append(candidate)
    return domains


def fetch_text(url: str) -> str:
    try:
        with urlopen(url, timeout=30) as resp:
            data = resp.read()
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")
    except (URLError, HTTPError) as e:
        raise RuntimeError(f"fetch failed: {e}")


def write_output(domains: list, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    content = "\n".join(f"DOMAIN,{d}" for d in domains)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def main() -> None:
    text = fetch_text(URL)
    domains = extract_domains(text)
    write_output(domains, OUTPUT_PATH)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
