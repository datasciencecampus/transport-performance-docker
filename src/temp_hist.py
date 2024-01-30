# %%
import os
import pathlib
from typing import Union

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pyprojroot import here
from matplotlib.patches import Patch
from shapely.geometry import box
from branca import colormap

from utils import plot

# %%
npt_path = here("data/newport_20240112_1045_python/outputs/metrics/")
london_path = here("data/london_20240112_1529/outputs/metrics/")
leeds_path = here("data/leeds_PoC_outputs_em/outputs/metrics")
marseille_path = here("data/marseille_PoC_outputs_em/outputs/metrics")

# %%


def single_hist(metrics: Union[str, pathlib.Path], title: str, out_path: str):
    df = gpd.read_parquet(metrics)

    _, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(
        df,
        x="transport_performance",
        stat="percent",
        bins=50,
        binrange=[0, 100],
    )
    ax.set_xlabel("Transport performance")
    ax.set_ylabel("Percent of cells")
    ax.set_title(title)
    ax.set_ylim(0, 12)
    sns.despine()
    plt.savefig(out_path)
    plt.show()


# %%
# newport
single_hist(
    os.path.join(npt_path, "transport_performance.parquet"),
    "Newport",
    os.path.join(npt_path, "hist.png"),
)
# %%
# london
single_hist(
    os.path.join(london_path, "transport_performance.parquet"),
    "London",
    os.path.join(london_path, "hist.png"),
)
# %%
# marseille
single_hist(
    os.path.join(marseille_path, "transport_performance.parquet"),
    "Marseille",
    os.path.join(marseille_path, "hist.png"),
)

# %%
# leeds
single_hist(
    os.path.join(leeds_path, "transport_performance.parquet"),
    "Leeds",
    os.path.join(leeds_path, "hist.png"),
)
# %%
leeds_df = gpd.read_parquet(os.path.join(leeds_path, "transport_performance.parquet"))
marseille_df = gpd.read_parquet(
    os.path.join(marseille_path, "transport_performance.parquet")
)

# %%
# remove bradford
bbox_gdf = gpd.GeoDataFrame(
    geometry=[box(*[-1.685271, 53.703581, -1.251998, 53.924119])],
    crs='epsg: 4326'
).to_crs('esri: 54009')
bounds = bbox_gdf.total_bounds
leeds_only = leeds_df.cx[bounds[0]:bounds[2], bounds[1]: bounds[3]]

# %%
plot(
    leeds_only,
    column="transport_performance",
    column_control_name="Transport Performance",
    uc_gdf=None,
    cmap="viridis",
    caption="Transport Performance (%)",
    save=here('data/leeds_PoC_outputs_em/outputs/metrics/transport_performance_leeds_only.html'),
)

const_cmap = colormap.LinearColormap(
    colors=[
        "#440154",
        "#414487",
        "#2A788E",
        "#22A884",
        "#7AD151",
        "#FDE725",
    ],
    vmin=0,
    vmax=100,
    max_labels=11,
    tick_labels=list(range(0, 110, 10)),
)
plot(
    leeds_only,
    column="transport_performance",
    column_control_name="Transport Performance",
    uc_gdf=None,
    cmap=const_cmap,
    caption="Transport Performance (%)",
    save=here('data/leeds_PoC_outputs_em/outputs/metrics/transport_performance_const_cmap_leeds_only.html'),
)

# %%

legend_elements = (
    Patch(
        facecolor='#1f77b4',
        edgecolor='black',
        alpha=0.5,
        label='Leeds'
    ),
    Patch(
        facecolor='#ff7f0e',
        edgecolor='black',
        alpha=0.5,
        label='Marseille'
    )
)

_, ax = plt.subplots(figsize=(7, 5))
sns.histplot(
    leeds_only,
    x="transport_performance",
    stat="percent",
    bins=50,
    binrange=[0, 100],
    ax=ax,
    alpha=0.4,
    multiple="dodge"
)
sns.histplot(
    marseille_df,
    x="transport_performance",
    stat="percent",
    bins=50,
    binrange=[0, 100],
    ax=ax,
    alpha=0.4,
    multiple="dodge",
)

ax.set_xlabel("Transport performance")
ax.set_ylabel("Percent of cells")
ax.set_ylim(0, 12)
ax.set_title('Leeds vs Marseille')
ax.legend(handles=legend_elements, loc='center right')
sns.despine()
plt.savefig(os.path.join(leeds_path, "comp_hist_leeds_only.png"))
plt.show()
# %%
