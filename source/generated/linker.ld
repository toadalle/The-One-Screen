OUTPUT_FORMAT("elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(tos_before)
SECTIONS {
 .patch_motion_disable 0x2ded60 : { KEEP(*(.patch_motion_disable)) }
 .patch_frontend_exact_queued_draw 0x2feaa4 : { KEEP(*(.patch_frontend_exact_queued_draw)) }
 .patch_movie 0x300518 : { KEEP(*(.patch_movie)) }
 .patch_target 0x300588 : { KEEP(*(.patch_target)) }
 .patch_submit_top 0x41952c : { KEEP(*(.patch_submit_top)) }
 .patch_submit_right 0x4197dc : { KEEP(*(.patch_submit_right)) }
 .patch_file_select_backdrop 0x419820 : { KEEP(*(.patch_file_select_backdrop)) }
 .patch_lower_fade 0x419868 : { KEEP(*(.patch_lower_fade)) }
 .patch_submit_bottom 0x4198b0 : { KEEP(*(.patch_submit_bottom)) }
 .patch_note 0x41a904 : { KEEP(*(.patch_note)) }
 .patch_action 0x41e250 : { KEEP(*(.patch_action)) }
 .patch_hud_submit 0x41eabc : { KEEP(*(.patch_hud_submit)) }
 .patch_minimap 0x41eb04 : { KEEP(*(.patch_minimap)) }
 .patch_common_backdrop 0x41ee2c : { KEEP(*(.patch_common_backdrop)) }
 .patch_ocarina_native_draw 0x41ee74 : { KEEP(*(.patch_ocarina_native_draw)) }
 .patch_hid_pointer 0x423340 : { KEEP(*(.patch_hid_pointer)) }
 .patch_touch 0x428a4c : { KEEP(*(.patch_touch)) }
 .patch_map_markers 0x42b85c : { KEEP(*(.patch_map_markers)) }
 .patch_motion_gate_a 0x42bca8 : { KEEP(*(.patch_motion_gate_a)) }
 .patch_draw_a 0x42bcc4 : { KEEP(*(.patch_draw_a)) }
 .patch_motion_gate_b 0x42be48 : { KEEP(*(.patch_motion_gate_b)) }
 .patch_draw_b 0x42be64 : { KEEP(*(.patch_draw_b)) }
 .patch_pause 0x42ec04 : { KEEP(*(.patch_pause)) }
 .patch_keyboard 0x43dd18 : { KEEP(*(.patch_keyboard)) }
 .patch_mode_backdrop_dual 0x43fe30 : { KEEP(*(.patch_mode_backdrop_dual)) }
 .patch_mode_backdrop_single 0x44015c : { KEEP(*(.patch_mode_backdrop_single)) }
 .patch_file_primary 0x450878 : { KEEP(*(.patch_file_primary)) }
 .patch_file_accent 0x450ad4 : { KEEP(*(.patch_file_accent)) }
 .patch_file_modal 0x45135c : { KEEP(*(.patch_file_modal)) }
 .patch_file_aux 0x452108 : { KEEP(*(.patch_file_aux)) }
 .patch_before 0x452390 : { KEEP(*(.patch_before)) }
 .patch_after 0x452434 : { KEEP(*(.patch_after)) }
 .patch_file_fade_producer_a 0x45ce68 : { KEEP(*(.patch_file_fade_producer_a)) }
 .patch_file_fade_producer_b 0x45db7c : { KEEP(*(.patch_file_fade_producer_b)) }
 .patch_file_fade_producer_c 0x45f754 : { KEEP(*(.patch_file_fade_producer_c)) }
 .patch_file_fade_producer_d 0x45fab8 : { KEEP(*(.patch_file_fade_producer_d)) }
 .patch_heart_positions 0x4695f0 : { KEEP(*(.patch_heart_positions)) }
 .patch_heart_indices 0x4695f8 : { KEEP(*(.patch_heart_indices)) }
 .patch_heart_texture 0x469628 : { KEEP(*(.patch_heart_texture)) }
 .patch_shard_overlay 0x469b48 : { KEEP(*(.patch_shard_overlay)) }
 .patch_vision_transition_a 0x4848d0 : { KEEP(*(.patch_vision_transition_a)) }
 .patch_vision_transition_b 0x484924 : { KEEP(*(.patch_vision_transition_b)) }
 .patch_vision_transition_c 0x484990 : { KEEP(*(.patch_vision_transition_c)) }
 .patch_target_note 0x494e10 : { KEEP(*(.patch_target_note)) }
 .patch_heart_descriptor 0x4d30a4 : { KEEP(*(.patch_heart_descriptor)) }
 .patch_shard_positions 0x4d31bc : { KEEP(*(.patch_shard_positions)) }
 . = 0x00610000;
 .payload : { *(.text*) *(.rodata*) *(.data*) }
 .zero : { *(.bss*) *(COMMON) }
 /DISCARD/ : { *(.comment*) *(.note*) *(.ARM.exidx*) *(.ARM.extab*) *(.eh_frame*) }
}
