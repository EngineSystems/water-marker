import pathlib
import time
import sys

from gooey import Gooey, GooeyParser
from PIL import Image
from pillow_heif import register_heif_opener  # support for HEIF images

register_heif_opener()


def overlay_images(
    source_path,
    input_output_folder_pairs,
    reference_corner,
    corner_offset_factor,
    border_offset_factor_horizontal,
    border_offset_factor_vertical,
    overlay_bounded_scale_factor,
    overlay_width_bounded_scale_factor,
    overlay_height_bounded_scale_factor,
):
    last_dest_size = None
    # Load source image with alpha transparency
    source = last_source_resized = Image.open(source_path).convert("RGBA")

    resolved_io_folder_pairs = tuple(
        (
            pathlib.Path(io_folder_pair[0]).resolve(),
            pathlib.Path(io_folder_pair[1]).resolve(),
        )
        for io_folder_pair in input_output_folder_pairs
    )

    current_image_num = 0
    total_images = sum(
        len(tuple(io_folder_pair[0].glob("*")))
        for io_folder_pair in resolved_io_folder_pairs
    )

    for io_folder_pair in resolved_io_folder_pairs:
        i_folder_path, o_folder_path = io_folder_pair

        dest_images = tuple(i_folder_path.glob("*"))
        # Iterate over destination images

        print(f"\n\n------ Processing Folder '{i_folder_path}' ------\n\n")

        for dest_path in dest_images:
            dest_output_path = o_folder_path / dest_path.name

            if dest_output_path.exists():
                print(
                    f"Skipping '{dest_path}' as it was already processed "
                    f"and saved at '{dest_output_path}' ({current_image_num+1}/{total_images} completed)"
                )
                current_image_num += 1
                continue

            if not dest_output_path.parent.exists():
                dest_output_path.parent.mkdir()

            try:
                # Attempt to open the file as an image
                dest = Image.open(dest_path).convert("RGBA")
            except (IOError, OSError, Image.DecompressionBombError):
                # Skip if the file is not a valid image
                continue

            # Calculate final pasting position after considering border offsets

            border_offset_x = border_offset_y = 0

            if corner_offset_factor:
                border_offset_x = border_offset_y = round(
                    dest.width * corner_offset_factor
                )
            elif border_offset_factor_horizontal and border_offset_factor_vertical:
                border_offset_x = round(dest.width * border_offset_factor_horizontal)
                border_offset_y = round(dest.height * border_offset_factor_vertical)

            elif border_offset_factor_horizontal:
                border_offset_x = border_offset_y = round(
                    dest.width * border_offset_factor_horizontal
                )

            elif border_offset_factor_vertical:
                border_offset_y = border_offset_x = round(
                    dest.height * border_offset_factor_vertical
                )

            if dest.size == last_dest_size:
                source_resized = last_source_resized

            elif overlay_bounded_scale_factor:
                resized_width = round(dest.width * overlay_bounded_scale_factor)
                source_resized = source.resize(
                    (
                        resized_width,
                        round(resized_width * (source.height / source.width)),
                    ),
                    Image.BICUBIC,
                )

            elif (
                overlay_width_bounded_scale_factor
                and overlay_height_bounded_scale_factor
            ):
                resized_width = round(dest.width * overlay_width_bounded_scale_factor)
                resized_height = round(
                    dest.height * overlay_height_bounded_scale_factor
                )

                source_resized = source.resize(
                    (resized_width, resized_height),
                    Image.BICUBIC,
                )

            elif overlay_width_bounded_scale_factor:
                resized_width = round(dest.width * overlay_width_bounded_scale_factor)

                source_resized = source.resize(
                    (
                        resized_width,
                        round(resized_width * (source.height / source.width)),
                    ),
                    Image.BICUBIC,
                )

            elif overlay_height_bounded_scale_factor:
                resized_height = round(
                    dest.height * overlay_height_bounded_scale_factor
                )

                source_resized = source.resize(
                    (
                        round(resized_height * (source.width / source.height)),
                        resized_height,
                    ),
                    Image.BICUBIC,
                )
            else:
                source_resized = source

            if reference_corner == "top-left":
                final_x = border_offset_x
                final_y = border_offset_y
            elif reference_corner == "top-right":
                final_x = dest.width - source_resized.width - border_offset_x
                final_y = border_offset_y
            elif reference_corner == "bottom-left":
                final_x = border_offset_x
                final_y = dest.height - source_resized.height - border_offset_y
            elif reference_corner == "bottom-right":
                final_x = dest.width - source_resized.width - border_offset_x
                final_y = dest.height - source_resized.height - border_offset_y

            result = Image.new("RGBA", dest.size)
            result.paste(dest, (0, 0))

            # Composite source image onto the destination image at specified position
            result.alpha_composite(source_resized, (final_x, final_y))

            result.convert("RGB").save(
                dest_output_path,
            )

            last_dest_size = dest.size
            last_source_resized = source_resized

            print(
                f"Overlay complete for '{dest_path}'. Result saved at "
                f"'{dest_output_path}' ({current_image_num+1}/{total_images} completed)"
            )

            time.sleep(0.01)

            current_image_num += 1


@Gooey(
    program_name=f"Water Marker",
    default_size=(800, 600),
    tabbed_groups=True,
    progress_regex=r"^.+\((?P<current>\d+)\/(?P<total>\d+) +completed\)$",
    progress_expr="current / total * 100",
)
def main():
    parser = GooeyParser(
        description="Overlay a source PNG image with alpha transparency on destination images."
    )

    main_group = parser.add_argument_group("Main")

    main_group.add_argument(
        "source_image",
        widget="FileChooser",
        help="The source PNG image to use as an overlay.",
    )
    main_group.add_argument(
        "input_folders",
        nargs="+",
        widget="MultiDirChooser",
        help="One or more folders with the destination images.",
    )
    main_group.add_argument(
        "output_folder",
        widget="DirChooser",
        default="{input_folder}/overlaid",
        help="The output folder where overlay results will be saved. "
        "Non-existing folders are automatically created when possible.\n\n "
        "Supported dynamic variables:\n\n "
        "- {input_folder} : An input folder.\n\nFor example, if an input folder "
        "is called '/Users/you/Pictures/targets', and you write "
        "'{input_folder}/overlaid' as an output folder, '{input_folder}' will "
        "be internally replaced by '/Users/you/Pictures/targets' giving you "
        "'/Users/you/Pictures/targets/overlaid'.",
    )

    advanced_group = parser.add_argument_group(
        "Advanced",
        description="Advanced options. Only change things here if you know what you "
        "are doing.\n\n ",
    )
    advanced_group.add_argument(
        "--reference-corner",
        type=str,
        nargs="?",
        default="bottom-right",
        choices=["top-left", "top-right", "bottom-left", "bottom-right"],
        help="The reference corner for positioning the overlay image.",
    )

    advanced_group.add_argument(
        "--corner-offset-factor",
        type=float,
        default=2.7,
        help="The factor in percent (%) by which to offset the overlay from the "
        "selected reference corner on a destination image, relative "
        "to the size of that destination image.",
    )

    advanced_group.add_argument(
        "--border-offset-factor-horizontal",
        type=float,
        help="The factor in percent (%) by which to offset the overlay from the "
        "selected reference corner on a destination image horizontally, relative "
        "to the size of that destination image's width.",
    )
    advanced_group.add_argument(
        "--border-offset-factor-vertical",
        type=float,
        help="The factor in percent (%) by which to offset the overlay from the "
        "selected reference corner on a destination image vertically, relative "
        "to the size of that destination image's height.",
    )
    advanced_group.add_argument(
        "--overlay-bounded-scale-factor",
        nargs="?",
        type=float,
        default=10,
        help="The factor in percent (%) by which to scale the overlay, "
        "relative to the size of a destination image.",
    )
    advanced_group.add_argument(
        "--overlay-width-bounded-scale-factor",
        nargs="?",
        type=float,
        help="The factor in percent (%) by which to scale the overlay's width, "
        "relative to a destination image's width.",
    )

    advanced_group.add_argument(
        "--overlay-height-bounded-scale-factor",
        nargs="?",
        type=float,
        default=None,
        help="The factor in percent (%) by which to scale the overlay's height, "
        "relative to a destination image's height.",
    )

    args = parser.parse_args()

    try:
        _ = "Invalid/non-existent image for 'input_folder' field."
        if not pathlib.Path(args.source_image).exists():
            print(_, file=sys.stderr)
    except TypeError:
        print(_, file=sys.stderr)
        raise

    output_folder = args.output_folder

    try:
        input_output_folder_pairs = tuple(
            (input_folder, output_folder.format(input_folder=input_folder))
            for input_folder in args.input_folders
        )
    except LookupError:
        print("Invalid text for 'input_folder' field.", file=sys.stderr)
        raise

    if not any(
        (
            args.corner_offset_factor,
            args.border_offset_factor_horizontal,
            args.border_offset_factor_vertical,
        )
    ):
        print(
            "At least one of 'corner_offset_factor', "
            "'border_offset_factor_horizontal' or "
            "'border_offset_factor_vertical' must be specified.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    
    elif not any(
        (
            args.overlay_bounded_scale_factor,
            args.overlay_height_bounded_scale_factor,
            args.overlay_width_bounded_scale_factor,
        )
    ):
        print(
            "At least one of 'overlay_bounded_scale_factor', "
            "'overlay_height_bounded_scale_factor' or "
            "'overlay_width_bounded_scale_factor' must be specified.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    overlay_images(
        args.source_image,
        input_output_folder_pairs,
        (args.reference_corner / 100 if args.reference_corner else None),
        (
            args.border_offset_factor_horizontal / 100
            if args.border_offset_factor_horizontal
            else None
        ),
        (
            args.border_offset_factor_vertical / 100
            if args.border_offset_factor_vertical
            else None
        ),
        (
            args.overlay_bounded_scale_factor / 100
            if args.overlay_bounded_scale_factor
            else None
        ),
        (
            args.overlay_width_bounded_scale_factor / 100
            if args.overlay_width_bounded_scale_factor
            else None
        ),
        (
            args.overlay_height_bounded_scale_factor / 100
            if args.overlay_height_bounded_scale_factor
            else None
        ),
    )


if __name__ == "__main__":
    main()
