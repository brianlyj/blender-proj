CLASSROOM + MARI SPORTS CHARACTER
================================

PROJECT GUIDE WITH PICTURES AND VIDEOS
Open ../README.md for animated previews, MP4 links, the current emote
gallery, installation steps, and the full numpad control table.

START HERE: DANCE + NUMPAD EMOTES
Open deliverables/Classroom-emotes.blend for nine emotes based on the supplied
reference reel plus both versions of the dance. Numpad + plays the refined
2 Phut Hon dance; Numpad - plays the original dance. Numpad 1-9 switches
emotes, 0 returns to idle, Enter pauses, and Numpad . toggles the shortcuts.
Transitions ease between poses. See deliverables/EMOTE-CONTROLS.txt.
The companion controller is installed and enabled in Blender on this PC.
Motion previews: deliverables/Classroom-dance-fluid-10s.mp4 and
deliverables/Emote-paws-fluid-6s.mp4 (silent, 24 fps).

ORIGINAL DANCE (PRESERVED)
Open deliverables/Classroom-dance.blend in Blender 5.2.
Press Space to play the 10-second animation (frames 1-240 at 24 fps).
The active camera shows the full character near the teacher's area.
Select "MARI | refined character rig" and enter Pose Mode to adjust the rig.

Watch deliverables/Classroom-dance-10s.mp4 for the rendered animation.
This is a silent, 2 Phut Hon inspired dance; no music is included.
Final stills are in deliverables/previews/.
Attribution and license details are in deliverables/ASSET-CREDIT.txt.

FOLDERS
deliverables/  Latest Blender scene, final video, previews and asset credit.
references/    Supplied GLB, reference inspection scene, original sports-outfit
               image, reference render and extracted textures.
scripts/       Python scripts grouped into initial, refinement, animation,
               render, diagnostics, shared and maintenance.
renders/       All 240 dance frames and both earlier 60-frame greeting renders.
reports/       Final checks, diagnostic data and the file-move manifest.
archive/       Earlier scenes and previews, checkpoints, Blender backups,
               and a ZIP containing the scripts before their paths were updated.

WORKING WITH THE SCRIPTS
All project paths resolve relative to the classroom folder. Keep the folder
structure together when copying the project to another drive or computer.
scripts/shared/project_paths.py and path-map.json route historical filenames
to their organized locations, including dynamically generated render names.

To render the final dance again, run Blender in background mode with:
  blender --background deliverables/Classroom-dance.blend --python scripts/render/render_dance_final.py
Run this command from the classroom folder. It regenerates the final stills
and PNG frames in renders/dance_frames/. The existing MP4 is retained.

To encode those frames into a new video with FFmpeg:
  ffmpeg -framerate 24 -i renders/dance_frames/frame_%03d.png -c:v libx264 -pix_fmt yuv420p -movflags +faststart deliverables/Classroom-dance-new.mp4

To check the final scene without changing it:
  blender --background deliverables/Classroom-dance.blend --python scripts/diagnostics/verify_organized_project.py

For a running Blender with its MCP server enabled, the existing MCP Python
environment can run scripts/shared/blender_bridge.py SCRIPT_PATH.
The bridge now supplies __file__ so scripts resolve this project's paths.

The build, refinement, animation and some diagnostic scripts are historical
editing steps. They can change or save the scene; do not batch-run them on
the final scene. Use a working copy when revisiting an earlier step.

ORGANIZATION RECORD
No earlier versions, backups or rendered frames were discarded.
reports/organization-manifest.json records every original and organized path
with SHA-256 checksums. All files were verified after moving; only script
paths were updated during the initial move.
The Blender MCP addon and server files in the parent folder remain in place.
