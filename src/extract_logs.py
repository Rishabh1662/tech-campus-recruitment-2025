#!/usr/bin/env python3
import os
import sys

DEBUG = True  # Set to False to disable debug prints

def debug_print(*args):
    if DEBUG:
        print("DEBUG:", *args)

def find_start_offset(f, target_date):
    """
    Use binary search to find the byte offset of the first log entry
    for the target date in a file assumed to be sorted chronologically.
    """
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    low, high = 0, file_size
    result_offset = None

    while low < high:
        mid = (low + high) // 2
        f.seek(mid)
        if mid != 0:
            # Skip a partial line
            f.readline()

        pos = f.tell()
        line = f.readline()
        if not line:
            high = mid
            continue
        try:
            # Strip any whitespace to avoid issues with trailing spaces/newlines
            line_date = line.decode('utf-8').strip()[:10]
        except UnicodeDecodeError:
            line_date = ""
        debug_print(f"Binary search: mid={mid}, pos={pos}, line_date='{line_date}'")
        if line_date < target_date:
            low = f.tell()
        else:
            high = mid
            result_offset = pos

    if result_offset is None:
        result_offset = low
    f.seek(result_offset)
    # Fine-tune: back up to ensure we capture the very first log entry for the target date
    while True:
        pos = f.tell()
        line = f.readline()
        if not line:
            break
        try:
            current_date = line.decode('utf-8').strip()[:10]
        except UnicodeDecodeError:
            current_date = ""
        debug_print(f"Fine-tuning: pos={pos}, current_date='{current_date}'")
        if current_date < target_date:
            result_offset = f.tell()
        else:
            # Go back one full line so that we include this entry
            f.seek(pos)
            break

    return f.tell()

def extract_logs(log_file_path, target_date, output_file_path):
    try:
        with open(log_file_path, 'rb') as f, open(output_file_path, 'wb') as out:
            start_offset = find_start_offset(f, target_date)
            debug_print(f"Start offset found: {start_offset}")
            f.seek(start_offset)
            line_count = 0
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    break
                try:
                    line_date = line.decode('utf-8').strip()[:10]
                except UnicodeDecodeError:
                    continue
                # Once the date no longer matches, we can break since logs are chronologically sorted.
                if line_date != target_date:
                    debug_print(f"Stopping at pos {pos}: found date '{line_date}' != target '{target_date}'")
                    break
                out.write(line)
                line_count += 1
            debug_print(f"Total lines written: {line_count}")
        print(f"Log entries for {target_date} written to {output_file_path}")
    except Exception as e:
        print(f"Error during log extraction: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_logs.py YYYY-MM-DD")
        sys.exit(1)
    
    target_date = sys.argv[1]
    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)
    output_file_path = f"output/output_{target_date}.txt"

    # Update this variable to the actual log file name
    log_file_path = "large_log_file.log"
    
    extract_logs(log_file_path, target_date, output_file_path)

if __name__ == "__main__":
    main()