# Image report — content/images.json

Generated 2026-09-30. Source: Wikimedia Commons only. Every file was checked for licence (CC0 / public domain / CC BY / CC BY-SA), JPEG, original width of 1,600 px or more, and reviewed by eye on contact sheets of 500 px thumbnails before selection. All 219 original URLs returned HTTP 200 on the final check.

## Totals

| Scope | Keys | Images |
|---|---|---|
| meghalaya | 20 | 59 |
| assam | 14 | 47 |
| arunachal | 14 | 45 |
| northeast | 8 | 24 |
| Extra keys (heroes, themes) | 16 | 44 |
| **All** | **72** | **219** |

Licences: CC BY-SA 4.0 177, CC0 11, CC BY-SA 3.0 10, CC BY 4.0 8, CC BY 2.0 7, CC BY-SA 2.0 5, CC BY 3.0 1. No file is used under two keys.

## Per place

### meghalaya

| Slug | Images | Notes |
|---|---|---|
| shillong | 3 |  |
| shillong-peak | 3 |  |
| elephant-falls | 3 |  |
| umiam-lake | 3 |  |
| laitlum-canyons | 3 |  |
| sohra | 3 |  |
| nohkalikai-falls | 3 |  |
| mawsmai-cave | 3 |  |
| nongriat-root-bridges | 3 |  |
| wei-sawdong-falls | 3 |  |
| mawlynnong | 3 |  |
| dawki-umngot | 4 |  |
| shnongpdeng | 3 | fallback (enclosing area) |
| krang-suri-falls | 3 |  |
| mawphlang-sacred-forest | 3 |  |
| nartiang-monoliths | 3 |  |
| jowai | 3 |  |
| mawsynram | 2 | thin |
| nongkhnum-island | 2 | fallback (enclosing area) |
| balpakram | 3 |  |

### assam

| Slug | Images | Notes |
|---|---|---|
| guwahati | 4 |  |
| kamakhya-temple | 3 |  |
| kaziranga | 4 |  |
| majuli | 4 |  |
| jorhat | 3 |  |
| sivasagar | 4 |  |
| dibrugarh | 3 |  |
| manas | 3 |  |
| pobitora | 3 |  |
| nameri | 3 |  |
| tezpur | 3 |  |
| haflong | 3 |  |
| dibru-saikhowa | 3 |  |
| hajo | 4 |  |

### arunachal

| Slug | Images | Notes |
|---|---|---|
| tawang | 3 |  |
| tawang-monastery | 3 |  |
| sela-pass | 4 |  |
| bum-la-pass | 4 |  |
| madhuri-lake | 3 |  |
| nuranang-falls | 3 |  |
| bomdila | 3 |  |
| dirang | 3 |  |
| ziro-valley | 3 |  |
| mechuka | 3 |  |
| itanagar | 3 |  |
| pasighat | 3 |  |
| namdapha | 3 |  |
| roing-mayodia | 4 |  |

### northeast

| Slug | Images | Notes |
|---|---|---|
| kohima | 3 |  |
| dzukou-valley | 3 |  |
| khonoma | 3 |  |
| imphal | 3 |  |
| loktak-lake | 3 |  |
| aizawl | 3 |  |
| agartala | 3 |  |
| unakoti | 3 |  |

## Extra keys

| Key | Images |
|---|---|
| _assam-tea | 3 |
| _bihu-dance | 3 |
| _brahmaputra | 3 |
| _hero-kaziranga-rhino | 2 |
| _hero-meghalaya | 2 |
| _hero-tawang | 2 |
| _hornbill-festival | 3 |
| _jadoh-or-northeast-food | 3 |
| _khasi-culture | 3 |
| _monsoon-clouds | 3 |
| _one-horned-rhino | 3 |
| _red-panda-or-hoolock | 3 |
| _root-bridge | 3 |
| _sela-snow | 2 |
| _shillong-streets | 3 |
| _ziro-rice-fields | 3 |
## Fallbacks

- **shnongpdeng** (3 images, all `fallback: true`): Commons has no licence-clean JPEG of Shnongpdeng itself (one small, untagged Umngot shot only). Used Umngot River photos from the Dawki stretch just downstream; alt text says "Umngot River … Dawki area", not Shnongpdeng.
- **nongkhnum-island** (2 images, both `fallback: true`): no photo of the river island exists on Commons. Used Weinia Falls (at Nongkhnum, Nongstoin) and Langshiang Falls (Nongstoin, West Khasi Hills), the two sights usually combined with the island.

## Thin or weaker coverage

- **mawsynram** (2): one black-and-white landscape and one Mawjymbuin cave interior. No good colour landscape of the village exists at ≥1,600 px.
- **nongkhnum-island** (2): see fallbacks.
- **nartiang-monoliths**: the three monolith photos are good; many other "Nartiang" files show the Durga temple, not the stones, and were skipped.
- **imphal**: few city views; hero is "Imphal At Dusk" (city lights), plus Kangla Fort palace ruins and the Kangla enclosure wall. Consider replacing the wall shot if a better Kangla or Ima Keithel photo appears.
- **loktak-lake**: only one strong phumdi photo (the hero). The other two are daytime jetty and canoe shots at the lakeshore.
- **pasighat**: the Siang hero was taken at Ranaghat on the Siang, just outside Pasighat, where the river leaves the hills for the plains. The town shots are only average.
- **_shillong-streets**: there are few good street photos. Hero is Police Bazaar at night. The second image shows identifiable people (a family walking); swap it if the site avoids recognisable non-performers.
- **_hero-meghalaya, _hero-kaziranga-rhino, _hero-tawang, _sela-snow**: 2 images each, as briefed for heroes.

## People and personality rights

The culture keys (_khasi-culture, _bihu-dance, _hornbill-festival) and _assam-tea show performers or workers at public events or at work, taken from Commons under free licences. Commons licences cover copyright only. They do not grant personality or model rights. These images suit editorial and illustrative use. Do not use them in ads or to imply endorsement. We skipped Hornbill files with a copyright watermark or burnt-in date stamp.

## How to reproduce

```
node tools/fetch-images.mjs candidates [key ...]     # licence-clean candidates -> .cache/commons/candidates
node tools/fetch-images.mjs sheet <key> [page] [re]   # numbered contact sheet -> .cache/commons/sheets
node tools/fetch-images.mjs search <key> "terms" "Category:X"
node tools/fetch-images.mjs build                    # tools/image-selection.json -> content/images.json + URL check
```

Search terms per key live in `tools/image-queries.mjs`. The curated picks and alt text live in `tools/image-selection.json`.
