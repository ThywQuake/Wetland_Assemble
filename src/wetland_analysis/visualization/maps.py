"""
Map visualization functions for wetland datasets.
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib import colors
from typing import Optional, Tuple, Dict, List, Union
import logging

logger = logging.getLogger(__name__)


def plot_wetland_map(
    data: xr.DataArray,
    title: str = "Wetland Distribution",
    cmap: str = "Blues",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    figsize: Tuple[int, int] = (12, 8),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot wetland distribution map.

    Parameters
    ----------
    data : xr.DataArray
        Wetland data to plot
    title : str, optional
        Plot title
    cmap : str, optional
        Colormap name
    vmin, vmax : float, optional
        Value range for colormap
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    # Create figure with cartopy projection
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

    # Determine value range if not provided
    if vmin is None:
        vmin = data.min().values
    if vmax is None:
        vmax = data.max().values

    # Plot data
    if 'lon' in data.dims and 'lat' in data.dims:
        im = ax.pcolormesh(data.lon, data.lat, data.values,
                          cmap=cmap, vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    elif 'x' in data.dims and 'y' in data.dims:
        im = ax.pcolormesh(data.x, data.y, data.values,
                          cmap=cmap, vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    else:
        raise ValueError("Data must have lon/lat or x/y coordinates")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label('Wetland Fraction/Probability')

    # Set title and grid
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

    # Set extent based on data
    if 'lon' in data.coords and 'lat' in data.coords:
        ax.set_extent([data.lon.min(), data.lon.max(),
                      data.lat.min(), data.lat.max()],
                     crs=ccrs.PlateCarree())

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Map saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_trend_map(
    trend_data: xr.Dataset,
    variable: str = 'slope',
    title: str = "Wetland Trend Analysis",
    cmap: str = 'RdBu_r',
    figsize: Tuple[int, int] = (12, 8),
    significance_mask: Optional[xr.DataArray] = None,
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot trend analysis results.

    Parameters
    ----------
    trend_data : xr.Dataset
        Trend analysis results from analyze_temporal_trends
    variable : str, optional
        Variable to plot: 'slope', 'p_value', 'significant'
    title : str, optional
        Plot title
    cmap : str, optional
        Colormap name
    figsize : tuple, optional
        Figure size (width, height)
    significance_mask : xr.DataArray, optional
        Mask for significant trends (True = significant)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    if variable not in trend_data.data_vars:
        raise ValueError(f"Variable '{variable}' not found in trend_data")

    data = trend_data[variable]

    # Create figure
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

    # Determine value range based on variable
    if variable == 'slope':
        # Center colormap at zero
        vmax = max(abs(data.min().values), abs(data.max().values))
        vmin = -vmax
        cmap = 'RdBu_r'
        label = 'Trend Slope'
    elif variable == 'p_value':
        vmin = 0
        vmax = 1
        cmap = 'viridis_r'  # Reverse viridis: low p-values (significant) are bright
        label = 'p-value'
    elif variable == 'significant':
        vmin = 0
        vmax = 1
        cmap = colors.ListedColormap(['gray', 'red'])  # Gray = not significant, Red = significant
        label = 'Significant (1=yes, 0=no)'
    else:
        vmin = data.min().values
        vmax = data.max().values
        label = variable

    # Plot data
    if 'lon' in data.dims and 'lat' in data.dims:
        im = ax.pcolormesh(data.lon, data.lat, data.values,
                          cmap=cmap, vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    elif 'x' in data.dims and 'y' in data.dims:
        im = ax.pcolormesh(data.x, data.y, data.values,
                          cmap=cmap, vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    else:
        raise ValueError("Data must have lon/lat or x/y coordinates")

    # Add hatching for significant trends if requested
    if significance_mask is not None and variable != 'significant':
        # Create hatched mask for significant areas
        if 'lon' in significance_mask.dims and 'lat' in significance_mask.dims:
            ax.contourf(significance_mask.lon, significance_mask.lat,
                       significance_mask.values, levels=[0.5, 1.5],
                       hatches=['...'], alpha=0, transform=ccrs.PlateCarree())

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label(label)

    # Set title
    title_full = f"{title} - {variable}"
    ax.set_title(title_full, fontsize=14, fontweight='bold')

    # Add grid
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

    # Set extent
    if 'lon' in data.coords and 'lat' in data.coords:
        ax.set_extent([data.lon.min(), data.lon.max(),
                      data.lat.min(), data.lat.max()],
                     crs=ccrs.PlateCarree())

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Trend map saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def plot_comparison_map(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    plot_type: str = 'difference',
    title: str = "Dataset Comparison",
    figsize: Tuple[int, int] = (15, 6),
    save_path: Optional[str] = None,
    show: bool = True
) -> plt.Figure:
    """
    Plot comparison between two datasets.

    Parameters
    ----------
    dataset1, dataset2 : xr.DataArray
        Datasets to compare
    plot_type : str, optional
        Type of comparison: 'difference', 'ratio', 'side_by_side'
    title : str, optional
        Plot title
    figsize : tuple, optional
        Figure size (width, height)
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display the figure

    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    if plot_type == 'difference':
        # Plot difference map
        fig = _plot_difference_map(dataset1, dataset2, title, figsize, save_path, show)
    elif plot_type == 'ratio':
        # Plot ratio map
        fig = _plot_ratio_map(dataset1, dataset2, title, figsize, save_path, show)
    elif plot_type == 'side_by_side':
        # Plot side-by-side comparison
        fig = _plot_side_by_side(dataset1, dataset2, title, figsize, save_path, show)
    else:
        raise ValueError(f"Unknown plot_type: {plot_type}")

    return fig


def _plot_difference_map(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    title: str,
    figsize: Tuple[int, int],
    save_path: Optional[str],
    show: bool
) -> plt.Figure:
    """Plot difference map between two datasets."""
    # Calculate difference
    difference = dataset2 - dataset1

    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

    # Determine symmetric color range
    vmax = max(abs(difference.min().values), abs(difference.max().values))
    vmin = -vmax

    # Plot difference
    if 'lon' in difference.dims and 'lat' in difference.dims:
        im = ax.pcolormesh(difference.lon, difference.lat, difference.values,
                          cmap='RdBu_r', vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    else:
        raise ValueError("Data must have lon/lat coordinates")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label('Difference (Dataset2 - Dataset1)')

    # Set title
    ax.set_title(f"{title} - Difference Map", fontsize=14, fontweight='bold')

    # Add grid
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Difference map saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def _plot_ratio_map(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    title: str,
    figsize: Tuple[int, int],
    save_path: Optional[str],
    show: bool
) -> plt.Figure:
    """Plot ratio map between two datasets."""
    # Calculate ratio (avoid division by zero)
    ratio = dataset2 / dataset1.where(dataset1 != 0, other=np.nan)

    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

    # Log-scale for ratio (centered at 1)
    ratio_log = np.log10(ratio.where(ratio > 0, other=np.nan))
    vmax = max(abs(ratio_log.min().values), abs(ratio_log.max().values))
    vmin = -vmax

    # Plot ratio (log scale)
    if 'lon' in ratio.dims and 'lat' in ratio.dims:
        im = ax.pcolormesh(ratio.lon, ratio.lat, ratio_log.values,
                          cmap='RdBu_r', vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    else:
        raise ValueError("Data must have lon/lat coordinates")

    # Add colorbar with ratio labels
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)

    # Create custom tick labels for log scale
    ticks = np.array([-2, -1, 0, 1, 2])  # log10 values
    tick_labels = [f'10^{tick}' for tick in ticks]
    cbar.set_ticks(ticks)
    cbar.set_ticklabels(tick_labels)
    cbar.set_label('Ratio (Dataset2/Dataset1, log10 scale)')

    # Set title
    ax.set_title(f"{title} - Ratio Map (log scale)", fontsize=14, fontweight='bold')

    # Add grid
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Ratio map saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def _plot_side_by_side(
    dataset1: xr.DataArray,
    dataset2: xr.DataArray,
    title: str,
    figsize: Tuple[int, int],
    save_path: Optional[str],
    show: bool
) -> plt.Figure:
    """Plot side-by-side comparison of two datasets."""
    fig, axes = plt.subplots(1, 2, figsize=figsize,
                            subplot_kw={'projection': ccrs.PlateCarree()})

    datasets = [dataset1, dataset2]
    titles = ['Dataset 1', 'Dataset 2']

    for i, (ax, data, sub_title) in enumerate(zip(axes, datasets, titles)):
        # Add map features
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
        ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
        ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

        # Plot data
        if 'lon' in data.dims and 'lat' in data.dims:
            im = ax.pcolormesh(data.lon, data.lat, data.values,
                              cmap='Blues', transform=ccrs.PlateCarree())
        else:
            raise ValueError("Data must have lon/lat coordinates")

        # Add title
        ax.set_title(sub_title, fontsize=12, fontweight='bold')

        # Add grid
        ax.gridlines(draw_labels=(i == 0), linewidth=0.5, alpha=0.5)

    # Add single colorbar for both plots
    cbar = fig.colorbar(im, ax=axes, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label('Wetland Fraction/Probability')

    # Main title
    fig.suptitle(title, fontsize=14, fontweight='bold', y=0.95)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Side-by-side comparison saved to {save_path}")

    if show:
        plt.show()
    else:
        plt.close()

    return fig


def create_animation(
    time_series: xr.DataArray,
    output_path: str,
    fps: int = 5,
    figsize: Tuple[int, int] = (10, 6),
    title_template: str = "Wetland Distribution - {time}"
) -> None:
    """
    Create animation from time series data.

    Parameters
    ----------
    time_series : xr.DataArray
        Time series data with time dimension
    output_path : str
        Path to save animation (e.g., 'animation.mp4' or 'animation.gif')
    fps : int, optional
        Frames per second
    figsize : tuple, optional
        Figure size (width, height)
    title_template : str, optional
        Template for frame titles, use {time} placeholder
    """
    try:
        import matplotlib.animation as animation
    except ImportError:
        logger.error("matplotlib.animation not available. Install matplotlib for animation support.")
        return

    if 'time' not in time_series.dims:
        raise ValueError("Data must have 'time' dimension for animation")

    # Get time values
    times = time_series.time.values

    # Create figure
    fig = plt.figure(figsize=figsize)
    ax = plt.axes(projection=ccrs.PlateCarree())

    # Add static map features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.3)
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)

    # Determine value range for consistent colormap
    vmin = time_series.min().values
    vmax = time_series.max().values

    # Initial plot
    if 'lon' in time_series.dims and 'lat' in time_series.dims:
        im = ax.pcolormesh(time_series.lon, time_series.lat,
                          time_series.isel(time=0).values,
                          cmap='Blues', vmin=vmin, vmax=vmax,
                          transform=ccrs.PlateCarree())
    else:
        raise ValueError("Data must have lon/lat coordinates")

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.8)
    cbar.set_label('Wetland Fraction/Probability')

    # Add grid
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

    # Set initial title
    time_str = str(times[0])[:10]  # First 10 chars of time string
    title_text = ax.set_title(title_template.format(time=time_str),
                             fontsize=12, fontweight='bold')

    def update_frame(frame):
        """Update plot for each frame."""
        # Update data
        im.set_array(time_series.isel(time=frame).values.ravel())

        # Update title
        time_str = str(times[frame])[:10]
        title_text.set_text(title_template.format(time=time_str))

        return im, title_text

    # Create animation
    anim = animation.FuncAnimation(fig, update_frame, frames=len(times),
                                  interval=1000/fps, blit=True)

    # Save animation
    anim.save(output_path, writer='ffmpeg', fps=fps, dpi=150)
    logger.info(f"Animation saved to {output_path}")

    plt.close(fig)