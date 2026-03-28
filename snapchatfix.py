import os
import shutil
import subprocess
import re

# --- CONFIGURATION ---
SIMULATION = False  
TARGET_FOLDER = r"C:\PATH\TO\MEMORIES\FOLDER\NO\SPACE\IN\FOLDER\NAME"
FFMPEG_PATH = shutil.which("ffmpeg")
EXIFTOOL_PATH = shutil.which("exiftool")

MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}
YEARS = [str(y) for y in range(2010, 2030)]

def run_master_process():
    if not FFMPEG_PATH or not EXIFTOOL_PATH:
        print("ERROR: FFmpeg or ExifTool not found in PATH.")
        return
    
    print(f"--- Starting Master Process (Simulation: {SIMULATION}) ---")

    # --- STEP 1: PROCESS ALL MEDIA (FUSION OR STANDALONE) ---
    print("\n[Step 1/3] Processing Media & Fixing Metadata...")
    for root, dirs, files in os.walk(TARGET_FOLDER):
        file_set = set(files)

        for f in files:
            # Only look for the primary media files
            if "-main" not in f or "_FUSION" in f:
                continue
                
            base_name, ext_media = f.rsplit("-main", 1)
            media_f = f
            overlay_f = f"{base_name}-overlay.png"
            path_media = os.path.join(root, media_f)
            
            # Check if it's a video file (to handle specific video date fixes)
            is_video = ext_media.lower() in [".mp4", ".mov", ".webm"]

            # CASE A: OVERLAY EXISTS (FUSE THEN FIX)
            if overlay_f in file_set:
                path_overlay = os.path.join(root, overlay_f)
                final_path = os.path.join(root, f"{base_name}_FUSION{ext_media}")

                if SIMULATION:
                    print(f"   [+] Would Merge & Fix Dates: {media_f}")
                else:
                    filter_cmd = "[1:v][0:v]scale2ref[ovr][base];[base][ovr]overlay=0:0"
                    ffmpeg_cmd = [FFMPEG_PATH, "-y", "-i", path_media, "-i", path_overlay, "-filter_complex", filter_cmd, "-map_metadata", "0", "-c:a", "copy", final_path]
                    
                    try:
                        # 1. Merge the files
                        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                        
                        # 2. Fix Fusion Dates
                        exif_cmd = [
                            EXIFTOOL_PATH, 
                            "-TagsFromFile", path_media, 
                            "-time:all", 
                            "-FileModifyDate<FileCreateDate", 
                            "-FileCreateDate<FileCreateDate", 
                            "-overwrite_original", 
                            final_path
                        ]
                        subprocess.run(exif_cmd, check=True, capture_output=True)
                        
                        os.remove(path_overlay)
                        os.remove(path_media)
                        print(f"   [Merged & Dates Fixed] {base_name}")
                    except Exception as e:
                        print(f"   [!] Error merging {media_f}: {e}")

            # CASE B: NO OVERLAY (NON-FUSION)
            else:
                if is_video:
                    if SIMULATION:
                        print(f"   [*] Would Sync OS Dates for Video: {media_f}")
                    else:
                        try:
                            # Syncs the OS file dates strictly to the internal origin 'CreateDate'
                            exif_cmd = [
                                EXIFTOOL_PATH, 
                                "-FileModifyDate<CreateDate", 
                                "-FileCreateDate<CreateDate", 
                                "-overwrite_original", 
                                path_media
                            ]
                            subprocess.run(exif_cmd, check=True, capture_output=True)
                            print(f"   [Synced Video OS Dates] {media_f}")
                        except Exception as e:
                            print(f"   [!] Error fixing video {media_f}: {e}")
                else:
                    # Fix Date Modified for standalone images
                    if SIMULATION:
                        print(f"   [*] Would Sync OS Modify Date for Standalone Image: {media_f}")
                    else:
                        try:
                            exif_cmd = [
                                EXIFTOOL_PATH, 
                                "-FileModifyDate<FileCreateDate", 
                                "-overwrite_original", 
                                path_media
                            ]
                            subprocess.run(exif_cmd, check=True, capture_output=True)
                            print(f"   [Synced Image OS Modify Date] {media_f}")
                        except Exception as e:
                            print(f"   [!] Error fixing image {media_f}: {e}")

    # --- STEP 2: SORT EVERYTHING ---
    print("\n[Step 2/3] Sorting Files...")
    for root, dirs, files in os.walk(TARGET_FOLDER):
        for item in files:
            if item.endswith(".py"): continue
            
            date_match = re.search(r'^(\d{4})-(\d{2})', item)
            if date_match:
                year, month_digit = date_match.groups()
                if year in YEARS and month_digit in MONTHS:
                    dest_folder = os.path.join(TARGET_FOLDER, f"{MONTHS[month_digit]} {year}")
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.move(os.path.join(root, item), os.path.join(dest_folder, item))

    # --- STEP 3: RENAME ---
    print("\n[Step 3/3] Renaming Sorted Files...")
    for root, dirs, files in os.walk(TARGET_FOLDER):
        if root == TARGET_FOLDER: continue
        folder_name = os.path.basename(root)
        files_to_rename = sorted([f for f in files if not f.endswith(".py")])
        for idx, f in enumerate(files_to_rename):
            ext = os.path.splitext(f)[1]
            new_name = f"{folder_name}-{idx + 1}{ext}"
            os.rename(os.path.join(root, f), os.path.join(root, new_name))
        if files_to_rename: print(f"   [#] Completed: {folder_name}")

    print("\n--- Process Complete! ---")

if __name__ == "__main__":
    run_master_process()
