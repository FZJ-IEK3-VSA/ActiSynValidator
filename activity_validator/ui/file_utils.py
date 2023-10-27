import glob
from pathlib import Path
from activity_validator.hetus_data_processing import activity_profile

from activity_validator.hetus_data_processing.activity_profile import ProfileType


def ptype_to_label(profile_type: ProfileType) -> str:
    return " - ".join(profile_type.to_tuple())


def get_files(path: Path) -> list[Path]:
    assert path.exists(), f"Invalid path: {path}"
    return [f for f in path.iterdir() if f.is_file()]


def get_profile_types(path: Path) -> dict[ProfileType, Path]:
    input_prob_files = get_files(path)
    profile_types = {ProfileType.from_filename(p)[1]: p for p in input_prob_files}
    if None in profile_types:
        raise RuntimeError("Invalid file name: could not parse profile type")
    return profile_types  # type: ignore


def get_profile_type_labels(path: Path) -> list[str]:
    profile_types = get_profile_types(path)
    return [ptype_to_label(p) for p in profile_types.keys()]


def get_file_path(directory: Path, profile_type: ProfileType, ext: str = "*") -> Path:
    filter = directory / ("*" + profile_type.construct_filename() + f".{ext}")

    # find the correct file
    files = glob.glob(str(filter))
    if len(files) == 0:
        raise RuntimeError(f"Could not find a matching file: {filter}")
    if len(files) > 1:
        raise RuntimeError(f"Found multiple files for the same profile type: {files}")
    return Path(files[0])


def load_data_by_type(path, profile_type):
    filter = str(path) + "/*" + profile_type.construct_filename() + ".csv"

    # find the correct file
    files = glob.glob(filter)
    if len(files) == 0:
        raise RuntimeError(f"Could not find a matching file: {filter}")
    if len(files) > 1:
        raise RuntimeError(f"Found multiple files for the same profile type: {files}")
    # load the correct file
    _, data = activity_profile.load_df(files[0])
    return data
