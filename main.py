import os
import random
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import json


def run_main():
    with open('countries.json', 'r') as f:
        data = json.load(f)

    terrorism = data['terrorism']
    natural_disasters = data['natural_disasters']
    war = data['war']
    anti_government_clashes = data['anti_government_clashes']
    ethnic_conflicts = data['ethnic_conflicts']
    frozen_conflicts = data['frozen_conflicts']

    def cycle_lists(*lists):
        while True:
            for lst in lists:
                yield lst

    texts = {
        "ethnic_conflicts": "ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS ETHNIC CONFLICTS",
        "anti_government_clashes": "ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ANTI-GOVERNMENT CLASHES ",
        "war": "WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR WAR",
        "natural_disasters": "NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS NATURAL DISASTERS",
        "frozen_conflicts": "FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS FROZEN CONFLICTS",
        "terrorism": "TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM TERRORISM"
    }

    def generate_colors(main_color, second_color):
        colormap = mcolors.LinearSegmentedColormap.from_list("main_to_second", [mcolors.to_rgba(main_color),
                                                                                mcolors.to_rgba(second_color)])
        colors_forward = [colormap(x) for x in np.linspace(0, 1, num_frames)]
        colors_backward = colors_forward[::-1]
        return colors_forward + colors_backward

    category_colors = {
        'ethnic_conflicts': ('#8D0A9B', '#c319d1'),  # violet
        'anti_government_clashes': ('#325939', '#5f976a'),  # green
        'war': ('#C51F19', '#f13329'),  # red
        'natural_disasters': ('#702716', '#BA4930'),  # brown
        'frozen_conflicts': ('#083A75', '#165bab'),  # blue
        'terrorism': ('#8E0C15', '#bf1926')  # dark red
    }

    num_frames = 3
    colors_dict = {key: generate_colors(color1, color2) for key, (color1, color2) in category_colors.items()}
    category_duration_seconds = 2
    frames_per_second = 15
    frames_per_category = category_duration_seconds * frames_per_second

    def update_color(num, country_shapes, target_countries_container, time_shifts_dict, colors_dict):
        if update_color.current_frame == frames_per_category:
            update_color.current_frame = 0
            target_countries_container[0] = next(country_lists)
        update_color.current_frame += 1
        target_countries = target_countries_container[0]
        time_shifts = time_shifts_dict[tuple(target_countries)]
        category_name = [key for key, value in zip(category_colors.keys(),
                                                   [ethnic_conflicts, anti_government_clashes, war, natural_disasters,
                                                    frozen_conflicts, terrorism]) if value == target_countries][0]
        colors = colors_dict[category_name]
        ax.clear()
        ax.add_feature(cfeature.LAND, facecolor='#D2D3D5')
        ax.add_feature(cfeature.RIVERS, linewidth=0, edgecolor='none')
        ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

        total_frames = len(colors)
        for shape in country_shapes:
            country_name = shape.attributes['ADMIN']
            if country_name in target_countries:
                idx = target_countries.index(country_name)
                shifted_frame = (num + time_shifts[idx]) % total_frames
                ax.add_geometries([shape.geometry], ccrs.PlateCarree(), facecolor=colors[shifted_frame],
                                  edgecolor='white',
                                  linewidth=0.5)
            else:
                ax.add_geometries([shape.geometry], ccrs.PlateCarree(), facecolor=facecolor, edgecolor='white',
                                  linewidth=0.5)

        text_key = [key for key, value in zip(category_colors.keys(),
                                              [ethnic_conflicts, anti_government_clashes, war, natural_disasters,
                                               frozen_conflicts, terrorism]) if value == target_countries][0]
        text = texts[text_key]
        text_color = category_colors[text_key][0]  # Get the first color from the category_colors dictionary

        # First scrolling text
        text_position_x1 = 1.2 - (update_color.current_frame / frames_per_category) * 1.2
        text_position_y1 = 0.001
        ax.text(text_position_x1, text_position_y1, text, transform=ax.transAxes, fontsize=16, fontweight='bold',
                fontstyle='italic', color=text_color, horizontalalignment='center', verticalalignment='center',
                bbox=dict(facecolor='none', edgecolor='none', pad=5, alpha=0.7))

        # Second scrolling text (a bit higher and in the opposite direction)
        text_position_x2 = (update_color.current_frame / frames_per_category) * -1.2
        text_position_y2 = 0.99
        doubled_text = text + "   " + text
        ax.text(text_position_x2, text_position_y2, doubled_text, transform=ax.transAxes, fontsize=16,
                fontweight='bold',
                fontstyle='italic', color=text_color, horizontalalignment='center', verticalalignment='center',
                bbox=dict(facecolor='none', edgecolor='none', pad=5, alpha=0.7))

        return []

    # Set the edge color of the axes to white
    plt.rcParams['axes.edgecolor'] = 'white'
    # Create a matplotlib figure and axis for displaying the text
    fig, ax = plt.subplots(figsize=(12, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.add_feature(cfeature.LAND, facecolor='#D2D3D5')
    ax.add_feature(cfeature.RIVERS, linewidth=0, edgecolor='none')
    ax.set_extent([-180, 180, -60, 90], crs=ccrs.PlateCarree())

    script_dir = os.path.dirname(os.path.abspath(__file__))
    shpfilename = os.path.join(script_dir, 'map', 'ne_110m_admin_0_countries.shp')

    country_shapes = list(shpreader.Reader(shpfilename).records())

    facecolor = '#D2D3D5'
    for shape in country_shapes:
        inactive_color = '#D2D3D5'
        ax.add_geometries([shape.geometry], ccrs.PlateCarree(), facecolor=inactive_color)

    country_lists = cycle_lists(ethnic_conflicts, anti_government_clashes, war, natural_disasters, frozen_conflicts,
                                terrorism)
    target_countries_container = [next(country_lists)]

    time_shifts_dict = {tuple(lst): [random.randint(0, 2 * num_frames - 1) for _ in lst] for lst in
                        [ethnic_conflicts, anti_government_clashes, war, natural_disasters, frozen_conflicts,
                         terrorism]}

    total_duration_seconds = 6 * category_duration_seconds

    update_color.current_frame = 0

    ani = animation.FuncAnimation(
        fig, update_color, frames=total_duration_seconds * frames_per_second,
        fargs=(country_shapes, target_countries_container, time_shifts_dict, colors_dict),
        interval=1000 / frames_per_second, blit=True
    )
    plt.show()

def main():
    run_main()

if __name__ == "__main__":
    main()



