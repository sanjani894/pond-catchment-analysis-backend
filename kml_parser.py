import io
import zipfile
import xml.etree.ElementTree as ET


KML_NAMESPACE = {"kml": "http://www.opengis.net/kml/2.2"}


def _get_kml_content(file_bytes: bytes, filename: str) -> bytes:
    """Return the KML XML content from a KML or KMZ file."""

    if filename.lower().endswith(".kmz"):
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as kmz:
            kml_files = [
                name for name in kmz.namelist()
                if name.lower().endswith(".kml")
            ]

            if not kml_files:
                raise ValueError("No KML file found inside KMZ")

            return kmz.read(kml_files[0])

    if filename.lower().endswith(".kml"):
        return file_bytes

    raise ValueError("Only KML and KMZ files are supported")


def parse_contours(file_bytes: bytes, filename: str) -> dict:
    """Parse contour features and return basic terrain information."""

    kml_content = _get_kml_content(file_bytes, filename)

    root = ET.fromstring(kml_content)

    placemarks = root.findall(".//kml:Placemark", KML_NAMESPACE)

    elevations = []
    contour_count = 0

    for placemark in placemarks:
        name = placemark.find("kml:name", KML_NAMESPACE)

        if name is None or name.text is None:
            continue

        try:
            elevation = float(name.text.strip())
        except ValueError:
            continue

        elevations.append(elevation)
        contour_count += 1

    if not elevations:
        raise ValueError("No contour elevations found in the input file")

    return {
        "filename": filename,
        "contour_count": contour_count,
        "min_elevation": min(elevations),
        "max_elevation": max(elevations)
    }