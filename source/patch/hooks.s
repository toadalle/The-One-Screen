.syntax unified
.arm
.text
.align 2
/* Mid-function seams preserve integer registers, flags and the VFP register
 * bank. Every frame is a multiple of eight bytes at C/native call boundaries. */
.macro SAVE
    push {r0-r12,lr}
    sub sp,sp,#8
    mrs r12,cpsr
    str r12,[sp]
    vmrs r12,fpscr
    str r12,[sp,#4]
    vpush {d0-d15}
.endm
.macro RESTORE
    vpop {d0-d15}
    ldr r12,[sp,#4]
    vmsr fpscr,r12
    ldr r12,[sp]
    msr cpsr_f,r12
    add sp,sp,#8
    pop {r0-r12,lr}
.endm
.global tos_before
tos_before:
    SAVE
    bl Tos_Before
    RESTORE
    mov r7,r0
    bx lr
.global tos_after
tos_after:
    SAVE
    bl Tos_After
    RESTORE
    ldr pc,=0x002E25F0
.global tos_touch
.global tos_submit_lower
tos_submit_lower:
    SAVE
    bl Presentation_EndLower
    cmp r0,#0
    ldrne r0,=0x004197E0
    strne r0,[sp,#188]
    RESTORE
    bx lr

/* Exact alpha-098 File Select backdrop hooks.  These two retail seams have
 * different calling conventions and MUST NOT share a generic C wrapper. */
.global tos_file_select_backdrop
tos_file_select_backdrop:
    push {r4,lr}
    mov r4,r0
    ldr r0,=0x00419820
    bl Presentation_SuppressBackdrop
    cmp r0,#0
    bne 1f
    mov r0,r4
    ldr ip,=0x002FFF7C
    blx ip
1:
    pop {r4,pc}

.global tos_common_backdrop
tos_common_backdrop:
    push {r4-r6,lr}
    mov r4,r0
    mov r5,r1
    ldr r0,=0x0041EE2C
    bl Presentation_SuppressBackdrop
    cmp r0,#0
    bne 2f
    mov r0,r4
    blx r5
2:
    pop {r4-r6,pc}
tos_touch:
    SAVE
    mov r0,r4
    mov r1,r5
    mov r2,r6
    bl Bridge_TouchMaterialized
    RESTORE
    ldrb r4,[r6]
    bx lr
.global tos_note
tos_note:
    SAVE
    mov r1,r9
    bl Bridge_OcarinaMask
    /* Saved r0 is at 128 bytes VFP + 8 bytes flags. */
    str r0,[sp,#136]
    RESTORE
    mov r6,#0
    bx lr
.global tos_hid
tos_hid:
    ldr r0,[r0,#4]
    SAVE
    bl Physical_BindHid
    RESTORE
    bx lr
.global tos_target_note
tos_target_note:
    SAVE
    bl Ocarina_TargetGlyph
    str r0,[sp,#136]
    RESTORE
    mov r1,r0
    bx lr
.global tos_draw
tos_draw:
    push {r4,lr}
    blx r1
    SAVE
    bl Hud_Draw
    RESTORE
    pop {r4,pc}
.global tos_action
tos_action:
    SAVE
    bl Hud_ActionBegin
    RESTORE
    push {r4,lr}
    ldr r12,=0x0042B848
    blx r12
    SAVE
    bl Hud_ActionEnd
    RESTORE
    pop {r4,pc}
.global tos_minimap
tos_minimap:
    SAVE
    bl Minimap_Project
    RESTORE
    ldr r12,=0x002FBC50
    bx r12
.global tos_movie
tos_movie:
    /* Preserve callback and object in a local frame through the native draw. */
    push {r4-r7,lr}
    sub sp,sp,#12
    str r0,[sp]
    str r1,[sp,#4]
    blx r1
    SAVE
    ldr r0,[sp,#192]
    ldr r1,[sp,#196]
    bl Presentation_Observe
    RESTORE
    add sp,sp,#12
    pop {r4-r7,pc}
