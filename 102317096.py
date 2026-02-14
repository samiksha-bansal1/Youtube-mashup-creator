import sys
import os
import shutil
from pathlib import Path

# Check dependencies at startup
try:
    from pytubefix import YouTube, Search
except ImportError:
    print("\nERROR: pytubefix not installed")
    print("Run: pip install pytubefix\n")
    sys.exit(1)

try:
    from moviepy.editor import AudioFileClip, concatenate_audioclips
except ImportError:
    print("\nERROR: moviepy not installed properly")
    print("Run these commands:")
    print("  pip uninstall moviepy")
    print("  pip install moviepy")
    print("  pip install imageio-ffmpeg\n")
    sys.exit(1)


def validate_args():
    if len(sys.argv) != 5:
        print("\nUsage: python 102317096.py <singer> <count> <duration> <output.mp3>")
        print('Example: python 102317096.py "Arijit Singh" 15 30 output.mp3\n')
        sys.exit(1)
    
    singer = sys.argv[1].strip()
    cnt = sys.argv[2].strip()
    dur = sys.argv[3].strip()
    out = sys.argv[4].strip()
    
    if not singer:
        print("\nSinger name required\n")
        sys.exit(1)
    
    try:
        n = int(cnt)
        t = int(dur)
    except:
        print(f"\nNumbers required, got: {cnt}, {dur}\n")
        sys.exit(1)
    
    if n <= 10:
        print(f"\nNeed >10 videos (got {n})\n")
        sys.exit(1)
    
    if t <= 20:
        print(f"\nNeed >20 seconds (got {t})\n")
        sys.exit(1)
    
    return singer, n, t, out


def setup_folders():
    base = Path("temp_workspace")
    folders = {
        "vids": base / "downloads",
        "audio": base / "extracted",
        "cuts": base / "trimmed"
    }
    for f in folders.values():
        f.mkdir(parents=True, exist_ok=True)
    return base, folders


def download_videos(singer, count, folder):
    print(f"\n{'='*60}")
    print(f"Downloading {count} videos for '{singer}'")
    print(f"{'='*60}\n")
    
    downloaded = []
    
    try:
        search = Search(singer)
        
        for video in search.videos:
            if len(downloaded) >= count:
                break
            
            try:
                yt = YouTube(video.watch_url)
                stream = yt.streams.get_audio_only()
                
                if stream:
                    filepath = stream.download(
                        output_path=str(folder),
                        filename_prefix=f"vid_{len(downloaded)}_"
                    )
                    downloaded.append(filepath)
                    print(f"  [{len(downloaded)}/{count}] {yt.title[:45]}")
            except:
                continue
        
        if not downloaded:
            print("\nNo videos downloaded\n")
            sys.exit(1)
        
        print(f"\n{'='*60}")
        print(f"Downloaded: {len(downloaded)} videos")
        print(f"{'='*60}\n")
        
        return downloaded
        
    except Exception as e:
        print(f"\nDownload error: {str(e)}\n")
        sys.exit(1)


def to_audio(videos, folder):
    print("Extracting audio...")
    audio_files = []
    
    for i, vid in enumerate(videos):
        try:
            clip = AudioFileClip(vid)
            audio_path = folder / f"audio_{i}.mp3"
            clip.write_audiofile(str(audio_path), verbose=False, logger=None)
            clip.close()
            audio_files.append(str(audio_path))
            print(f"  [{i+1}/{len(videos)}] Extracted")
        except Exception as e:
            print(f"  [{i+1}/{len(videos)}] Failed: {str(e)[:30]}")
            continue
    
    if not audio_files:
        print("\nAudio extraction failed\n")
        sys.exit(1)
    
    print(f"Extracted {len(audio_files)} audio files\n")
    return audio_files


def trim_clips(audio_files, duration, folder):
    print(f"Trimming to {duration}s...")
    trimmed = []
    
    for i, audio in enumerate(audio_files):
        try:
            clip = AudioFileClip(audio)
            length = min(duration, clip.duration)
            cut = clip.subclip(0, length)
            cut_path = folder / f"cut_{i}.mp3"
            cut.write_audiofile(str(cut_path), verbose=False, logger=None)
            clip.close()
            cut.close()
            trimmed.append(str(cut_path))
            print(f"  [{i+1}/{len(audio_files)}] Trimmed")
        except Exception as e:
            print(f"  [{i+1}/{len(audio_files)}] Failed: {str(e)[:30]}")
            continue
    
    if not trimmed:
        print("\nTrimming failed\n")
        sys.exit(1)
    
    print(f"Trimmed {len(trimmed)} clips\n")
    return trimmed


def create_mashup(clips, output):
    print("Creating mashup...")
    
    try:
        audio_clips = [AudioFileClip(c) for c in clips]
        final = concatenate_audioclips(audio_clips)
        final.write_audiofile(output, verbose=False, logger=None)
        
        size = os.path.getsize(output) / (1024 * 1024)
        duration = final.duration
        
        for c in audio_clips:
            c.close()
        final.close()
        
        print(f"\n{'='*60}")
        print(f"SUCCESS!")
        print(f"{'='*60}")
        print(f"File: {output}")
        print(f"Size: {size:.1f} MB")
        print(f"Duration: {duration:.0f}s")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\nMashup creation failed: {str(e)}\n")
        sys.exit(1)


def cleanup(base):
    if base.exists():
        shutil.rmtree(base)
        print("Cleaned up temp files\n")


def main():
    print("\n" + "="*60)
    print("  YOUTUBE MASHUP CREATOR")
    print("="*60)
    
    singer, count, duration, output = validate_args()
    
    print(f"\nSettings:")
    print(f"  Singer: {singer}")
    print(f"  Videos: {count}")
    print(f"  Duration: {duration}s")
    print(f"  Output: {output}")
    
    base, folders = setup_folders()
    
    try:
        vids = download_videos(singer, count, folders["vids"])
        audio = to_audio(vids, folders["audio"])
        clips = trim_clips(audio, duration, folders["cuts"])
        create_mashup(clips, output)
        cleanup(base)
        print("Complete!\n")
    except KeyboardInterrupt:
        print("\n\nStopped by user\n")
        cleanup(base)
        sys.exit(1)


if __name__ == "__main__":
    main()