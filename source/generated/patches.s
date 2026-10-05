.syntax unified
.arm
.section .patch_motion_disable,"ax",%progbits
bx lr
.section .patch_frontend_exact_queued_draw,"ax",%progbits
bl Presentation_DrawQueued
.section .patch_movie,"ax",%progbits
blne tos_movie
.section .patch_target,"ax",%progbits
ldr pc, [pc, #-4]
.word Presentation_Target
.section .patch_submit_top,"ax",%progbits
bl Presentation_Submit
.section .patch_submit_right,"ax",%progbits
bl Presentation_Submit
.section .patch_file_select_backdrop,"ax",%progbits
bl tos_file_select_backdrop
.section .patch_lower_fade,"ax",%progbits
bl Presentation_LowerFade
.section .patch_submit_bottom,"ax",%progbits
bl tos_submit_lower
.section .patch_note,"ax",%progbits
bl tos_note
.section .patch_action,"ax",%progbits
bl tos_action
.section .patch_hud_submit,"ax",%progbits
bl Hud_Submit
.section .patch_minimap,"ax",%progbits
bl tos_minimap
.section .patch_common_backdrop,"ax",%progbits
bl tos_common_backdrop
.section .patch_ocarina_native_draw,"ax",%progbits
bl Ocarina_DrawNative
.section .patch_hid_pointer,"ax",%progbits
bl tos_hid
.section .patch_touch,"ax",%progbits
bl tos_touch
.section .patch_map_markers,"ax",%progbits
bl Minimap_MaterializeMarkers
.section .patch_motion_gate_a,"ax",%progbits
nop
.section .patch_draw_a,"ax",%progbits
bl tos_draw
.section .patch_motion_gate_b,"ax",%progbits
nop
.section .patch_draw_b,"ax",%progbits
bl tos_draw
.section .patch_pause,"ax",%progbits
bl Bridge_PauseMask
.section .patch_keyboard,"ax",%progbits
bl Tos_ObserveRegister
.section .patch_mode_backdrop_dual,"ax",%progbits
bl Presentation_ModeBackdrop
.section .patch_mode_backdrop_single,"ax",%progbits
bl Presentation_ModeBackdrop
.section .patch_file_primary,"ax",%progbits
bl Tos_ObserveRegister
.section .patch_file_accent,"ax",%progbits
bl Tos_ObserveRegister
.section .patch_file_modal,"ax",%progbits
bl Tos_ObserveRegister
.section .patch_file_aux,"ax",%progbits
bl Tos_ObserveRegister
.section .patch_before,"ax",%progbits
bl tos_before
.section .patch_after,"ax",%progbits
b tos_after
.section .patch_file_fade_producer_a,"ax",%progbits
bl Presentation_FadePrimitive
.section .patch_file_fade_producer_b,"ax",%progbits
bl Presentation_FadePrimitive
.section .patch_file_fade_producer_c,"ax",%progbits
bl Presentation_FadePrimitive
.section .patch_file_fade_producer_d,"ax",%progbits
bl Presentation_FadePrimitive
.section .patch_heart_positions,"ax",%progbits
nop
.section .patch_heart_indices,"ax",%progbits
nop
.section .patch_heart_texture,"ax",%progbits
mov r0,#2
.section .patch_shard_overlay,"ax",%progbits
.float 144
.section .patch_vision_transition_a,"ax",%progbits
nop
.section .patch_vision_transition_b,"ax",%progbits
nop
.section .patch_vision_transition_c,"ax",%progbits
nop
.section .patch_target_note,"ax",%progbits
bl tos_target_note
.section .patch_heart_descriptor,"ax",%progbits
.word tosHeartPositions,tosHeartUVs,0,80,tosHeartIndices,118,2,12
.section .patch_shard_positions,"ax",%progbits
.float 12,174,0,60,174,0,12,126,0,60,126,0
