import re
import subprocess
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import pytest
import yaml
from matplotlib.colors import BoundaryNorm

from clear import viz

GLOSSARY = Path(__file__).resolve().parents[2] / "GLOSSARY.md"


def glossary_code_names() -> set[str]:
    # Second column of every GLOSSARY table row: | Term | `code_name` | ...
    text = GLOSSARY.read_text(encoding="utf-8")
    return set(re.findall(r"^\|[^|]+\|\s*`([a-z0-9_/]+)`\s*\|", text, flags=re.MULTILINE))


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout


def sidecar_meta(saved: viz.SavedFigure) -> dict[str, object]:
    return yaml.safe_load(saved.sidecar.read_text(encoding="utf-8").split("---")[1])


def test_tokens_load_and_cover_every_role_group():
    tokens = viz.load_tokens()
    assert tokens.alert_levels.provisional is True
    assert set(tokens.alert_levels.order) == set(tokens.alert_levels.colors)
    assert set(tokens.sources) == {
        "naps",
        "mecp",
        "aqs",
        "purpleair",
        "satellite",
        "era5",
        "airnow",
    }
    assert set(tokens.sources) == set(tokens.source_labels)
    assert len(tokens.categorical) == 8


def test_source_keys_are_glossary_code_names():
    # color("source.<key>") is the role name every figure uses; it must match the data.
    assert set(viz.load_tokens().sources) <= glossary_code_names()


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        ("alert.high", "#FF0000"),
        ("source.naps", "#0072B2"),
        ("source.mecp", "#56B4E9"),
        ("source.aqs", "#009E73"),
        ("neutral.ink", "#1A1A1A"),
        ("cat.0", "#0072B2"),
        ("aqhi.10+", "#660000"),
    ],
)
def test_color_roles_resolve(role, expected):
    assert viz.color(role) == expected


@pytest.mark.parametrize(
    "role",
    ["alert.extreme", "source.unknown", "source.epa", "source.ontario_mecp", "red", "cat.99"],
)
def test_unknown_color_role_raises(role):
    with pytest.raises(KeyError):
        viz.color(role)


@pytest.mark.parametrize(
    ("name", "width_in"),
    [("paper-1col", 3.5), ("paper-2col", 7.2), ("slide-16x9", 13.33), ("poster", 16.0)],
)
def test_preset_sizes(name, width_in):
    assert viz.preset(name).width_in == width_in


def test_unknown_preset_raises():
    with pytest.raises(KeyError):
        viz.preset("a4")


def test_alert_cmap_follows_level_order():
    cmap = viz.alert_cmap()
    assert len(viz.load_tokens().alert_levels.order) == cmap.N


def test_pm25_norm_requires_increasing_breakpoints():
    assert isinstance(viz.pm25_norm([0.0, 10.0, 20.0]), BoundaryNorm)
    with pytest.raises(ValueError, match="strictly increasing"):
        viz.pm25_norm([10.0, 5.0])


def test_plotly_template_uses_token_colorway():
    template = viz.plotly_template()
    layout = template["layout"]
    assert isinstance(layout, dict)
    assert layout["colorway"] == viz.load_tokens().categorical


def test_save_figure_writes_png_svg_and_sidecar(tmp_path: Path):
    data = tmp_path / "input.csv"
    data.write_text("time_utc,pm25_ugm3\n", encoding="utf-8")
    viz.use_style("paper-1col")
    fig, ax = viz.new_figure("paper-1col")
    ax.plot([0, 1], [0, 1], color=viz.color("source.naps"))

    saved = viz.save_figure(
        fig, "unit-test", caption="Test.", inputs=[data], preset="paper-1col", out_dir=tmp_path
    )

    assert saved.png.is_file()
    assert saved.svg.is_file()
    meta = sidecar_meta(saved)
    assert meta["slug"] == "unit-test"
    assert meta["preset"] == "paper-1col"
    assert meta["headline"] is False
    inputs = meta["inputs"]
    assert isinstance(inputs, list) and len(inputs) == 1
    assert len(inputs[0]["sha256"]) == 64
    assert str(meta["script"]).endswith("test_viz.py")


def test_saved_files_have_exactly_the_preset_size(tmp_path: Path):
    # A tight bbox would crop the saved file; the preset width must hold on disk.
    viz.use_style("paper-1col")
    p = viz.preset("paper-1col")
    fig, ax = viz.new_figure("paper-1col")
    ax.set_title("A long title that reaches the edge of the panel")
    ax.set_ylabel("PM2.5 (µg/m³)")
    saved = viz.save_figure(
        fig, "size-test", caption="x", inputs=[], preset="paper-1col", out_dir=tmp_path
    )
    plt.close(fig)

    height_px, width_px = mpimg.imread(saved.png).shape[:2]
    assert (width_px, height_px) == (round(p.width_in * p.dpi), round(p.height_in * p.dpi))
    svg_width = re.search(r'width="([\d.]+)pt"', saved.svg.read_text(encoding="utf-8"))
    assert svg_width is not None
    assert float(svg_width.group(1)) == pytest.approx(p.width_in * 72)  # SVG is in points


def test_save_figure_rejects_bad_slug_wrong_width_and_missing_input(tmp_path: Path):
    fig, _ = viz.new_figure("paper-1col")
    with pytest.raises(ValueError, match="slug"):
        viz.save_figure(
            fig, "Bad_Slug", caption="x", inputs=[], preset="paper-1col", out_dir=tmp_path
        )
    with pytest.raises(ValueError, match="width"):
        viz.save_figure(fig, "ok", caption="x", inputs=[], preset="paper-2col", out_dir=tmp_path)
    with pytest.raises(FileNotFoundError, match="missing.csv"):
        viz.save_figure(
            fig,
            "ok",
            caption="x",
            inputs=[tmp_path / "missing.csv"],
            preset="paper-1col",
            out_dir=tmp_path,
        )
    # Every check runs before the first write: nothing half-written is left behind.
    assert list(tmp_path.iterdir()) == []


def test_git_commit_is_dirty_unless_head_holds_script_and_inputs(
    git_repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("CLEAR_ROOT", str(git_repo))
    (git_repo / "fig_demo.py").write_text("# demo\n", encoding="utf-8")
    (git_repo / "input.csv").write_text("a\n", encoding="utf-8")
    git(git_repo, "add", "-A")
    git(git_repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "init")
    head = git(git_repo, "rev-parse", "--short", "HEAD").strip()

    def commit_of(script: str) -> object:
        fig, _ = viz.new_figure("paper-1col")
        saved = viz.save_figure(
            fig,
            "demo",
            caption="x",
            inputs=["input.csv"],
            preset="paper-1col",
            out_dir=tmp_path / "out",
            script=script,
        )
        plt.close(fig)
        return sidecar_meta(saved)["git_commit"]

    assert commit_of("fig_demo.py") == head
    (git_repo / "unrelated.txt").write_text("x\n", encoding="utf-8")
    assert commit_of("fig_demo.py") == head  # changes elsewhere do not matter
    (git_repo / "input.csv").write_text("b\n", encoding="utf-8")
    assert commit_of("fig_demo.py") == f"{head}-dirty"  # modified input
    git(git_repo, "checkout", "--", "input.csv")
    (git_repo / "fig_new.py").write_text("# new\n", encoding="utf-8")
    assert commit_of("fig_new.py") == f"{head}-dirty"  # untracked script
    git(git_repo, "add", "fig_new.py")
    assert commit_of("fig_new.py") == f"{head}-dirty"  # staged, not committed


def test_map_projection_and_domain_are_typed_and_provisional():
    proj = viz.map_projection()
    assert proj.name == "lambert_conformal"
    assert len(proj.standard_parallels_deg) == 2
    domain = viz.map_domain()
    assert domain.provisional is True
    assert domain.half_width_km > 0


def test_map_axes_is_centred_on_the_domain():
    ccrs = pytest.importorskip("cartopy.crs")
    domain = viz.map_domain()
    fig = plt.figure()
    ax = viz.map_axes(fig)
    # map_axes returns a cartopy GeoAxes, typed as plain Axes (cartopy is untyped).
    map_crs = ax.projection  # pyright: ignore[reportAttributeAccessIssue]
    (x0, x1), (y0, y1) = ax.get_xlim(), ax.get_ylim()
    plt.close(fig)
    assert x1 - x0 == pytest.approx(2 * domain.half_width_km * 1000)
    lon, lat = ccrs.Geodetic().transform_point((x0 + x1) / 2, (y0 + y1) / 2, map_crs)
    assert (lat, lon) == pytest.approx((domain.center_lat_deg, domain.center_lon_deg))
