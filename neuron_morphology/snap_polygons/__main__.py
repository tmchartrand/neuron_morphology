import logging
import copy as cp

import shapely


from argschema.argschema_parser import ArgSchemaParser

from neuron_morphology.snap_polygons._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.snap_polygons._from_lims import FromLimsSource
from neuron_morphology.snap_polygons.geometries import (
    Geometries, make_scale_transform, clear_overlaps, closest_from_stack, 
    get_snapped_polys, find_vertical_surfaces
)
from neuron_morphology.snap_polygons.image_outputter import ImageOutputter


def main(
    layer_polygons, 
    pia_surface, 
    wm_surface, 
    layer_order,
    working_scale: float,
    images=None
):
    """
    """

    bounds = shapely.geometry.polygon.Polygon(pia_surface["path"][::-1] + wm_surface["path"][::])

    geometries = Geometries()
    geometries.register_polygons(layer_polygons)
    geometries.register_surface("pia", pia_surface["path"])
    geometries.register_surface("wm", wm_surface["path"])

    scale_transform = make_scale_transform(working_scale)
    working_geo = geometries.transform(scale_transform)

    raster_stack = working_geo.rasterize()
    clear_overlaps(raster_stack)
    closest, closest_names = closest_from_stack(raster_stack)
    snapped_polys = get_snapped_polys(closest, closest_names)

    result_geos = Geometries()
    result_geos.register_polygons(snapped_polys)

    result_geos = (result_geos
        .transform(
            lambda vt, hr: (
                vt + working_geo.close_bounds.vorigin,
                hr + working_geo.close_bounds.horigin
            )
        )
        .transform(make_scale_transform(1.0 / working_scale))
    )

    for key in list(result_geos.polygons.keys()):
        result_geos.polygons[key] = result_geos.polygons[key].intersection(bounds)

    boundaries = find_vertical_surfaces(
        result_geos.polygons, 
        layer_order, 
        pia=geometries.surfaces["pia"], 
        wm=geometries.surfaces["wm"]
    )

    result_geos.register_surfaces(boundaries)        

    outputter = ImageOutputter(
        geometries, result_geos, images
    )

    results = result_geos.to_json()
    results["images"] = outputter.write_images()

    return results


if __name__ == "__main__":

    class Parser(ArgSchemaParser):
        """
        """
        default_configurable_sources = \
            ArgSchemaParser.default_configurable_sources + [FromLimsSource]

    parser = Parser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = main(**args)
    output.update({"inputs": parser.args})

    if "output_json" in parser.args:
        parser.output(output, indent=2)
    else:
        print(parser.get_output_json(output))