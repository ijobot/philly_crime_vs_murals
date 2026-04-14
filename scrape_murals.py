"""
Scrape Mural Arts Philadelphia and output a GeoJSON file.
Fields kept: artist name, mural name, address, geo (lon/lat), media (image sources),
             year_created, date_groups, is_active.
"""

import json
import time
import requests

API_URL = "https://api-ng.publicartarchive.org/graphql"

QUERY = """
query SearchArtsList($dto: SearchArtsInput!) {
  searchArts(dto: $dto) {
    items {
      id
      titles
      artists
      address {
        address
        city
        state
        zip
        country
      }
      geo
      media {
        source
        title
        mediaType
      }
      dateGroups {
        type
        display
      }
      yearCreated
      metaInfo {
        status
        mapView
      }
    }
    meta {
      totalItems
      totalPages
      currentPage
      hasMore
    }
  }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://www.muralarts.org",
    "Referer": "https://www.muralarts.org/",
}


def fetch_page(page: int, limit: int = 100) -> dict:
    payload = {
        "operationName": "SearchArtsList",
        "query": QUERY,
        "variables": {
            "dto": {
                "filterCategories": [
                    {
                        "category": "collections.keyword",
                        "values": ["Mural Arts Philadelphia"]
                    }
                ],
                "page": page,
                "limit": limit,
                "sort": {
                    "orderField": "titles.keyword",
                    "orderDirection": "ASC"
                }
            }
        }
    }
    resp = requests.post(API_URL, json=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all_murals(limit: int = 100) -> list[dict]:
    murals = []
    page = 1

    while True:
        print(f"  Fetching page {page} ...")
        data = fetch_page(page, limit)
        items = data.get("data", {}).get("searchArts", {}).get("items", [])
        meta  = data.get("data", {}).get("searchArts", {}).get("meta", {})

        if not items:
            break

        murals.extend(items)
        print(f"    Got {len(items)} items (total so far: {len(murals)} / {meta.get('totalItems', '?')})")

        if not meta.get("hasMore"):
            break

        page += 1
        time.sleep(0.5)

    return murals


def is_active_mural(item: dict) -> bool:
    """Return False for temporary or off-view murals."""
    meta = item.get("metaInfo") or {}
    if meta.get("status") == "temp":
        return False
    if meta.get("mapView") == "offview":
        return False
    return True


def extract_year_created(item: dict) -> str | None:
    """
    Try dateGroups first (type=creation), fall back to yearCreated.
    Returns a string like '2009' or '3/15/2012', or None if unavailable.
    """
    date_groups = item.get("dateGroups") or []
    for group in date_groups:
        if group.get("type") == "creation":
            return group.get("display")

    # Fallback to top-level yearCreated
    return item.get("yearCreated") or None


def mural_to_feature(item: dict) -> dict | None:
    geo = item.get("geo")
    if not geo or len(geo) < 2:
        return None

    lon, lat = geo[0], geo[1]

    addr = item.get("address") or {}
    address_str = ", ".join(filter(None, [
        addr.get("address"),
        addr.get("city"),
        addr.get("state"),
        addr.get("zip"),
        addr.get("country"),
    ]))

    media_sources = [
        m["source"] for m in (item.get("media") or [])
        if m.get("mediaType") == "image" and m.get("source")
    ]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat],
        },
        "properties": {
            "mural_name":   (item.get("titles") or [""])[0],
            "artist":       (item.get("artists") or [""])[0],
            "address":      address_str,
            "year_created": extract_year_created(item),
            "media":        media_sources,
        },
    }


def main():
    print("Fetching murals from Mural Arts Philadelphia...")
    murals = fetch_all_murals()
    print(f"\n  Total records fetched: {len(murals)}")

    features = []
    skipped_no_geo = 0
    skipped_inactive = 0

    for item in murals:
        if not is_active_mural(item):
            skipped_inactive += 1
            continue
        feature = mural_to_feature(item)
        if feature:
            features.append(feature)
        else:
            skipped_no_geo += 1

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    out_path = "data/murals/philadelphia_murals_raw.geojson"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"  Features written    : {len(features)}")
    print(f"  Skipped (inactive)  : {skipped_inactive}")
    print(f"  Skipped (no geo)    : {skipped_no_geo}")
    print(f"  Output file         : {out_path}")


if __name__ == "__main__":
    main()