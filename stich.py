import os
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
TARGET_FOLDER = r"C:\PATH\TO\MEMORIES\FOLDER\NO\SPACE\IN\FOLDER\NAME"
FFMPEG_PATH = "ffmpeg" # Assuming it's in your PATH
EXIFTOOL_PATH = "exiftool" # Assuming it's in your PATH

# The maximum seconds between the start of one video and the start of the next to be considered a "split"
# If a video is 10s long, the next one should start ~10-11 seconds later.
TIME_THRESHOLD_SECONDS = 12 

def get_video_files_with_times(folder):
    """Gets all mp4s and their OS creation times, sorted chronologically."""
    videos = []
    for f in os.listdir(folder):
        if f.lower().endswith((".mp4", ".mov")):
            full_path = os.path.join(folder, f)
            # Getting the OS creation time (Make sure your OS dates are relatively accurate first!)
            ctime = os.path.getmtime(full_path) 
            videos.append({"path": full_path, "name": f, "time": ctime})
    
    # Sort by time
    return sorted(videos, key=lambda x: x["time"])

def stitch_snapchat_videos():
    videos = get_video_files_with_times(TARGET_FOLDER)
    if not videos:
        print("No videos found.")
        return

    groups = []
    current_group = [videos[0]]

    # Group videos that are close in time
    for i in range(1, len(videos)):
        prev_vid = current_group[-1]
        curr_vid = videos[i]
        
        time_diff = curr_vid["time"] - prev_vid["time"]
        
        # If the next video was created within ~12 seconds of the previous one
        if 0 < time_diff <= TIME_THRESHOLD_SECONDS:
            current_group.append(curr_vid)
        else:
            groups.append(current_group)
            current_group = [curr_vid]
            
    groups.append(current_group) # Add the last group

    # Process the groups
    for idx, group in enumerate(groups):
        if len(group) > 1:
            print(f"\n[+] Found a split video sequence ({len(group)} parts):")
            for v in group:
                print(f"    - {v['name']}")
                
            # Create the text file for FFmpeg
            list_file_path = os.path.join(TARGET_FOLDER, f"concat_list_{idx}.txt")
            with open(list_file_path, "w") as f:
                for v in group:
                    # FFmpeg requires safe paths in the text file
                    safe_path = v['path'].replace('\\', '/')
                    f.write(f"file '{safe_path}'\n")

            # Define output name based on the first video in the sequence
            base_name = os.path.splitext(group[0]['name'])[0]
            output_path = os.path.join(TARGET_FOLDER, f"{base_name}_STITCHED.mp4")
            first_video_path = group[0]['path']

            # Run FFmpeg
            ffmpeg_cmd = [
                FFMPEG_PATH, "-y", "-f", "concat", "-safe", "0", 
                "-i", list_file_path, "-c", "copy", output_path
            ]
            
            try:
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
                print(f"   [SUCCESS] Stitched into: {os.path.basename(output_path)}")
                

                print("   [*] Restoring original OS and metadata dates...")
                exiftool_cmd = [
                    EXIFTOOL_PATH, 
                    "-TagsFromFile", first_video_path,
                    "-CreateDate", "-ModifyDate", 
                    "-FileCreateDate<FileCreateDate", 
                    "-FileModifyDate<FileModifyDate", 
                    output_path,
                    "-overwrite_original_in_place" # <-- FIX: Prevents Windows from generating a new "Date Modified"
                ]
                
                subprocess.run(exiftool_cmd, check=True, capture_output=True)
                print("   [SUCCESS] Dates restored successfully.")
                
                subprocess.run(exiftool_cmd, check=True, capture_output=True)
                print("   [SUCCESS] Dates restored successfully.")
                
                # Cleanup: Delete the list file and the original split parts
                os.remove(list_file_path)
                for v in group:
                    os.remove(v['path'])
                    
            except subprocess.CalledProcessError as e:
                # This will catch errors from either FFmpeg or Exiftool
                print(f"   [!] Error during processing: {e}")
                if e.stderr:
                    print(f"   [!] Details: {e.stderr.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"   [!] Unexpected error: {e}")

if __name__ == "__main__":
    print("--- Starting Video Stitcher ---")
    stitch_snapchat_videos()
    print("--- Done ---")
