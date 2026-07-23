#!/bin/python3
""" Helper tools to create plots from APES data.
Before using these functions to create plots, make sure to use the functions in gleaner.py
to calculate the statistical quantities, where the data is also stored in the database.

These functions were developed as a part of the Master Thesis done by Achuthan Rajendran,
master student at TU Dresden.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import logging
logging.basicConfig(level=logging.INFO)
import os
import sys
# Path to gleaner (Better use environment variable PYTHONPATH!)
glrPath = os.getenv('HOME') + '/apes/gleaner'
sys.path.append(glrPath)
import gleaner

def fft_velocities_plot(sqlcon, all_tab_names, percentage, frequency):
  """ (sqlite3.Connection, list of strings, float, int)
        Get column values from the tables 'all_tab_names' in the database connected by 'sqlcon'.

        The database should contain the data of fast fourier transforms calculated for the chosen
        'percentage' of samples and 'frequency'

        Creates the amplitude spectra of the data and stores in each folder
    """

  from pathlib import Path
  fft_col_head = ['Frequency', 'Amplitude_U', 'Amplitude_V', 'Amplitude_W']

  for name in all_tab_names:
    xf, my_list_u, my_list_v, my_list_w = gleaner.get_columns(sqlcon, tabname = f'{name}_FFT_uvw',
                                                              columns = fft_col_head)

    fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
    axs[0, 0].loglog(xf, my_list_u, color="r", label=r'Spectrum of $U$')
    axs[0, 0].set_ylabel(r'$U$-Amplitude [$\mathrm{m/s}$]')
    axs[0, 0].grid()
    axs[0, 0].legend()

    axs[0, 1].loglog(xf, my_list_v, color="g", label=r'Spectrum of $V$')
    axs[0, 1].set_ylabel(r'$V$-Amplitude [$\mathrm{m/s}$]')
    axs[0, 1].grid()
    axs[0, 1].legend()

    axs[1, 0].loglog(xf, my_list_w, color="b", label=r'Spectrum of $W$')
    axs[1, 0].set_xlabel(r'Frequency [Hz]')
    axs[1, 0].set_ylabel(r'$W$-Amplitude [$\mathrm{m/s}$]')
    axs[1, 0].grid()
    axs[1, 0].legend()

    axs[1, 1].loglog(xf, my_list_u, color="r", label=r'Spectrum of $U$')
    axs[1, 1].loglog(xf, my_list_v, color="g", label=r'Spectrum of $V$')
    axs[1, 1].loglog(xf, my_list_w, color="b", label=r'Spectrum of $W$')
    axs[1, 1].set_xlabel(r'Frequency [Hz]')
    axs[1, 1].set_ylabel(r'Amplitudes [$\mathrm{m/s}$]')
    axs[1, 1].grid()
    axs[1, 1].legend()

    fft_folder = f'{name}_FFT'
    if not os.path.exists(f'{fft_folder}'):
      os.makedirs(f'{fft_folder}')
      logging.info(f'{fft_folder} folder created')

    image_filename_write = f'{fft_folder}/{name}_FFT_Spectra_Merged_UVW.jpg'
    imagename_without_extension = Path(image_filename_write).stem
    plot_title = (f'{imagename_without_extension} for '
                  f'\n{percentage}% data and sampling frequency {frequency}')
    # imagename_without_extension = imagename_without_extension.replace('_p00000', '')
    fig.suptitle(plot_title, fontsize=10)
    plt.tight_layout()
    plt.savefig(image_filename_write, dpi=300)
    plt.close()

    col_header = ['U', 'V', 'W']
    colors = ["red", "green", "blue"]
    my_list = [my_list_u, my_list_v, my_list_w]

    for c_h, cl, m_l in zip(col_header, colors, my_list):
      image_filename_write = f'{fft_folder}/{name}_{c_h}_FFT_Spectra.jpg'
      imagename_without_extension = Path(image_filename_write).stem
      plot_title = (f'{imagename_without_extension} for '
                    f'\n{percentage}% data and sampling frequency {frequency}')

      plt.loglog(xf, m_l, color=cl, label=rf'Spectrum of ${c_h}$')
      plt.legend()
      plt.grid()
      plt.xlabel('Frequency [Hz]')
      plt.ylabel(rf'${c_h}$-Amplitude [m/s]')
      plt.suptitle(plot_title, fontsize=10)
      plt.savefig(image_filename_write, dpi=300)
      # plt.show()
      plt.close()
    logging.info(f'Plots are stored in the folder: {name}_FFT')
  logging.info('---------------------------------------------------------------------------------------------')


def cumulative_mean_var_plot(sqlcon, all_tab_names):
  """ (sqlite3.Connection, list of strings)
      Get column values from the tables 'all_tab_names' in the database connected by 'sqlcon'.

      The database should contain cumulative means and variances stored under each table names

      Creates the plots of cumulative means and variances and stores in each folder
  """

  col_head = ['velocity_phy_01', 'velocity_phy_02', 'velocity_phy_03']
  cum_col_head = ['time', 'Mean_U', 'Mean_V', 'Mean_W', 'Variance_U', 'Variance_V', 'Variance_W']
  all_data_folders = []
  for table in all_tab_names:
    cum_table = f'{table}_cumulative_mean_var'
    [t, run_mean_U, run_mean_V, run_mean_W, u_var, v_var, w_var] = gleaner.get_columns(sqlcon, tabname=cum_table,
                                                                               columns=cum_col_head)
    [u, v, w] = gleaner.get_columns(sqlcon, tabname=table, columns=col_head)

    data_folder_ind = f"Cumu_{table}"
    if not os.path.exists(f'{data_folder_ind}'):
      os.makedirs(f'{data_folder_ind}')
      logging.info(f'\n{data_folder_ind} folder created')

    all_data_folders.append(data_folder_ind)

    fig, ax = plt.subplots()
    ax.plot(t, u, color="tab:blue", label=f'Inst. velocity-$U$')
    ax.plot(t, run_mean_U, color="r", label=r'Mean velocity-$\overline{U}$')
    ax.legend()
    ax.set_xlabel('Time [s]')
    ax.set_ylabel(r'$U, \overline{U}$ [m/s]')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
    ax.grid(axis='x')
    # plt.show()
    fig.savefig(f"{data_folder_ind}/U_inst_u_mean_comparison_plot.jpg", dpi=300)
    plt.clf()
    plt.close()

    all_vel = [u, v, w]
    all_mean = [run_mean_U, run_mean_V, run_mean_W]
    all_var = [u_var, v_var, w_var]

    inst_dir = ['U', 'V', 'W']
    mean_dir = [r"$\overline{U}$", r"$\overline{V}$", r"$\overline{W}$"]
    var_dir = [r"$\overline{{u'}^2}$", r"$\overline{{v'}^2}$", r"$\overline{{w'}^2}$"]

    for inst, mean, var, i_dir, m_dir, v_dir in zip(all_vel, all_mean, all_var, inst_dir, mean_dir, var_dir):
      fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
      ax1.plot(t, inst, color="tab:blue", linewidth=1)
      ax1.set_xlabel('Time [s]')
      ax1.set_ylabel(rf'Inst. velocity-${i_dir}$ [m/s]')
      ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax1.grid(axis='x')
      ylim_inst = ax1.get_ylim()
      color = 'tab:red'
      ax2.plot(t, mean, color=color)
      ax2.set_xlabel('Time [s]')

      ax2.set_ylabel(f'Mean velocity-{m_dir} [m/s]', color=color)
      ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax2.grid(axis='x')
      ax2.tick_params(axis='y', labelcolor=color)
      ax2.set_ylim(ylim_inst)

      ax3 = ax2.twinx()  # instantiating a second Axes that shares the same x-axis
      color = 'tab:green'
      ax3.set_ylabel(f"Variance-{v_dir} [$m^2/s^2$]", color=color)  # we already handled the x-label with ax1
      ax3.plot(t, var, color=color)
      # ax2.set_ylim(0, 0.03)
      ax3.tick_params(axis='y', labelcolor=color)
      fig2.savefig(f"{data_folder_ind}/{table}_{i_dir}.jpg", dpi=300)
      plt.close(fig2)
    logging.info(f'Plots are stored in the folder: Cumu_{table}')
  logging.info('---------------------------------------------------------------------------------------------')


def simple_moving_avg_var_plot(sqlcon, all_tab_names):
  """ (sqlite3.Connection, list of strings)
      Get column values from the tables 'all_tab_names' in the database connected by 'sqlcon'.
`
      The database also contains simple moving means and variances stored under each table names

      Creates the plots of simple moving means and variances and stores in each folder
  """

  moving_col_head = ['time_red', 'Mean_U', 'Mean_V', 'Mean_W', 'Variance_U', 'Variance_V', 'Variance_W']
  col_head = ['time', 'velocity_phy_01', 'velocity_phy_02', 'velocity_phy_03']
  all_data_folders = []
  for table in all_tab_names:
    moving_table = f'{table}_simple_moving_mean_var'
    [t_red, u_mean, v_mean, w_mean, u_var, v_var, w_var] = gleaner.get_columns(sqlcon, tabname=moving_table,
                                                                               columns=moving_col_head)
    [t, u, v, w] = gleaner.get_columns(sqlcon, tabname=table, columns=col_head)

    data_folder_ind = f"Sma_{table}"
    if not os.path.exists(f'{data_folder_ind}'):
      os.makedirs(f'{data_folder_ind}')
      logging.info(f'\n{data_folder_ind} folder created')

    all_data_folders.append(data_folder_ind)

    fig, ax = plt.subplots()
    ax.plot(t, u, color="tab:blue", label=r'Inst. velocity-$U$')
    ax.plot(t_red, u_mean, color="r", label=r'Mean velocity-$\overline{U}$')
    ax.legend()
    ax.set_xlabel('Time [s]')
    ax.set_ylabel(r'$U$, $\overline{U}$ [m/s]')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
    ax.grid(axis='x')
    fig.savefig(f"{data_folder_ind}/U_inst_u_mean_comparison_plot.jpg", dpi=300)
    plt.close(fig)

    all_vel = [u, v, w]
    all_mean = [u_mean, v_mean, w_mean]
    all_var = [u_var, v_var, w_var]
    inst_dir = ['U', 'V', 'W']
    mean_dir = [r"$\overline{U}$", r"$\overline{V}$", r"$\overline{W}$"]
    var_dir = [r"$\overline{{u'}^2}$", r"$\overline{{v'}^2}$", r"$\overline{{w'}^2}$"]

    for inst, mean, var, i_dir, m_dir, v_dir in zip(all_vel, all_mean, all_var, inst_dir, mean_dir, var_dir):
      fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
      ax1.plot(t, inst, color="tab:blue", linewidth=1)
      ax1.set_xlabel('Time [s]')
      ax1.set_ylabel(rf'Inst. velocity-${i_dir}$ [m/s]')
      ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax1.grid(axis='x')
      ylim_inst = ax1.get_ylim()
      xlim_inst = ax1.get_xlim()

      color = 'tab:red'
      ax2.plot(t_red, mean, color=color)
      ax2.set_xlabel('Time [s]')
      ax2.set_ylabel(f'Mean velocity-{m_dir} (m/s)', color=color)
      ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax2.grid(axis='x')
      ax2.tick_params(axis='y', labelcolor=color)
      ax2.set_xlim(xlim_inst)
      ax2.set_ylim(ylim_inst)

      ax3 = ax2.twinx()  # instantiating a second Axes that shares the same x-axis
      color = 'tab:green'
      ax3.set_ylabel(f"Variance-{v_dir} [$m^2/s^2$]", color=color)  # we already handled the x-label with ax1
      ax3.plot(t_red, var, color=color)
      ax3.set_ylim(min(var) * 0.005, max(var) * 3) ### set ylim as per your need ##
      ax3.tick_params(axis='y', labelcolor=color)
      fig2.savefig(f"{data_folder_ind}/{table}_{i_dir}.jpg", dpi=300)
      plt.close(fig2)
    logging.info(f'Plots are stored in the folder: Sma_{table}')
  logging.info('---------------------------------------------------------------------------------------------')


def fourier_mean_var_plot(sqlcon, all_tab_names):
  """ (sqlite3.Connection, list of strings)
      Get column values from the tables 'all_tab_names' in the database connected by 'sqlcon'.
`
      The database also contains fourier means and variances stored under each table names

      Creates the plots of fourier means and variances and stores in each folder
  """

  fourier_col_head = ['time', 'Mean_U', 'Mean_V', 'Mean_W', 'Variance_U', 'Variance_V', 'Variance_W']
  col_head = ['velocity_phy_01', 'velocity_phy_02', 'velocity_phy_03']
  all_data_folders = []
  for table in all_tab_names:
    fourier_table = f'{table}_fourier_mean_var'
    [t, U_avg, V_avg, W_avg, u_var, v_var, w_var] = gleaner.get_columns(sqlcon, tabname=fourier_table,
                                                                       columns=fourier_col_head)
    [u, v, w] = gleaner.get_columns(sqlcon, tabname=table, columns=col_head)

    fig, ax = plt.subplots()
    ax.plot(t, u, color="b", label=r'Inst. Velocity-$U$')
    ax.plot(t, U_avg, color="r", label=r'Mean Velocity-$\overline{U}$')
    ax.legend()
    ax.set_xlabel('Time [s]')
    ax.set_ylabel(r'$U$, $\overline{U}$ [m/s]')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
    ax.grid(axis='x')

    data_folder_ind = f"Fourier_{table}"
    if not os.path.exists(f'{data_folder_ind}'):
      os.makedirs(f'{data_folder_ind}')
      logging.info(f'\n{data_folder_ind} folder created')

    all_data_folders.append(data_folder_ind)

    fig.savefig(f"{data_folder_ind}/U_inst_u_mean_comparison_plot.jpg", dpi=300)
    plt.close(fig)

    all_vel = [u, v, w]
    all_mean = [U_avg, V_avg, W_avg]
    all_var = [u_var, v_var, w_var]
    inst_dir = ['U', 'V', 'W']
    mean_dir = [r"$\overline{U}$", r"$\overline{V}$", r"$\overline{W}$"]
    var_dir = [r"$\overline{{u'}^2}$", r"$\overline{{v'}^2}$", r"$\overline{{w'}^2}$"]

    for inst, mean, var, i_dir, m_dir, v_dir in zip(all_vel, all_mean, all_var, inst_dir, mean_dir, var_dir):
      fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
      ax1.plot(t, inst, color="tab:blue", linewidth=1)
      ax1.set_xlabel('Time [s]')
      ax1.set_ylabel(f'Inst. Velocity-{i_dir}')
      ax1.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax1.grid(axis='x')
      ylim_inst = ax1.get_ylim()
      xlim_inst = ax1.get_xlim()
      color = 'tab:red'

      ax2.plot(t, mean, color=color)
      ax2.set_xlabel('Time [s]')
      ax2.set_ylabel(f'Mean velocity-{m_dir} (m/s)', color=color)
      ax2.xaxis.set_major_locator(ticker.MaxNLocator(nbins=7))
      ax2.grid(axis='x')
      ax2.tick_params(axis='y', labelcolor=color)
      ax2.set_xlim(xlim_inst)
      ax2.set_ylim(ylim_inst)

      ax3 = ax2.twinx()  # instantiating a second Axes that shares the same x-axis
      color = 'tab:green'
      ax3.set_ylabel(f"Variance-{v_dir} [$m^2/s^2$]", color=color)
      ax3.plot(t, var, color=color)
      ax3.set_ylim(min(var) * 0.005, max(var) * 3) ## you can change or remove the ylim as your wish ##
      # ax2.set_ylim(0, 0.03)
      ax3.tick_params(axis='y', labelcolor=color)
      fig2.savefig(f"{data_folder_ind}/{table}_{i_dir}.jpg", dpi=300)
      plt.close(fig2)
    logging.info(f'Plots are stored in the folder: Fourier_{table}')
  logging.info('----------------------------------------------------------------------------------------------')


