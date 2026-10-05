# 1.1.12: RB label above the music-sheet icon

The compact Ocarina play overlay now draws RB centered above the native q61 music-sheet icon. The label follows that icon's materialized bounds and existing compact transform. It leaves the red music-sheet artwork visible and is hidden on the expanded song page. Inputs and the 1.1.11 frontend backdrop/fade changes are unchanged.

Validation: ARM Ocarina composition tests verify horizontal centering, clearance above the icon, and hiding on the song page; existing X/Y, Quit, cursor and song-title checks pass. Host build/IPS checks pass. This label change has not been visually verified in Azahar.

Install the complete release's load/mods/0004000000033500 folder, replacing the previous title mod contents. Open the Ocarina: RB should appear above the music-sheet icon. Press RB to open the song sheet and verify no stray RB remains on that page.
