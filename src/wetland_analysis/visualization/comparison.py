"""
Visualization functions for dataset comparison and multi-scale analysis.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import seaborn as sns
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Union
import logging

logger = logging.getLogger(__name__)

def plot_spatial_agreement(
    ds_a: xr.DataArray,
    ds_b: xr.DataArray,
    name_a: str = "Dataset A",
    name_b: str = "Dataset B",
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[Union[str, Path]] = None
) -> plt.Figure:
    """
    Plot spatial agreement between two binary datasets (Bivariate Map).
    
    Categories:
    - 0: Both absent (Background)
    - 1: Only A present
    - 2: Only B present
    - 3: Both present (Consensus)
    """
    # Ensure datasets are aligned and binary
    agreement = xr.full_like(ds_a, 0, dtype=np.uint8)
    
    # Logic: A=1, B=1 -> 3; A=1, B=0 -> 1; A=0, B=1 -> 2
    agreement = agreement.where(ds_a == 0, 1)
    agreement = xr.where((ds_a == 0) & (ds_b == 1), 2, agreement)
    agreement = xr.where((ds_a == 1) & (ds_b == 1), 3, agreement)
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Custom color palette (Colorblind friendly)
    # 0: white, 1: green (Only A), 2: purple (Only B), 3: blue (Consensus)
    cmap = plt.cm.colors.ListedColormap(['#ffffff', '#2ca02c', '#9467bd', '#1f77b4'])
    
    im = agreement.plot(
        ax=ax, 
        cmap=cmap, 
        add_colorbar=False,
        levels=[0, 1, 2, 3, 4]
    )
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ca02c', label=f'Only {name_a}'),
        Patch(facecolor='#9467bd', label=f'Only {name_b}'),
        Patch(facecolor='#1f77b4', label='Consensus (Both)')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    ax.set_title(f"Spatial Agreement: {name_a} vs {name_b}")
    ax.coastlines()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def plot_multiscale_comparison(
    ds_high: xr.DataArray,
    ds_low: xr.DataArray,
    coarsen_factor: int = 10,
    figsize: Tuple[int, int] = (18, 6),
    save_path: Optional[Union[str, Path]] = None
) -> plt.Figure:
    """
    Plot high-res data, its coarsened version, and a low-res dataset side-by-side.
    """
    # 1. Calculate coarsened version
    ds_coarsened = ds_high.coarsen(lat=coarsen_factor, lon=coarsen_factor, boundary='trim').mean()
    
    fig, axes = plt.subplots(1, 3, figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # High-res
    ds_high.plot(ax=axes[0], cmap='Blues', add_colorbar=False)
    axes[0].set_title(f"Original High-Res (30m)")
    
    # Coarsened
    ds_coarsened.plot(ax=axes[1], cmap='Blues', add_colorbar=False)
    axes[1].set_title(f"Coarsened (x{coarsen_factor})")
    
    # Low-res comparison
    ds_low.plot(ax=axes[2], cmap='Blues', add_colorbar=False)
    axes[2].set_title(f"Comparison Low-Res")
    
    for ax in axes:
        ax.coastlines()
        
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def plot_uncertainty_heatmap(
    entropy: xr.DataArray,
    threshold: float = 0.8,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[Union[str, Path]] = None
) -> plt.Figure:
    """
    Plot normalized Shannon Entropy heatmap with hotspot highlighting.
    """
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Hot colormap for uncertainty
    im = entropy.plot(ax=ax, cmap='hot', vmin=0, vmax=1, cbar_kwargs={'label': 'Shannon Entropy'})
    
    # Overlay contours for hotspots
    hotspots = entropy.where(entropy > threshold)
    hotspots.plot.contour(ax=ax, colors='cyan', linewidths=0.5)
    
    ax.set_title(f"Uncertainty Heatmap (Hotspots > {threshold})")
    ax.coastlines()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def plot_temporal_comparison(
    ds_list: List[xr.DataArray],
    names: List[str],
    region_name: str = "ROI",
    figsize: Tuple[int, int] = (12, 6),
    save_path: Optional[Union[str, Path]] = None
) -> plt.Figure:
    """
    Plot time-series comparison of wetland extent/frequency across datasets.
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    for ds, name in zip(ds_list, names):
        if 'time' in ds.dims:
            # Spatial average
            extent = ds.mean(dim=['lat', 'lon'], skipna=True)
            extent.plot(ax=ax, label=name, marker='o')
        else:
            logger.warning(f"Dataset {name} does not have a time dimension. Skipping.")
            
    ax.set_title(f"Wetland Extent Time-Series: {region_name}")
    ax.set_ylabel("Mean Inundation / Extent")
    ax.legend()
    sns.despine()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
        
    return fig

def save_interactive_map(m, output_path: Union[str, Path]):
    """
    Save a geemap/ipyleaflet Map object as an image.
    """
    import geemap
    if isinstance(output_path, Path):
        output_path = str(output_path)
    
    try:
        m.to_image(filename=output_path)
        logger.info(f"Interactive map saved to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save interactive map: {e}")
