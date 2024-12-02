#!/usr/bin/env python3
import argparse
import os
import sys

# Top-level docstring
"""
Memory Visualizer -- A program to visualize memory usage with bar charts.
Author: Kushal Parmar
Academic Honesty Declaration:
By submitting this code, I affirm that I have written this program myself and have not copied from any other source. I have also followed all rules and guidelines set by the course instructor.
"""

# Function to convert percentage to a graph bar
def percent_to_graph(percentage, bar_length=20):
    """
    Converts a memory usage percentage to a bar graph represented by '#' characters.
    
    Args:
        percentage (float): The percentage of memory usage (0.0 - 1.0).
        bar_length (int): The length of the bar (default is 20 characters).

    Returns:
        str: A string of '#' characters representing the usage and spaces for remaining memory.
    """
    filled_length = int(percentage * bar_length)
    bar = '#' * filled_length + ' ' * (bar_length - filled_length)
    return bar

# Function to get total system memory from /proc/meminfo
def get_sys_mem():
    """
    Reads /proc/meminfo to retrieve the total system memory in kilobytes.
    
    Returns:
        int: Total system memory in kilobytes.
    """
    with open('/proc/meminfo', 'r') as f:
        for line in f:
            if line.startswith("MemTotal"):
                total_mem = int(line.split()[1])  # In kilobytes
                return total_mem

# Function to get available memory from /proc/meminfo
def get_avail_mem():
    """
    Reads /proc/meminfo to retrieve available memory in kilobytes.
    If MemAvailable is missing (like in WSL), it sums MemFree and SwapFree.
    
    Returns:
        int: Available memory in kilobytes.
    """
    with open('/proc/meminfo', 'r') as f:
        mem_free = 0
        swap_free = 0
        mem_available = 0
        for line in f:
            if line.startswith("MemFree"):
                mem_free = int(line.split()[1])  # In kilobytes
            elif line.startswith("SwapFree"):
                swap_free = int(line.split()[1])  # In kilobytes
            elif line.startswith("MemAvailable"):
                mem_available = int(line.split()[1])  # In kilobytes
        
        # Fallback for WSL or missing MemAvailable
        if mem_available == 0:
            mem_available = mem_free + swap_free

        return mem_available

# Function to convert bytes to a human-readable format
def bytes_to_human_readable(bytes):
    """
    Converts bytes to a human-readable format (e.g., 1KiB, 1MiB).
    
    Args:
        bytes (int): The number of bytes.
        
    Returns:
        str: The memory size in a human-readable format.
    """
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0

# Function to parse command-line arguments
def parse_command_args():
    """
    Parses command-line arguments using argparse.
    
    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts")
    
    # Positional argument for program name
    parser.add_argument('program', nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    
    # Optional argument to display memory in human-readable format
    parser.add_argument('-H', '--human-readable', action='store_true', help="Prints sizes in human readable format")
    
    # Optional argument to set the length of the graph
    parser.add_argument('-l', '--length', type=int, default=20, help="Specify the length of the graph. Default is 20.")
    
    # Parse the arguments
    return parser.parse_args()

# Function to get process IDs for a program
def pids_of_prog(program):
    """
    Gets the process IDs (PIDs) of all instances of the specified program.
    
    Args:
        program (str): The name of the program to search for.
        
    Returns:
        list: A list of process IDs.
    """
    pids = []
    try:
        # Using pidof command to find PIDs of the program
        pid_list = os.popen(f"pidof {program}").read().strip()
        pids = pid_list.split() if pid_list else []
    except Exception as e:
        print(f"Error finding processes for {program}: {e}")
    return pids

# Function to get the RSS memory usage of a process
def rss_mem_of_pid(pid):
    """
    Reads the RSS memory usage for a given process ID.
    
    Args:
        pid (str): The process ID to check.
        
    Returns:
        int: The total RSS memory used by the process in kilobytes.
    """
    rss_total = 0
    try:
        # Reading the smaps file for the given PID
        with open(f"/proc/{pid}/smaps", "r") as f:
            for line in f:
                if line.startswith("Rss"):
                    rss_total += int(line.split()[1])  # Rss is in kilobytes
    except FileNotFoundError:
        print(f"Process {pid} not found.")
    return rss_total

# Main function to tie everything together
def main():
    args = parse_command_args()

    # Get the system memory details
    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    percent_used = used_mem / total_mem

    # If human-readable format is requested, convert values
    if args.human_readable:
        total_mem_hr = bytes_to_human_readable(total_mem * 1024)  # Convert from KiB to B for human-readable
        used_mem_hr = bytes_to_human_readable(used_mem * 1024)    # Same conversion
        avail_mem_hr = bytes_to_human_readable(avail_mem * 1024)
    else:
        total_mem_hr = f"{total_mem} KiB"
        used_mem_hr = f"{used_mem} KiB"
        avail_mem_hr = f"{avail_mem} KiB"

    # Print the memory usage graph
    bar_graph = percent_to_graph(percent_used, args.length)
    
    if args.program:
        # Show the memory usage of the program
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
            return

        total_prog_rss = 0
        for pid in pids:
            pid_rss = rss_mem_of_pid(pid)
            total_prog_rss += pid_rss

        # Ensure the total_prog_rss is in kilobytes for calculation
        total_prog_rss_kb = total_prog_rss

        # If human-readable format is requested, convert program's total memory usage
        if args.human_readable:
            total_prog_rss_hr = bytes_to_human_readable(total_prog_rss * 1024)  # Convert from KiB to B
        else:
            total_prog_rss_hr = f"{total_prog_rss} KiB"

        # Calculate the percentage used by the program in relation to total memory
        prog_percent_used = total_prog_rss_kb / total_mem

        # Print the program's memory usage with graph
        print(f"{args.program}        [{percent_to_graph(prog_percent_used, args.length)}] {total_prog_rss_hr}/{total_mem_hr}")

        for pid in pids:
            pid_rss = rss_mem_of_pid(pid)

            # If human-readable format is requested, convert PID's RSS memory usage
            if args.human_readable:
                pid_rss_hr = bytes_to_human_readable(pid_rss * 1024)
            else:
                pid_rss_hr = f"{pid_rss} KiB"

            # Calculate the percentage used by the PID in relation to total memory
            pid_percent_used = pid_rss / total_mem

            # Print each PID's memory usage with graph
            print(f"{pid}         [{percent_to_graph(pid_percent_used, args.length)}] {pid_rss_hr}/{total_mem_hr}")
    else:
        # Show the total memory usage
        print(f"Memory         [{bar_graph} | {percent_used * 100:.0f}%] {used_mem_hr}/{total_mem_hr}")

if __name__ == "__main__":
    main()
