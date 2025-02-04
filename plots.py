#!/usr/bin/env python3
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
# for 3d bar plot
from mpl_toolkits.mplot3d.axes3d import Axes3D

# for num2date
import matplotlib.dates as mpl_dates

# for FuncFormatter
import matplotlib.ticker as ticker

import pandas as pd
from itertools import chain

def extract_dates(daily):
    return [pd.to_datetime(x[0], "%Y-%m-%d").date() for x in daily.items()]

def tou_stacked_plot(daily=None, plan=None):
    """
    Generates a stacked bar plot that shows the decomposed energy usage of each day.
    """
    dates = extract_dates(daily)

    daily_arrays = category_tally_by_plan(daily=daily, plan=plan)

    # plot the daily summary with stacked bars
    plt.figure()

    previous = np.zeros(len(dates))
    for index, category in enumerate(daily_arrays):
        # print(index, category, daily_arrays[category])
        plt.bar(dates, daily_arrays[category], label=category, color=f"C{index}", bottom=previous)
        previous += daily_arrays[category]

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

    plt.ylabel("Consumption (kWh)")
    plt.grid(linestyle="--", axis="y")
    plt.title("Daily Consumption")
    plt.legend()
    plt.tight_layout()
    plt.show()


def daily_net_usage_plot(daily=None):
    """
    Generates sum of energy usage for each day.
    """
    dates = extract_dates(daily)
    plt.figure()
    plt.title(f'Daily Net Usage: {dates[0].strftime("%Y/%m/%d")} to {dates[-1].strftime("%Y/%m/%d")}')
    daily_net_usage = [sum(consumption_data)[1] for date, consumption_data in daily.items()]

    plt.bar(dates, daily_net_usage)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.gcf().autofmt_xdate()
    plt.ylabel("Net Usage (kWh)")
    plt.savefig(f"plot_daily_net_usage_{dates[0].strftime('%Y%m%d')}_{dates[-1].strftime('%Y%m%d')}.png", dpi=300)


def aggregated_hourly_net_usage_plot(daily=None):
    """
    Generates aggregated usage by hour across all dates.
    """
    dates = extract_dates(daily)
    # plot the hourly summary
    plt.figure()
    plt.title(f'Aggregated Hourly Consumption: {dates[0].strftime("%Y/%m/%d")} to {dates[-1].strftime("%Y/%m/%d")}')
    # handles cases where readings from some hour may be missing
    aggregated_hourly = [sum(chain.from_iterable([[daily[x][k][1] for k in range(len(daily[x])) if daily[x][k][0] == i] for x in daily.index])) for i in range(24)]
    plt.bar(list(range(24)), aggregated_hourly)
    plt.ylabel("Net Usage (kWh)")
    plt.xlabel("Hour")
    plt.xlim([-0.5, 23.5])
    plt.savefig(f"plot_aggregated_hourly_net_usage_{dates[0].strftime('%Y%m%d')}_{dates[-1].strftime('%Y%m%d')}.png", dpi=300)


def daily_hourly_2d_plot(daily=None):
    """
    Generate plots for hourly energy usage for each day (one day each row).
    """
    if len(daily.index) >= 50:
        return
    dates = extract_dates(daily)
    fig, axs = plt.subplots(len(daily.index), 1, sharex=True)

    i = 0
    # series can use iteritems method
    for date, consumption_data in daily.items():
        # print(date, consumption_data)
        # daw plot for a particular day
        axs[i].bar(list(range(24)), consumption_data)
        axs[i].set_yticks([])
        i += 1
        # collect flattened data for 3d plot

    plt.xlim([-0.5, 23.5])

    """
    #add the common Y label before plt 3.4.0
    fig.add_subplot(111, frameon=False)
    #hide tick and tick label of the big axes
    plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
    plt.grid(False)
    plt.ylabel("consumption by day")
    """
    # add the common Y label after matplotlib 3.4.0
    fig.supylabel("Consumption by Day")
    fig.suptitle(f'Daily Details 2D: {dates[0].strftime("%Y/%m/%d")} to {dates[-1].strftime("%Y/%m/%d")}')
    plt.show()

def daily_hourly_3d_plot(daily=None):
    if len(daily.index) >= 50:
        return
    dates = extract_dates(daily)
    all_data = list(chain.from_iterable(daily))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    # 24 hours
    xvalues = np.array(list(range(24)))
    # the days, the trick here is to convert dates to number, for easier 3d plot involving dates
    yvalues = np.array([mpl_dates.date2num(d) for d in daily.index])
    # yvalues = np.array(list(range(len(daily.index))));
    xx, yy = np.meshgrid(xvalues, yvalues)

    xx = xx.flatten()
    yy = yy.flatten()

    # convert to np array
    all_data = np.array(all_data)
    zz = np.zeros_like(all_data)

    dx = np.ones_like(xx)
    dy = np.ones_like(yy)
    dz = all_data

    # colorcode the bars
    colors = plt.cm.jet(all_data / float(all_data.max()))

    ax.set_xlim([-0.5, 23.5])
    ax.set_ylim([min(yvalues), max(yvalues)])

    ax.set_xlabel("Hour")
    ax.set_zlabel("Consumption (kWh)")

    # ylabels=[a.strftime('%Y-%m-%d') for a in days ]

    ax.bar3d(xx, yy, zz, dx, dy, dz, color=colors)

    # The function should take in two inputs (a tick value x and a position pos), and return a string containing the corresponding tick label.
    num2formatted = lambda x, _: mpl_dates.num2date(x).strftime("%Y-%m-%d")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(num2formatted))

    # auto-adjust the orientation of labels
    # fig.autofmt_xdate()
    # manually set the orientation of labels
    ax.tick_params(axis="y", labelrotation=90)
    plt.title(f'Daily Details 3D: {dates[0].strftime("%Y/%m/%d")} to {dates[-1].strftime("%Y/%m/%d")}')
    plt.show()